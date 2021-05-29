from typing import Iterable

from .abstract import AbstractPublisher
from .exceptions import PublisherError


def run(publishers: Iterable[AbstractPublisher]) -> dict:
    invalid_credentials, invalid_event = [], []
    for p in publishers:
        if not p.are_credentials_valid():
            invalid_credentials.append(p)
        if not p.is_event_valid():
            invalid_event.append(p)
    if invalid_credentials or invalid_event:
        # TODO: consider to use exceptions or data class if necessary
        return {
            "status": "fail",
            "description": "Validation failed for at least 1 publisher",
            "invalid_credentials": invalid_credentials,
            "invalid_event": invalid_event,
        }

    failed_publishers, successful_publishers = [], []
    for p in publishers:
        try:
            p.post()
        except PublisherError:
            failed_publishers.append(p)
        else:
            successful_publishers.append(p)

    if failed_publishers:
        return {
            "status": "fail",
            "description": "Posting failed for at least 1 publisher",
            "failed_publishers": failed_publishers,
            "successful_publishers": successful_publishers,
        }
    return {
        "status": "success",
        "description": "https://www.youtube.com/watch?v=2lHgmC6PBBE",
    }
