#!/usr/bin/env python
import ast
from datetime import datetime
import logging
import os
import unittest
import sys
import urllib

import motor
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncTestCase, gen_test


here = os.path.dirname(os.path.abspath(__file__))
par_here = os.path.join(here, os.pardir)
if par_here not in sys.path:
    sys.path.append(par_here)

from algo_parsers.algorithm import Algorithm
from algo_parsers.apns_sender import apns_sender
from cron_scripts.crawler import SinaCrawler


class BaseUnitTest(AsyncTestCase):
    base_url = "http://stockup-dev.cloudapp.net:9990"
    # base_url = "http://localhost:9990"
    headers = None

    @gen.coroutine
    def login(self):
        body = {"username": "admin", "password": "admin"}
        response = yield AsyncHTTPClient().fetch(BaseUnitTest.base_url + "/auth/login",
                                                 method="POST",
                                                 body=urllib.urlencode(body))
        BaseUnitTest.headers = {"Cookie": response.headers["set-cookie"]}

    @gen.coroutine
    def logout(self):
        yield AsyncHTTPClient().fetch(BaseUnitTest.base_url + "/auth/logout")
        BaseUnitTest.headers = None


class ApnsUnitTest(BaseUnitTest):
    """
    Unit Test for Apple Push Notification
    """

    @gen_test
    def test_apns(self):
        yield gen.Task(apns_sender.connect)
        apns_sender.on_connected()
        result = yield apns_sender.send()
        self.assertTrue(result)


class AlgoUnitTest(BaseUnitTest):
    """
    Unit Test for the Various Algorithms
    """

    @gen_test
    def test_price_condition(self):
        time = datetime(year=2014, month=9, day=15, hour=15, minute=0,
                        second=10)
        Algorithm.db = motor.MotorClient().ss_test
        matches = yield Algorithm.parse_all(time)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].algo_name, "match_algo")

    @gen_test
    def test_algo_post(self):
        yield self.login()
        body = {"algo": {
            "algo_v": 1,
            "algo_id": "upload_algo_id",
            "algo_name": "upload_algo",
            "stock_id": 600100,
            "user_id": "robert",
            "price_type": "market",
            "trade_method": "sell",
            "volume": 100,
            "primary_condition": "price_condition",
            "conditions": {
                "price_condition": {
                    "price_type": "more_than",
                    "price": "130.00",
                    "window": "60"
                }
            }
        }, "test": 1}

        response = yield AsyncHTTPClient().fetch(AlgoUnitTest.base_url + "/algo/upload",
                                                 method="POST",
                                                 headers=AlgoUnitTest.headers,
                                                 body=urllib.urlencode(body))
        d = ast.literal_eval(response.body)
        self.assertDictEqual(d, {"saved": "upload_algo_id"})
        yield self.logout()

    @gen_test
    def test_algo_remove(self):
        yield self.login()
        body = {"algo": {
            "algo_v": 1,
            "algo_id": "upload_algo_id"
        }, "test": 1}

        response = yield AsyncHTTPClient().fetch(AlgoUnitTest.base_url + "/algo/remove",
                                                 method="POST",
                                                 headers=AlgoUnitTest.headers,
                                                 body=urllib.urlencode(body))
        d = ast.literal_eval(response.body)
        self.assertDictEqual(d, {"removed": "upload_algo_id"})
        yield self.logout()

    @gen_test
    def test_algo_get(self):
        pass


class CrawlerUnitTest(BaseUnitTest):
    """
    Unit Test for the Sina Crawler
    """

    @gen_test(timeout=20)
    def test_crawler(self):
        SinaCrawler.db = motor.MotorClient().ss
        result = yield SinaCrawler().fetch_stock_info(commit=False)
        self.assertGreater(len(result), 10)


class AuthenticationUnitTest(BaseUnitTest):
    @gen_test
    def test_authentication(self):
        cls = AuthenticationUnitTest
        client = AsyncHTTPClient()
        yield client.fetch(cls.base_url + "/auth/logout")

        bad_body = {"username": "admin", "password": "wrong"}
        response = yield client.fetch(cls.base_url + "/auth/login",
                                      method="POST",
                                      body=urllib.urlencode(bad_body))
        d = ast.literal_eval(response.body)
        self.assertDictEqual({u'error': u'login incorrect'}, d)

        body = {"username": "admin", "password": "admin"}
        response = yield client.fetch(cls.base_url + "/auth/login",
                                      method="POST",
                                      body=urllib.urlencode(body))
        cookie = response.headers["set-cookie"]
        headers = {"Cookie": cookie}

        response = yield client.fetch(cls.base_url, headers=headers)
        d = ast.literal_eval(response.body)
        self.assertDictEqual({u"you're logged in as": u'admin'}, d)


if __name__ == "__main__":
    logging.getLogger('tornado').addHandler(sys.stdout)
    unittest.main()
