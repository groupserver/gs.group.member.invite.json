# -*- coding: utf-8 -*-
import json
from zope.cachedescriptors.property import Lazy
from gs.group.base.form import GroupForm
from gs.group.base.page import GroupPage
from zope.formlib import form as formlib
from gs.group.member.invite.base.invitefields import InviteFields
from interfaces import IApiTest

import pprint
import logging
log = logging.getLogger('gs.group.member.invite.json')

PROFILE_CREATED = 0
EXISTING_PROFILE_INVITED = 1
EXISTING_MEMBER_IGNORED = 2
VALIDATION_ERROR = 100


class InviteUserAPI(GroupForm):
    # if this is set to true, we invite users. Otherwise we just add them.
    invite = True

    def __init__(self, group, request):
        super(InviteUserAPI, self).__init__(group, request)
        self.prefix = ''
        self.inviteFields = InviteFields(group)

    @Lazy
    def globalConfiguration(self):
        retval = self.inviteFields.config
        return retval

#    @Lazy
#    def form_fields(self):
#        retval = formlib.Fields(IApiTest, render_context=False)
#        assert retval
#        return retval
    @Lazy
    def form_fields(self):
        retval = formlib.Fields(self.inviteFields.adminInterface,
                                render_context=False)
        assert retval
        return retval

    # TODO Make the form return JSON results, not HTML
    @formlib.action(label=u'Submit', prefix='', name='fn', 
                    failure='invite_user_failure')
    def invite_user_success(self, action, data):
        # TODO Access supplied JSON
        # TODO Make this mess actually handle an API request with provided JSON
        #      Also make it less of a mess
        # Zope's regular form validation system *should* take care of checking
        # on columns and what not. So here we just have to pass data on to the
        # actual invite code and package the result up as json
        log.info('Success')
        log.info(pprint.pformat(data, indent=3))
        # retdict = JSONProcessor.process(data)
        retval = json.dumps(data)
        contentType = 'applicaton/json'
        self.request.response.setHeader('Content-Type', contentType)
        return retval

    def invite_user_failure(self, action, data, errors):
        # Humm... what does errors give us? There *should* be ValidationErrors
        # which contain messages we can send back to the user.
        #
        # Would we want to get fansier and return multiple status/message pairs
        # for multiple errors? If so, we'd have to create status values for
        # each type of validation error.
        log.info('Failure')
        log.info(pprint.pformat(data, indent=3))
        log.info(pprint.pformat(errors, indent=3))
        retdict = {
            'status': VALIDATION_ERROR,
            'message': [unicode(error) for error in errors]
        }
        retval = json.dumps(retdict)
        contentType = 'application/json'
        self.request.response.setHeader('Content-Type', contentType)
        return retval

#    def __call__(self, ignore_request=False):
#        log.info('Called!')
#        log.info(pprint.pformat(self.request.__dict__, indent=3))
#        contentType = 'application/json'
#        self.request.response.setHeader('Content-Type', contentType)
#        return 'Hello'
