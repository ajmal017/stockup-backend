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

from algo_parsers.apns_sender import ApnsSender
import config
from cron_scripts.crawler import SinaCrawler
from request_handlers import *


define("port", default=9990, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode", type=bool)
define("env", default="dev", help="environment: prod|dev|stage", type=str)
define("run_crawler", default=True, help="run the crawler", type=bool)
define("run_server", default=True, help="run the server", type=bool)
define("cookie_secret", default=config.COOKIE_KEY,
       help="the key to generate secure cookies", type=str)


class StockApplication(Application):
    db = motor.MotorClient().ss
    test_db = motor.MotorClient().ss_test

    def __init__(self):

        settings = dict(
            debug=options.debug,
            xsrf_cookies=False,
            db=StockApplication.db,
            test_db=StockApplication.test_db,
            cookie_secret=options.cookie_secret,
            login_url="/auth/login",
            static_path=os.path.join(here, "static")
        )

        handlers = [
            (r"/?", HomeHandler),
            (r"/condition/(macd|kdj|price)/?", ConditionHandler),
            (r"/algo/(upload|remove|list)/?", AlgoHandler),
            (r"/stock-list/?", StockListHandler),
            (r"/auth/login/?", AuthLoginHandler),
            (r"/auth/logout/?", AuthLogoutHandler),
            (r"/add-token/?", ApnsTokenHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"})

        ]

        Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    loop = tornado.ioloop.IOLoop.instance()

    if options.run_crawler:
        SinaCrawler().fetch_stock_info()
        PeriodicCallback(SinaCrawler().fetch_stock_info,
                         options.interval).start()

    if options.run_server:
        ApnsSender.connect()
        tornado.httpserver.HTTPServer(StockApplication()).listen(options.port)

    loop.start()


if __name__ == "__main__":
    main()