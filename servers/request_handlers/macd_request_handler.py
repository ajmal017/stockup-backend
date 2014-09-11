from base_request_handler import BaseRequestHandler


class MacdRequestHandler(BaseRequestHandler):

    def initialize(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-cache, must-revalidate")

    def get(self):
        self.write({'macd':'handler'})
