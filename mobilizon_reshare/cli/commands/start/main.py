from config.command import CommandConfig
from mobilizon_reshare.main.start import start


async def start_command(command_config: CommandConfig):
    """
    STUB
    :return:
    """
    reports = await start(command_config)
    return 0 if reports and reports.successful else 1
