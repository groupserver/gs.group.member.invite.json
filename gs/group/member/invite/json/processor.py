# -*- coding: utf-8 -*-
from email.utils import parseaddr
from zope.formlib import form
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from Products.GSProfile.utils import create_user_from_email
from gs.content.form.utils import enforce_schema
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    EmailAddressExists
from gs.group.member.base import user_member_of_group
from gs.group.member.invite.base.audit import Auditor, INVITE_NEW_USER, \
    INVITE_OLD_USER, INVITE_EXISTING_MEMBER
from gs.group.member.invite.base.inviter import Inviter
from gs.group.member.invite.base.utils import set_digest


class InviteProcessor(object):
    """
        Class that does the technical work of inviting a user based on data
        provided by another user.
    """

    def __init__(self, context, request, siteInfo, groupInfo, invitingUserInfo, 
                 form_fields, inviteFields):
        """
            Input: context - Zope context object. Should be a Group context.
                   request - Zope request that is causing this invitation.
                   siteInfo - SiteInfo object for the Site that a user is
                              joining a group in.
                   groupInfo - GroupInfo object for the Group that a user is
                               being invited to.
                   invitingUserInfo - UserInfo object representing the user who
                                      is doing the inviting
                   form_fields - zope.formlib.Fields used by the *Form that is
                                 creating an instance of InviteProcessor
                   inviteFields - InviteFields object that governs what data is
                                  required to process the invite.
        """
        self.context = context
        self.request = request
        self.siteInfo = siteInfo
        self.groupInfo = groupInfo
        self.invitingUserInfo = invitingUserInfo
        self.form_fields = form_fields
        self.inviteFields = inviteFields

    def process(self, data):
        """
            Attempt to invite a user to join a group based on the provided
            data.

            Input: data - A dict of data submitted to a *Form, assumed to be
                          data used to invite a person to a group
            Output: If successful, a tuple - (status_code, userInfo) -
                    containing a status code indicating the result of
                    processing the invite and an IGSUserInfo instance
        """
        userInfo = None

        acl_users = self.context.acl_users
        toAddr = data['toAddr'].strip()
        addrName, addr = parseaddr(toAddr)

        emailChecker = NewEmailAddress(title=u'Email')
        emailChecker.context = self.context

        try:
            emailChecker.validate(toAddr)  # Can handle a full address
        except EmailAddressExists:
            user = acl_users.get_userByEmail(addr)  # Cannot
            assert user, 'User for address <%s> not found' % addr
            userInfo = IGSUserInfo(user)
            auditor, inviter = self.get_auditor_inviter(userInfo)
            if user_member_of_group(user, self.groupInfo):
                auditor.info(INVITE_EXISTING_MEMBER, addr)
                status_code = INVITE_EXISTING_MEMBER
            else:
                inviteId = inviter.create_invitation(data, False)
                auditor.info(INVITE_OLD_USER, addr)
                inviter.send_notification(data['subject'],
                                          data['message'],
                                          inviteId,
                                          data['fromAddr'])  # No to-addr
                self.set_delivery(userInfo, data['delivery'])
                status_code = INVITE_OLD_USER
        else:
            # Email address does not exist, but it is a legitimate address
            user = create_user_from_email(self.context, toAddr)
            userInfo = IGSUserInfo(user)
            self.add_profile_attributes(userInfo, data)
            auditor, inviter = self.get_auditor_inviter(userInfo)
            inviteId = inviter.create_invitation(data, True)
            auditor.info(INVITE_NEW_USER, addr)
            inviter.send_notification(data['subject'], data['message'],
                                      inviteId, data['fromAddr'],
                                      addr)  # Note the to-addr
            self.set_delivery(userInfo, data['delivery'])
            status_code = INVITE_NEW_USER

        assert status_code
        assert user, 'User not created or found'
        return (status_code, userInfo)

    def add_profile_attributes(self, userInfo, data):
        enforce_schema(userInfo.user, self.inviteFields.profileInterface)
        fields = self.form_fields.select(*self.inviteFields.profileFieldIds)
        for field in fields:
            field.interface = self.inviteFields.profileInterface

        form.applyChanges(userInfo.user, fields, data)
        # wpb: Why not use self.set_delivery?
        set_digest(userInfo, self.groupInfo, data)

    def get_auditor_inviter(self, userInfo):
        """
            Retrives the Inviter and Auditor objects that will be used to
            invite the user.

            Input: userInfo - A UserInfo instance of the user who will be
                              invited.
            Output: A tuple - (Auditor, Inviter)
        """
        ctx = get_the_actual_instance_from_zope(self.context)
        inviter = Inviter(ctx, self.request, userInfo, self.invitingUserInfo,
                          self.siteInfo, self.groupInfo)
        auditor = Auditor(self.siteInfo, self.groupInfo,
                          self.invitingUserInfo, userInfo)
        return (auditor, inviter)

    def set_delivery(self, userInfo, delivery):
        """
            Convenience method for setting the delivery method of a user in a
            group.

            Input: userInfo - A UserInfo instance of the user to set delivery
                              for.
                   delivery - A string indicating the desired delivery setting.
                              Allowed values are 'email', 'digest', and 'web'.
        """
        if delivery == 'email':
            # --=mpj17=-- The default is one email per post
            pass
        elif delivery == 'digest':
            userInfo.user.set_enableDigestByKey(self.groupInfo.id)
        elif delivery == 'web':
            userInfo.user.set_disableDeliveryByKey(self.groupInfo.id)
