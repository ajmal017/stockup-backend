import json
from tornado import gen
from base_request_handler import BaseRequestHandler


class AlgoRequestHandler(BaseRequestHandler):

    @gen.coroutine
    def post(self, action=None):
        if action == 'upload':
            self.post_upload()

        self.write({'received post': 1})

    @gen.coroutine
    def post_upload(self):
        data = json.loads(self.request.body)
