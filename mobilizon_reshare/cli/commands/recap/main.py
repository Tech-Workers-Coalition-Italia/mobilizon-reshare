import logging.config

from mobilizon_reshare.main.recap import recap

logger = logging.getLogger(__name__)


async def main():

    reports = await recap()
    return 0 if reports and reports.successful else 1
