class EventNotFound(Exception):
    """Event is not present in the database"""


class DuplicateEvent(ValueError):
    """A duplicate mobilizon_id has been found in the database"""
