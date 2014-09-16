import urlparse


def construct_sina_url(values):
    scheme = "http"
    netloc = "hq.sinajs.cn:80"
    path = "/"
    params = ""
    query = "list=" + ",".join(str(s) for s in values)
    frags = ""
    return urlparse.urlunparse((scheme, netloc, path, params, query, frags))