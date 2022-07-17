from mobilizon_reshare.publishers.coordinators.recap_publishing.recap import (
    RecapCoordinator,
)


class DryRunRecapCoordinator(RecapCoordinator):
    def _send(self, content, recap_publication):
        pass
