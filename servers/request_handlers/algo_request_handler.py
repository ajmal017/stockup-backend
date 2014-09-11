import json
from tornado import gen
from base_request_handler import BaseRequestHandler


class AlgoRequestHandler(BaseRequestHandler):

    @gen.coroutine
    def post(self, action=None):
        if action == 'upload':
            data = json.loads(self.request.body)

        self.write({'received post': 1})