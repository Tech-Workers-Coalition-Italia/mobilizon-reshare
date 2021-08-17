from uuid import UUID

import pytest

from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.coordinator import (
    PublisherCoordinatorReport,
    PublicationReport,
)


@pytest.mark.parametrize(
    "statuses, successful",
    [
        [[PublicationStatus.COMPLETED, PublicationStatus.COMPLETED], True],
        [[PublicationStatus.WAITING, PublicationStatus.COMPLETED], False],
        [[PublicationStatus.COMPLETED, PublicationStatus.FAILED], False],
        [[], True],
        [[PublicationStatus.COMPLETED], True],
    ],
)
def test_publication_report_successful(statuses, successful):
    reports = {}
    for i, status in enumerate(statuses):
        reports[UUID(int=i)] = PublicationReport(
            reason=None, publication_id=None, status=status
        )
    assert PublisherCoordinatorReport(None, reports).successful == successful
