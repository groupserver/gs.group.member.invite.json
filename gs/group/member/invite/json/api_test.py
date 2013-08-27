# -*- coding: utf-8 -*-
import json
from zope.cachedescriptors.property import Lazy
from zope.formlib import form as formlib
from gs.group.member.invite.base.invitefields import InviteFields
from group_api_json_form import GroupApiJsonForm

import logging
log = logging.getLogger('gs.group.member.invite.json')

PROFILE_CREATED = 0
EXISTING_PROFILE_INVITED = 1
EXISTING_MEMBER_IGNORED = 2


class InviteUserAPI(GroupApiJsonForm):
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

    @formlib.action(label=u'Submit', prefix='', failure='invite_user_failure')
    def invite_user_success(self, action, data):
        # TODO Make this mess actually handle an API request with provided JSON
        #      Also make it less of a mess
        # Zope's regular form validation system *should* take care of checking
        # on columns and what not. So here we just have to pass data on to the
        # actual invite code and package the result up as json
        retval = json.dumps(data, indent=4)
        return retval

    def invite_user_failure(self, action, data, errors):
        return self.build_error_response(action, data, errors)
