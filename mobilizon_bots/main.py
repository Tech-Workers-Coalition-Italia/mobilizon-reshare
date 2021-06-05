from mobilizon_bots.mobilizon.events import get_unpublished_events
from mobilizon_bots.storage.db import MobilizonBotsDB


def main():
    """
    STUB
    :return:
    """
    db = MobilizonBotsDB().setup()
    published_events = db.get_published_events()
    unpublished_events = get_unpublished_events(published_events)
    event = select_event_to_publish()
    report = PublisherCoordinator(event).publish() if event else exit(0)
    report.write_to_db()
    notify_report(report)
    exit(0 if report.is_success() else 1)
