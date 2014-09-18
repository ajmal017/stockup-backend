#!/usr/bin/env python
import sys
import os

import motor
import tornado.httpserver
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
from tornado.web import Application
from tornado.options import options, define


here = os.path.dirname(os.path.abspath(__file__))
if here not in sys.path:
    sys.path.append(here)

from algo_parsers.apns_sender import apns_sender
import config
from cron_scripts.crawler import SinaCrawler
from request_handlers import *


define("port", default=9990, help="run on the given port", type=int)
define("env", default="dev", help="environment: prod|dev|stage|test", type=str)
define("crawler_only", default=False, help="run only the crawler", type=bool)
define("cookie_secret", default=config.COOKIE_KEY,
       help="the key to generate secure cookies", type=str)


class StockApplication(Application):
    db = motor.MotorClient().ss
    test_db = motor.MotorClient().ss_test

    def __init__(self):
        handlers = [
            (r"/?", HomeHandler),
            (r"/condition/(macd|kdj|price)/?", ConditionHandler),
            (r"/algo/(upload|remove)/?", AlgoHandler),
            (r"/stock-list/?", StockListHandler),
            (r"/auth/login/?", AuthLoginHandler),
            (r"/auth/logout/?", AuthLogoutHandler)

        ]

        settings = dict(
            debug=config.DEBUG,
            xsrf_cookies=False,
            db=StockApplication.db,
            test_db=StockApplication.test_db,
            cookie_secret=options.cookie_secret,
            login_url="/auth/login"
        )

        Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    loop = tornado.ioloop.IOLoop.instance()

    if options.env != "test":
        SinaCrawler().fetch_stock_info()
        PeriodicCallback(SinaCrawler().fetch_stock_info,
                         options.interval).start()

    if not options.crawler_only:
        apns_sender.connect()
        tornado.httpserver.HTTPServer(StockApplication()).listen(options.port)

    loop.start()


if __name__ == "__main__":
    main()