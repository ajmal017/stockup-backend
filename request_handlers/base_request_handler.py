from tornado.web import RequestHandler


class BaseRequestHandler(RequestHandler):
    def initialize(self):
        self.set_header("Cache-Control", "no-cache, must-revalidate")

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.write({"error": 404,
                        "description": "The requested resource could not be found but may be available again in the future"})

    def write_start_array(self):
        self.write("[")

    def write_end_array(self):
        self.write("]")

    def write_separator(self):
        self.write(",")

    def write_linebreak(self):
        self.write("\n")

    def get_current_user(self):
        return self.get_secure_cookie("user")
