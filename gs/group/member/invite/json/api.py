# -*- coding: utf-8 -*-
import json
from zope.cachedescriptors.property import Lazy
from gs.group.base.form import GroupForm
from zope.formlib import form as formlib
from gs.group.member.invite.base.invitefields import InviteFields

# Not sure which of the following are actually required
from gs.profile.email.base.emailuser import EmailUser
from Products.GSProfile import interfaces as profileSchemas
#from processor import JSONProcessor
# TODO Rename CSVProcessor to JSONProcessor
# TODO Make JSONProcessor actually process JSON
#from columns import Columns
from profilelist import ProfileList
# TODO Determine if Columns and ProfileList should be in
# gs.group.member.invite.base
# TODO Determine if the invite API needs to use Columns and ProfileList

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

    @property
    def invite_only(self):
        return self.invite

    # TODO Determine if the invite API needs to use profileSchemaName
    # TODO Determine if profileSchemaName should be in
    # gs.group.member.invite.base
    @Lazy
    def profileSchemaName(self):
        ifName = self.globalConfiguration.getProperty('profileInterface',
                                                      'IGSCoreProfile')
        # --=mpj17=-- Sometimes profileInterface is set to ''
        ifName = (ifName and ifName) or 'IGSCoreProfile'
        retval = '%sAdminJoinCSV' % ifName
        assert hasattr(profileSchemas, ifName), \
            'Interface "%s" not found.' % ifName
        assert hasattr(profileSchemas, retval), \
            'Interface "%s" not found.' % retval
        return retval

    # TODO Determine if the invite API needs to use profileSchema
    # TODO Determine if profileSchema should be in
    # gs.group.member.invite.base
    @property
    def profileSchema(self):
        return getattr(profileSchemas, self.profileSchemaName)

    # TODO Determine if the invite API needs to use profileFields
    # TODO Determine if profileFields should be in
    # gs.group.member.invite.base
    @Lazy
    def profileFields(self):
        retval = formlib.Fields(self.profileSchema, render_context=False)
        return retval

    # TODO Determine if the invite API needs to use profileList
    # TODO Determine if profileList should be in
    # gs.group.member.invite.base
    @Lazy
    def profileList(self):
        retval = ProfileList(self.context)
        return retval

    # TODO Determine if the invite API needs to use requiredColumns
    # TODO Determine if requiredColumns should be in
    # gs.group.member.invite.base
    @Lazy
    def requiredColumns(self):
        retval = [p for p in self.profileList if p.value.required]
        return retval

    # TODO Determine if the invite API needs to use columns
    # TODO Determine if columns should be in
    # gs.group.member.invite.base
    @property
    def columns(self):
        retval = []

        profileAttributes = {}
        for pa in self.profileList:
            profileAttributes[pa.token] = pa.title

        for i in range(0, len(self.profileList)):
            j = i + 65
            columnId = 'column%c' % chr(j)
            columnTitle = u'Column %c' % chr(j)
            column = {
                'columnId': columnId,
                'columnTitle': columnTitle,
                'profileList': self.profileList}
            retval.append(column)
        assert len(retval) > 0
        return retval

    @Lazy
    def adminInfo(self):
        retval = self.loggedInUserInfo
        return retval

    @Lazy
    def fromAddr(self):
        eu = EmailUser(self.context, self.adminInfo)
        addrs = eu.get_addresses()
        retval = addrs[0] if addrs else u''
        return retval

    # TODO Determine if this should be in gs.group.member.invite.base instead
    @Lazy
    def subject(self):
        retval = u'Invitation to join {0}'.format(self.groupInfo.name)
        return retval

    # TODO Determine if this should be in gs.group.member.invite.base instead
    @Lazy
    def message(self):
        m = u'''Hi there!

Please accept this invitation to join {0}. I have set everything up for
you, so you can start participating in the group as soon as you follow
the link below and accept this invitation.'''
        retval = m.format(self.groupInfo.name)
        return retval

    # TODO Make the form return JSON results, not HTML
    @formlib.action(label=u'Submit', failure='invite_user_failure')
    def invite_user_success(self, action, data):
        # TODO Access supplied JSON
        # TODO Make this mess actually handle an API request with provided JSON
        #      Also make it less of a mess
        # Zope's regular form validation system *should* take care of checking
        # on columns and what not. So here we just have to pass data on to the
        # actual invite code and package the result up as json
        retdict = JSONProcessor.process(data)
        retval = json.dumps(retdict)
        return retval

        # Is anything beyond this comment needed?
        #form = data
        #result = {}
        #result['form'] = form

        #if 'submitted' in form:
        #    result['message'] = u''
        #    result['error'] = False
        #    # FIXME: Fix logging
        #    #m = u'process_form: Adding users to %s (%s) on %s (%s) in'\
        #    #  u' bulk for %s (%s)' % \
        #    #  (self.groupInfo.name,   self.groupInfo.id,
        #    #   self.siteInfo.get_name(),    self.siteInfo.get_id(),
        #    #   self.adminInfo.name, self.adminInfo.id)
        #    #log.info(m)

        #    # Processing the CSV is done in three stages.
        #    #   1. Process the columns.
        #    columnProcessor = Columns(self.context, form)
        #    r = columnProcessor.process()
        #    result['message'] = u'\n'.join((result['message'], r['message']))
        #    result['error'] = result['error'] \
        #        if result['error'] else r['error']
        #    columns = r['columns']
        #    processor = CSVProcessor(self.context, self.request, form, columns,
        #                             self.subject, self.message,
        #                             self.fromAddr, self.profileSchema,
        #                             self.profileFields)
        #    #   2. Parse the file.
        #    if not result['error']:
        #        r = processor.process()
        #        result['message'] = u'\n'.join((result['message'],
        #                                        r['message']))
        #        result['error'] = result['error'] or r['error']
        #        csvResults = r['csvResults']
        #    #   3. Interpret the data.
        #    if not result['error']:
        #        try:
        #            r = processor.process_csv_results(csvResults,
        #                                              form['delivery'])
        #        except UnicodeDecodeError, ude:
        #            result['error'] = True
        #            m = u'<p>Error reading the CSV file (did you select the '\
        #                u'correct file?): <span class="muted">{0}</p></p>'
        #            result['message'] = m.format(ude)
        #        else:
        #            m = u'\n'.join((result['message'], r['message']))
        #            result['message'] = m
        #            result['error'] = result['error'] or r['error']

        #    assert 'error' in result
        #    assert type(result['error']) == bool
        #    assert 'message' in result
        #    assert type(result['message']) == unicode

        #assert type(result) == dict
        #assert 'form' in result
        #assert type(result['form']) == dict

    def invite_user_failure(self, action, data, errors):
        # Humm... what does errors give us? There *should* be ValidationErrors
        # which contain messages we can send back to the user.
        #
        # Would we want to get fansier and return multiple status/message pairs
        # for multiple errors? If so, we'd have to create status values for
        # each type of validation error.
        retdict = {
            'status': VALIDATION_ERROR,
            'message': [unicode(error) for error in errors]
        }
        retval = json.dumps(retdict)
        return retval

    def __call__(self):
        retval = super(InviteUserAPI, self).__call__()
        self.request.response.setHeader('Content-Type', 'application/json')
        return retval
