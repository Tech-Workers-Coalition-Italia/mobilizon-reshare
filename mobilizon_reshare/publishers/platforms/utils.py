def fqdn_to_uri(fqdn: str):
    if not fqdn.startswith("http"):
        return "https://" + fqdn
    else:
        return fqdn


def uri_join(uri: str, path: str):
    ends = uri.endswith("/")
    starts = path.startswith("/")
    if ends and starts:
        return uri + path[1:]
    elif ends or starts:
        return uri + path
    else:
        return uri + "/" + path
