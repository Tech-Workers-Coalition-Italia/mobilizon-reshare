from typing import List

from fastapi_pagination import paginate
from tortoise import Model


async def transform_and_paginate(model, model_list: List[Model]):
    return paginate(
        [await model.to_pydantic().from_tortoise_orm(x) for x in model_list]
    )
