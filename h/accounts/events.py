# -*- coding: utf-8 -*-
class ActivationEvent(object):
    def __init__(self, request, user):
        self.request = request
        self.user = user


class LoginEvent(object):
    def __init__(self, request, user):
        self.request = request
        self.user = user


class LogoutEvent(object):
    def __init__(self, request):
        self.request = request


class PasswordResetEvent(object):
    def __init__(self, request, user):
        self.request = request
        self.user = user
