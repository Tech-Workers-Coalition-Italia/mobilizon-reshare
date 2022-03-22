from mobilizon_reshare.main.publish import publish


async def publish_command():
    """
    STUB
    :return:
    """
    reports = await publish()
    return 0 if reports and reports.successful else 1
