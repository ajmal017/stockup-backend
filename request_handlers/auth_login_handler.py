from tornado.web import MissingArgumentError

from request_handlers.base_request_handler import BaseRequestHandler


class AuthLoginHandler(BaseRequestHandler):

    def get(self):
        self.render('../static/login/index.html')

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
            self.redirect('/static/test/index.html', permanent=True)
        else:
            self.write({"username": username})
            self.write({"password": password})
            self.write({"error": "login incorrect"})

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", user)
        else:
            self.clear_cookie("user")