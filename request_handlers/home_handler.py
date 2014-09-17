from request_handlers.base_request_handler import BaseRequestHandler


class HomeHandler(BaseRequestHandler):
    def get(self):
        self.write({"hello": {"world": True}})
