from datetime import datetime
import motor
from tornado import gen

from algo_parsers.algorithm import Algorithm
from algo_parsers.apns_sender import apns_sender
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
        Algorithm.db = motor.MotorClient().ss_test
        time = datetime.now()
        yield Algorithm().parse_all(time)
        self.write({"test": "price condition"})

    @gen.coroutine
    def test_apns(self):
        yield apns_sender.send()
        self.write({"test": "apns"})


