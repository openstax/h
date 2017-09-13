# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from zope.interface import implementer

from h import models
from h.formatters.user_info import UserInfoFormatter
from h.formatters.interfaces import IAnnotationFormatter


@implementer(IAnnotationFormatter)
class AnnotationUserInfoFormatter(object):
    def __init__(self, session, user_svc):
        self.session = session
        self.user_svc = user_svc
        self.user_formatter = UserInfoFormatter()

    def preload(self, ids):
        if not ids:
            return

        userids = {t[0] for t in self.session.query(models.Annotation.userid).filter(models.Annotation.id.in_(ids))}
        self.user_svc.fetch_all(userids)

    def format(self, annotation_resource):
        user = self.user_svc.fetch(annotation_resource.annotation.userid)
        return self.user_formatter.format(user)
