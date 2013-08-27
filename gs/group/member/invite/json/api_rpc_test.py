# -*- coding: utf-8 -*-
import json
from z3c.jsonrpc import publisher
from zope.cachedescriptors.property import Lazy
from zope.formlib import form as formlib
from gs.group.member.invite.base.invitefields import InviteFields
from gs.group.member.invite.base.audit import INVITE_NEW_USER, \
    INVITE_OLD_USER, INVITE_EXISTING_MEMBER
from processor import InviteProcessor
from group_api_json_form import GroupApiJsonForm

import logging
log = logging.getLogger('gs.group.member.invite.json')

import pprint

PROFILE_CREATED = 0
EXISTING_PROFILE_INVITED = 1
EXISTING_MEMBER_IGNORED = 2


class InviteUserAPI(publisher.MethodPublisher):
    label = u'POST data to this URL to invite a member to join this '\
        + 'group.'

    def __init__(self, group, request):
        super(InviteUserAPI, self).__init__(group, request)
        self.inviteFields = InviteFields(group)

    @Lazy
    def globalConfiguration(self):
        retval = self.inviteFields.config
        return retval

    @Lazy
    def interface(self):
        retval = self.inviteFields.adminInterface
        assert retval
        return retval

    @Lazy
    def form_fields(self):
        retval = formlib.Fields(self.interface, render_context=False)
        assert retval
        return retval

    def gs_group_member_invite_json_invite(self):
        # TODO Make this mess actually handle an API request with provided JSON
        #      Also make it less of a mess
        # Zope's regular form validation system *should* take care of checking
        # on columns and what not. So here we just have to pass data on to the
        # actual invite code and package the result up as json
        logging.info(pprint.pformat(self.request.form, indent=2))
        # TODO Call some validation method
        #inviteProcessor = InviteProcessor(self.context, self.groupInfo,
        #                                  self.form_fields, self.inviteFields)
        #result, userInfo = inviteProcessor.process(data)
        #retval = {}
        # TODO Include a URL to the user and group in results
        if result == INVITE_NEW_USER:
            retval['status'] = 1
            m = u'A profile for {0} has been created, and given the '\
                u'email address {1}.\n'\
                u'{0} has been sent an invitation to join {2}.'
            retval['message'] = m.format(data['email'], 
                                         userInfo.getProperty('fn',''), 
                                         self.groupInfo.title)
        elif result == INVITE_OLD_USER:
            retval['status'] = 2
            m = u'Inviting the existing person with the email address '\
                    u'{0} - {1} - to join {2}.</li>'
            retval['message'] = m.format(data['email'], 
                                         userInfo.getProperty('fn',''),
                                         self.groupInfo.title)
        elif result == INVITE_EXISTING_MEMBER:
            retval['status'] = 3
            m = u'The person with the email address {0} - {1} -'\
                u' is already a member of {2}.\n'\
                u'No changes to the profile of {1} have been made.'
            retval['message'] = m.format(data['email'], 
                                         userInfo.getProperty('fn',''), 
                                         self.groupInfo.title)
        else:
            # What the hell happened?
            retval['status'] = 100
            retval['message'] = self.request.form
            # TODO Write a more meaningful message

        retval = json.dumps(retval, indent=4)
        return retval

    def invite_user_failure(self, action, data, errors):
        return self.build_error_response(action, data, errors)
