# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 E-Democracy.org and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import json
from email.utils import parseaddr
from zope.cachedescriptors.property import Lazy
from zope.formlib import form as formlib
from gs.content.form.api.json import GroupEndpoint
from gs.group.member.invite.base.invitefields import InviteFields
from gs.group.member.invite.base.audit import INVITE_NEW_USER, \
    INVITE_OLD_USER, INVITE_EXISTING_MEMBER
from gs.group.member.invite.base.processor import InviteProcessor
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.CustomUserFolder.userinfo import userInfo_to_anchor

PROFILE_CREATED = 0
EXISTING_PROFILE_INVITED = 1
EXISTING_MEMBER_IGNORED = 2


class InviteUserAPI(GroupEndpoint):
    label = u'POST data to this URL to invite a member to join this '\
            u'group.'

    def __init__(self, group, request):
        super(InviteUserAPI, self).__init__(group, request)
        self.inviteFields = InviteFields(group)

    @Lazy
    def globalConfiguration(self):
        retval = self.inviteFields.config
        return retval

    @Lazy
    def form_fields(self):
        retval = formlib.Fields(self.inviteFields.adminInterface,
                                render_context=False)
        assert retval
        return retval

    @formlib.action(label=u'Submit', prefix='', failure='invite_user_failure')
    def invite_user_success(self, action, data):
        # Zope's regular form validation system *should* take care of checking
        # on columns and what not. So here we just have to pass data on to the
        # actual invite code and package the result up as json
        inviteProcessor = InviteProcessor(self.context, self.request,
                                          self.siteInfo, self.groupInfo,
                                          self.loggedInUser, self.form_fields,
                                          self.inviteFields)
        result, userInfo = inviteProcessor.process(data)

        # Prep data for display
        addrName, addr = parseaddr(data['toAddr'].strip())
        linked_username = userInfo_to_anchor(userInfo)
        linked_groupname = groupInfo_to_anchor(self.groupInfo)
        retval = {}

        if result == INVITE_NEW_USER:
            retval['status'] = 1
            m = []
            m.append(u'A profile for {0} has been created, and given the '
                     u'email address {1}.')
            m.append(u'{0} has been sent an invitation to join {2}.')
            m = [i.format(linked_username, addr, linked_groupname) for i in m]
            retval['message'] = m
        elif result == INVITE_OLD_USER:
            retval['status'] = 2
            m = []
            m.append(u'Inviting the existing person with the email address '
                     u'{0} - {1} - to join {2}.')
            m = [i.format(addr, linked_username, linked_groupname) for i in m]
            retval['message'] = m
        elif result == INVITE_EXISTING_MEMBER:
            retval['status'] = 3
            m = []
            m.append(u'The person with the email address {0} - {1} -'
                     u' is already a member of {2}.')
            m.append(u'No changes to the profile of {1} have been made.')
            m = [i.format(addr, linked_username, linked_groupname) for i in m]
            retval['message'] = m
        else:
            retval['status'] = 100
            retval['message'] = u'An unknown event occurred.'

        retval = json.dumps(retval, indent=4)
        return retval

    def invite_user_failure(self, action, data, errors):
        return self.build_error_response(action, data, errors)
