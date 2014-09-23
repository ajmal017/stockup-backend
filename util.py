import urlparse


def construct_sina_url(values):
    scheme = "http"
    netloc = "111.161.68.235"
    path = "/"
    params = ""
    query = "list=" + ",".join(str(s) for s in values)
    frags = ""
    return urlparse.urlunparse((scheme, netloc, path, params, query, frags))


def shift(a, v, l):
    """
    shift the window "a" over a stream of values by one,
    where v is the next value in the stream
    :param a: the windows
    :param v: the next value in the stream
    :param l: the length of the window
    """
    a.append(v)
    if len(a) > l:
        a.popleft()


def avg(a):
    return float(sum(a)) / len(a)