from mobilizon_reshare.main.retry import retry_publication, retry_event


async def retry_event_command(event_id):
    reports = await retry_event(event_id)
    return 0 if reports and reports.successful else 1


async def retry_publication_command(publication_id):
    reports = await retry_publication(publication_id)
    return 0 if reports and reports.successful else 1
