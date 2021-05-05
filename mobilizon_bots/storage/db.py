from pathlib import Path

from tortoise import Tortoise


class MobotsDB:
    def __init__(self, path: Path):
        self.path = path

    async def setup(self):
        await Tortoise.init(
            db_url=f"sqlite:///{self.path}",
            modules={"models": ["mobilizon_bots.event.model"]},
        )
        if not self.is_init():
            # Generate the schema
            await Tortoise.generate_schemas()

    def is_init(self) -> bool:
        # TODO: Check if DB is openable/"queriable"
        return self.path.exists() and (not self.path.is_dir())

    @staticmethod
    async def tear_down():
        await Tortoise.close_connections()
