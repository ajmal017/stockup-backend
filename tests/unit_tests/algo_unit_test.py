from datetime import datetime
import logging
import unittest
import motor
import sys
from tornado import gen
import tornado.ioloop
from tornado.testing import AsyncTestCase, gen_test

from algo_parsers.algorithm import Algorithm
from config import get_client


class CrawlerUnitTest(AsyncTestCase):
    """
    Unit Test for the Various Algorithms
    """

    @gen_test
    def test_price(self):
        # Use a different DB for test
        db = motor.MotorClient().ss_test
        cursor = db.algos.find()
        print db,cursor

        @gen.coroutine
        def f():
            for i in (yield cursor.to_list(100)):
                print i
        u = yield f()
        print "here2"
        time = datetime(year=2014, month=9, day=15, hour=15, minute=0, second=10)
        Algorithm.db = get_client().ss_test
        print Algorithm.db
        matches = yield Algorithm.parse_all(time)
        print matches

if __name__ == "__main__":
    logging.getLogger('tornado').addHandler(sys.stdout)
    unittest.main()
