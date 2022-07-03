import click

from mobilizon_reshare.publishers.coordinator import PublisherCoordinatorReport


def print_reports(reports: PublisherCoordinatorReport) -> None:
    for report in reports.reports:
        click.echo(report.published_content)
