import ast

from tornado import gen
from tornado.web import authenticated

from request_handlers.base_request_handler import BaseRequestHandler


class AlgoHandler(BaseRequestHandler):

    @authenticated
    @gen.coroutine
    def post(self, action=None):
        if action == 'upload':
            yield self.post_upload()
        elif action == 'remove':
            yield self.post_remove()
        else:
            self.write_end_array(404)

    @gen.coroutine
    def post_remove(self):
        algo_data_raw = self.get_argument("algo", None)
        algo_data = ast.literal_eval(algo_data_raw)

        query = {"_id.algo_id": algo_data["algo_id"]}

        if self.get_argument("test", None):
            yield self.settings["test_db"].algos.remove(query)
        else:
            yield self.settings["db"].algos.save(query)
        self.write({"removed": algo_data["algo_id"]})

    @gen.coroutine
    def post_upload(self):
        algo_data_raw = self.get_argument("algo", None)
        algo_data = ast.literal_eval(algo_data_raw)

        _id = {"algo_id": algo_data["algo_id"], "algo_v": algo_data["algo_v"]}
        algo_data["_id"] = _id

        del algo_data["algo_id"]
        del algo_data["algo_v"]

        if self.get_argument("test", None):
            yield self.settings["test_db"].algos.save(algo_data)
        else:
            yield self.settings["db"].algos.save(algo_data)
        self.write({"saved": algo_data["_id"]["algo_id"]})

    @authenticated
    @gen.coroutine
    def get(self, action=None):
        if action == "list":
            user_id = self.get_argument("user_id", None)

            if self.get_argument("test", None):
                cursor = self.settings["test_db"].algos.find(
                    {"user_id": user_id})
            else:
                cursor = self.settings["db"].algos.find({"user_id": user_id})

            algos = []
            for algo in (yield cursor.to_list(100)):
                algos.append(algo)

            self.write({"algos": algos})
        else:
            self.write_error(404)
