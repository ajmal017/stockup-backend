import urlparse


def construct_sina_url(values):
    scheme = "http"
    netloc = "111.161.68.235"
    path = "/"
    params = ""
    query = "list=" + ",".join(str(s) for s in values)
    frags = ""
    return urlparse.urlunparse((scheme, netloc, path, params, query, frags))