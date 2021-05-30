import pytest

from mobilizon_bots.models.publisher import Publisher


@pytest.mark.asyncio
async def test_publisher_create(publisher_model_generator):
    publisher_model = publisher_model_generator()
    await publisher_model.save()
    publisher_db = await Publisher.filter(type="publisher_1").first()
    assert publisher_db.account_ref == "account_ref_1"
