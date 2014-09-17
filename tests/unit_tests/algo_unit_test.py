from datetime import datetime
import logging
import unittest
import motor
import sys
from tornado import gen
import tornado.ioloop
from tornado.testing import AsyncTestCase, gen_test

from algo_parsers.algorithm import Algorithm
from algo_parsers.apns_sender import apns_sender


class ApnsUnitTest(AsyncTestCase):
    """
    Unit Test for Apple Push Notification
    """
    @gen_test
    def test_apns(self):
        yield gen.Task(apns_sender.connect)
        apns_sender.on_connected()
        result = yield apns_sender.send()
        self.assertTrue(result)

class ConditionUnitTest(AsyncTestCase):
    """
    Unit Test for the Various Algorithms
    """

    @gen_test
    def test_price(self):
        time = datetime(year=2014, month=9, day=15, hour=15, minute=0, second=10)
        Algorithm.db = motor.MotorClient().ss_test
        matches = yield Algorithm.parse_all(time)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].algo_name, "match_algo")

if __name__ == "__main__":
    logging.getLogger('tornado').addHandler(sys.stdout)
    unittest.main()
