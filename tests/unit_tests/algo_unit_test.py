import unittest
import tornado.ioloop
from tornado.testing import AsyncTestCase

from algo_parsers.algorithm import Algorithm


class CrawlerUnitTest(AsyncTestCase):
    """
    Unit Test for the Various Algorithms
    """

    @tornado.testing.gen_test
    def test_algo_parser(self):
        def f(callback):
            yield Algorithm().parse_all()
            callback()
        f(self.stop)
        self.wait()



def all():
    return unittest.defaultTestLoader.loadTestsFromNames(['tests.unit_tests.algo_unit_test'])

if __name__ == "__main__":
    unittest.main()
