import json

from tornado import gen

from request_handlers.base_request_handler import BaseRequestHandler


class AlgoRequestHandler(BaseRequestHandler):

    @gen.coroutine
    def post(self, action=None):
        if action == 'upload':
            self.post_upload()

        self.write({'received post': 1})

    @gen.coroutine
    def post_upload(self):
        algo_data = json.loads(self.request.body)
        # save algo data
        _id = {"algo_id": algo_data["algo_id"], "algo_v": algo_data["algo_v"]}
        algo_data["_id"] = _id
        del algo_data["algo_id"]
        del algo_data["algo_v"]
        self.db.algos.save(algo_data)
