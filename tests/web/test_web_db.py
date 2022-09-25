import logging

import pytest
import urllib3.util

from mobilizon_reshare.web.backend import main
from mobilizon_reshare.web.backend.main import check_database, init_app


def test_check_database_sqlite(caplog):
    with caplog.at_level(logging.WARNING):
        check_database()
        assert caplog.messages == [
            "Database is SQLite. This might create issues when running the web application. "
            "Please use a PostgreSQL or MariaDB backend."
        ]


@pytest.mark.asyncio
async def test_check_database_cli(caplog):
    with caplog.at_level(logging.WARNING):
        await init_app()
        assert caplog.messages == [
            "Database is SQLite. This might create issues when running the web application. "
            "Please use a PostgreSQL or MariaDB backend."
        ]


@pytest.mark.asyncio
async def test_check_database_postgres(caplog, monkeypatch):
    def get_url():
        return urllib3.util.parse_url("postgres://someone@something.it")

    monkeypatch.setattr(main, "get_db_url", get_url)
    with caplog.at_level(logging.WARNING):
        check_database()
        assert caplog.messages == []
