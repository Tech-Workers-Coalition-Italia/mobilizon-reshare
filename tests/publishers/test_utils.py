import pytest

from mobilizon_reshare.publishers.platforms.utils import fqdn_to_uri, uri_join


@pytest.mark.parametrize(
    "fqdn,expected_result",
    [
        ["mastodon.bida.im", "https://mastodon.bida.im"],
        ["puntarella.party/", "https://puntarella.party/"],
        ["http://nebbia.fail", "http://nebbia.fail"],
        ["https://mastodon.cisti.org/", "https://mastodon.cisti.org/"],
    ],
)
def test_fqdn_to_uri(fqdn, expected_result):
    assert fqdn_to_uri(fqdn) == expected_result


@pytest.mark.parametrize(
    "uri,path,expected_result",
    [
        ["https://mastodon.bida.im", "statuses", "https://mastodon.bida.im/statuses"],
        ["https://puntarella.party/", "/statuses", "https://puntarella.party/statuses"],
        ["http://nebbia.fail", "/statuses", "http://nebbia.fail/statuses"],
        [
            "https://mastodon.cisti.org/",
            "statuses",
            "https://mastodon.cisti.org/statuses",
        ],
    ],
)
def test_uri_join(uri, path, expected_result):
    assert uri_join(uri, path) == expected_result
