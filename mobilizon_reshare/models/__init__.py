from tortoise.contrib.pydantic import pydantic_model_creator


class WithPydantic:
    @classmethod
    def to_pydantic(cls):
        return pydantic_model_creator(cls)
