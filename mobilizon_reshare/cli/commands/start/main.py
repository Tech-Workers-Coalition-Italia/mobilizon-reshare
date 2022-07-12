from mobilizon_reshare.cli.commands import print_reports
from mobilizon_reshare.config.command import CommandConfig
from mobilizon_reshare.main.start import start


async def start_command(command_config: CommandConfig):
    """
    STUB
    :return:
    """
    reports = await start(command_config)
    if command_config.dry_run and reports:
        print_reports(reports)
    return 0 if reports and reports.successful else 1
