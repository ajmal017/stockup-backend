from tornado import gen
from tornado.web import authenticated

from request_handlers.base_request_handler import BaseRequestHandler


class ApnsTokenHandler(BaseRequestHandler):

    @authenticated
    @gen.coroutine
    def post(self):
        token = self.get_argument("apns_token", None)
        user_id = self.get_argument("user_id", None)

        if self.get_argument("test", None):
            db = self.settings["test_db"]
        else:
            db = self.settings["db"]

        query = {"_id": user_id}
        update = {"$addToSet": {"apns_tokens": token}}

        yield db.users.update(query, update, upsert=True)

        self.write({"added token": str(token)})