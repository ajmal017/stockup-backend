from tornado.web import MissingArgumentError

from request_handlers.base_request_handler import BaseRequestHandler


class AuthLoginHandler(BaseRequestHandler):
    def get(self):
        try:
            error_message = self.get_argument("error")
        except MissingArgumentError:
            error_message = ""
        if error_message:
            self.write({"error": error_message})
        else:
            self.write({"login": "handler"})

    def check_permission(self, password, username):
        # TODO: flush this out
        if username == "admin" and password == "admin":
            return True
        return False

    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)

        authenticated = self.check_permission(password, username)

        if authenticated:
            self.set_current_user(username)
            self.write({"authenticated": True})
        else:
            self.write({"error": "login incorrect"})

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", user)
        else:
            self.clear_cookie("user")