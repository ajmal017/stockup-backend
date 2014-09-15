import unittest
import tornado
import tornado.ioloop
from tornado import gen
from tornado.options import options

from algo_parsers.algorithm import Algorithm
from cron_scripts.crawler import SinaCrawler


class CrawlerUnitTest(unittest.TestCase):
    """
    Unit Test for the Various Algorithms
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @gen.coroutine
    def test_algo_parser(self):
        Algorithm().parse_all(1)

if __name__ == "__main__":
    unittest.main()
    options.logging = None
    SinaCrawler().fetch_stock_info()
    periodic_callback = tornado.PeriodicCallback(SinaCrawler().fetch_stock_info, options.interval)
    tornado.ioloop.IOLoop.instance().start()
