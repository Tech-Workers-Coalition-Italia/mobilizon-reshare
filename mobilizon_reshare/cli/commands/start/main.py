from mobilizon_reshare.main.start import start


async def start_command():
    """
    STUB
    :return:
    """
    reports = await start()
    return 0 if reports and reports.successful else 1
