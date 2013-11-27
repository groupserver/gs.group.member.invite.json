==============================
``gs.group.member.invite.json``
==============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Via JSON, send an invitation to join a group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Bill Bushey`_
:Contact: Bill Bushey <bill.bushey@e-democracy.org>
:Date: 2013-08-20
:Organization: `E-Democracy.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 3.0`_
  by `E-Democracy.org`_.

Introduction
===========

This product provides an `API`_ by which software can issue invitations to
individuals to join a group. 

The impetus for creating this product is to
provide an end point for the JavaScript based bulk invite process of
`gs.group.member.invite.csv`_. However, this product is independant of
gs.group.member.invite.csv; any code which can submit a properly formatted
request should be able to use this end point to issue invitations.

Usage
=====

To see a list of available parameters, including which parameters are required,
make a simple request to <group_url>/gs-group-member-invite-json.html.

To make an invitation, make a request to 
<group_url>/gs-group-member-invite-json.html that supplies all required data
via the application/x-www-form-urlencoded content-type. This request must 
include the parameter 'submit' to indicate the request is to be processed. This
request must also pass a cookie with the parameter __ac and a value that
corresponds to an authenticated session.

fromAddr
--------

The documentation provided by <group_url>/gs-group-member-invite-json.html
indicates that fromAddr is required, but does not indicate that only certain
values are accepted. fromAddr must be an email address associated with the
authenticated session the submitted cookie corresponds to.

CURL Example
------------

Assuming an instance of GroupServer is running at 'gsbox', the following
example will attempt to invite a user to the Example Group::

    curl -H "Accept: application/json" -b "__ac=<VALUE_FROM_BROWSER>" 
    -X POST -d "toAddr=teddy%40bullmouse.com&fn=Teddy%20Roosevelt&delivery=email&message=Hi&fromAddr=<YOUR_EMAIL_ADDRESS>&subject=Welcome&submit" 
    http://gsbox/groups/example_group/gs-group-member-invite-json.html

In Firefox, if you are logged into your GroupServer instance, you can find the value for __ac at chrome://browser/content/preferences/cookies.xul.

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.group.member.invite.json
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _E-Democracy.org: http://e-democracy.org/
.. _Bill Bushey: http://groupserver.org/p/wbushey
.. _Creative Commons Attribution-Share Alike 3.0:
   http://creativecommons.org/licenses/by-sa/3.0/
.. _API: http://en.wikipedia.org/wiki/Application_programming_interface
.. _gs.group.member.invite.csv:
   https://source.iopen.net/groupserver/gs.group.member.invite.csv
