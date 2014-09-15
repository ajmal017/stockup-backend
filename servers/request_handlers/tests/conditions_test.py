from tornado import gen
from algo_parsers.apns_sender import apns_sender
from servers.request_handlers.base_request_handler import BaseRequestHandler


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
        self.write({"test": "price condition"})

    @gen.coroutine
    def test_apns(self):
        yield apns_sender.send()
        self.write({"test": "apns"})


