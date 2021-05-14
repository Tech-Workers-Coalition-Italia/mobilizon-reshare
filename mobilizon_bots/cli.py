import logging.config
import sys
from argparse import ArgumentParser

from mobilizon_bots.config.config import settings

logger = logging.getLogger(__name__)


def command_line():
    parser = ArgumentParser()

    return parser.parse_args()


def run():
    logging.config.dictConfig(settings.logging)
    logger.debug("Test message debug")
    logger.info("Test message info")
    logger.error("Test message error")
    sys.exit(0)


if __name__ == "__main__":
    run()
