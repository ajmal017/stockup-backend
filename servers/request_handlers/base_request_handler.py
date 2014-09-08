from tornado.web import RequestHandler


class BaseRequestHandler(RequestHandler):

    def initialize(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-cache, must-revalidate")

    @property
    def db(self):
        return self.settings["stock_db"]

    @property
    def datetime_repr(self):
        return '%Y-%m-%dT%H:%M:%SZ'
