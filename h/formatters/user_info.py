# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from zope.interface import implementer

from h.formatters.interfaces import IUserFormatter


@implementer(IUserFormatter)
class UserInfoFormatter(object):
    def format(self, user):
        if user is None:
            return {}

        return {
            'user_info': {
                'display_name': user.display_name,
            }
        }
