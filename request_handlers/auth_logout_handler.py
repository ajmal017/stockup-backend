from request_handlers.base_request_handler import BaseRequestHandler


class AuthLogoutHandler(BaseRequestHandler):

    def get(self):
        self.clear_cookie("user")
        self.write({"logged out": True})