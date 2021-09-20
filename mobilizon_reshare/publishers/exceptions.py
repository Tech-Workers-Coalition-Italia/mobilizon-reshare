class PublisherError(Exception):
    """ Generic publisher error """

    def __init__(self, message):
        """ :param str message: exception message """
        super().__init__(message)


class InvalidAttribute(PublisherError):
    """ Publisher defined with invalid or missing attribute """


class InvalidBot(PublisherError):
    """ Publisher refers to the wrong service bot """


class InvalidCredentials(PublisherError):
    """ Publisher cannot validate credentials """


class InvalidEvent(PublisherError):
    """ Publisher cannot validate events """


class InvalidMessage(PublisherError):
    """ Publisher cannot validate message """


class InvalidResponse(PublisherError):
    """ Publisher receives an invalid response from its service """


class InvalidSettings(PublisherError):
    """ Publisher settings are either missing or badly configured """


class ZulipError(PublisherError):
    """ Publisher receives an error response from Zulip"""
