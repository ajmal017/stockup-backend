import unittest
import tornado
import tornado.ioloop
from tornado import gen
from tornado.options import options

from algo_parsers.algorithm import Algorithm


class CrawlerUnitTest():
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
    CrawlerUnitTest().test_algo_parser()
    # unittest.main()
    options.logging = None
    tornado.ioloop.IOLoop.instance().start()

