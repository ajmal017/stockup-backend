from datetime import datetime
from tornado import gen

from algo_parsers.algorithm import Algorithm
from algo_parsers.apns_sender import apns_sender
from config import get_client
from request_handlers.base_request_handler import BaseRequestHandler


class ConditionsTestHandler(BaseRequestHandler):

    @gen.coroutine
    def get(self, condition=None):
        if condition == 'price':
            yield self.test_price()
        elif condition == 'apns':
            yield self.test_apns()
        else:
            self.send_error(404)

    @gen.coroutine
    def test_price(self):
        # Use a different DB for test
        time = datetime(year=2014, month=9, day=15, hour=15, minute=0, second=10)
        Algorithm.db = get_client().ss_test
        matches = yield Algorithm.parse_all(time)
        for match in matches:
            self.write({"matched": {"algo_name": match.algo_name, "time": str(match.time)}})
        if not matches:
            self.write("no matches")

    @gen.coroutine
    def test_apns(self):
        yield apns_sender.send()
        self.write({"test": "apns"})


