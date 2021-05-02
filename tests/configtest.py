import pytest
from dynaconf import settings
from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    initializer(
        ["tests.test_models"],
        db_url=f"sqlite:///{settings.DB_PATH}",
        app_label="models",
    )
    request.addfinalizer(finalizer)
