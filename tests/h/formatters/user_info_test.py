# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from h.formatters.user_info import UserInfoFormatter


class TestAnnotationUserInfoFormatter(object):
    def test_format_returns_user_info_object(self, factories, formatter):
        user = factories.User.build(display_name='Jane Doe')

        result = formatter.format(user)
        assert result == {'user_info': {'display_name': 'Jane Doe'}}

    def test_format_allows_null_display_name(self, factories, formatter):
        user = factories.User.build(display_name=None)

        result = formatter.format(user)
        assert result == {'user_info': {'display_name': None}}

    def test_format_returns_empty_dict_when_user_missing(self, formatter):
        assert formatter.format(None) == {}

    @pytest.fixture
    def formatter(self):
        return UserInfoFormatter()
