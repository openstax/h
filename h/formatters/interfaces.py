# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from zope.interface import Interface


class IAnnotationFormatter(Interface):
    """
    Interface for annotation formatters.

    Annotation formatters are ways to add data to the annotation JSON payload
    without putting everything in the annotation presenter, thus allowing better
    decoupling of code.

    The main method is ``format(annotation_resource)`` which is expected to
    return a dictionary representation based on the passed-in annotation. If
    the formatter depends on other data it should be able to load it on-demand
    for the given annotation.

    Since we are rendering lists of potentially hundreds of annotations in one
    request, formatters need to be able to optimize the fetching of additional
    data (e.g. from the database). Which is why this interface defines the
    ``preload(ids)`` method.
    Each formatter implementation is expected to handle a cache internally which
    is being preloaded with said method.
    """

    def preload(ids):  # noqa: N805
        """
        Batch load data based on annotation ids.

        :param ids: List of annotation ids based on which data should be preloaded.
        :type ids: list of unicode
        """

    def format(annotation_resource):  # noqa: N805
        """
        Presents additional annotation data that will be served to API clients.

        :param annotation_resource: The annotation that needs presenting.
        :type annotation_resource: h.resources.AnnotationResource

        :returns: A formatted dictionary.
        :rtype: dict
        """


class IUserFormatter(Interface):
    """
    Interface for user formatters.

    User formatters are ways to compose a user JSON representation out of
    different formatters.

    The main method is ``format(user)`` which is expected to return a
    dictionary representation based on the passed-in user. If the formatter
    depends on other data it should be able to load it on-demand for the
    give user.

    Currently there is no need to format a list of potentially hundreds of
    users in one request, if we have a need for this we should provide a
    way for formatters to optimize database access.
    """

    def format(user):  # noqa: N805
        """
        Presents data for a JSON user representation.

        :param user: The user that needs presenting.
        :type user: h.models.User

        :returns: A formatted dictionary.
        :rtype: dict
        """
