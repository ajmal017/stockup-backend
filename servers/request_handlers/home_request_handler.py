from base_request_handler import BaseRequestHandler


class HomeRequestHandler(BaseRequestHandler):

    def initialize(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-cache, must-revalidate")

    def get(self):
        self.write({"hello":{"world":True}})