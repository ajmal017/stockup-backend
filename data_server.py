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


class StockApplication(Application):
    db = motor.MotorClient().ss

    def __init__(self):
        handlers = [
            (r"/?", HomeRequestHandler),
            (r"/condition/(macd|kdj|price)/?", ConditionRequestHandler),
            (r"/algo/(upload)/?", AlgoRequestHandler),
            (r"/stock-list/?", StockListRequestHandler),
        ]

        settings = dict(
            debug=config.DEBUG,
            xsrf_cookies=not config.DEBUG,
            db=StockApplication.db
        )

        Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(StockApplication())
    http_server.listen(options.port)
    if options.env != "test":
        SinaCrawler().fetch_stock_info()
        PeriodicCallback(SinaCrawler().fetch_stock_info, options.interval).start()
    loop = tornado.ioloop.IOLoop.instance()
    loop.add_callback(apns_sender.connect)
    loop.start()


if __name__ == "__main__":
    main()