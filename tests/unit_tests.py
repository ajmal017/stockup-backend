#!/usr/bin/env python

from datetime import datetime
import json
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

class CrawlerUnitTest(AsyncTestCase):
    """
    Unit Test for the Sina Crawler
    """

    @gen_test(timeout=20)
    def test_crawler(self):
        SinaCrawler.db = motor.MotorClient().ss
        result = yield SinaCrawler().fetch_stock_info(commit=False)
        self.assertGreater(len(result), 10)

class AuthenticationUnitTest(AsyncTestCase):

    @gen_test
    def test_authentication(self):
        client = AsyncHTTPClient()
        body = {"username": "admin", "password": "admin"}

        yield client.fetch("http://localhost:9990/auth/logout")

        bad_body = {"username": "admin", "password": "wrong"}
        response = yield client.fetch("http://localhost:9990/auth/login", method="POST", body=urllib.urlencode(bad_body))
        d = json.loads(response.body)
        self.assertDictEqual({u'error': u'login incorrect'}, d)

        response = yield client.fetch("http://localhost:9990/auth/login", method="POST", body=urllib.urlencode(body))
        cookie = response.headers["set-cookie"]
        headers = {"Cookie": cookie}

        response = yield client.fetch("http://localhost:9990", headers=headers)
        d = json.loads(response.body)
        self.assertDictEqual({u"you're logged in as": u'admin'}, d)


if __name__ == "__main__":
    logging.getLogger('tornado').addHandler(sys.stdout)
    unittest.main()
