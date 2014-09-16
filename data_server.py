#!/usr/bin/env python
import sys
if "/var/www/stockup-backend/" not in sys.path:
    sys.path.append("/var/www/stockup-backend/")

import os

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
from tests.conditions_test import ConditionsTestHandler


define("port", default=9990, help="run on the given port", type=int)
define("env", default="dev", help="environment: prod|dev|stage|test", type=str)


class StockApplication(Application):

    def __init__(self):
        handlers = [
            (r"/?", HomeRequestHandler),
            (r"/condition/(macd|kdj|price)/?", ConditionRequestHandler),
            (r"/algo/(upload)/?", AlgoRequestHandler),
            (r"/stock-list/?", StockListRequestHandler),
        ]

        if options.env == "test":
            handlers.extend([
                (r"/tests/(price|apns)/?", ConditionsTestHandler)
            ])

        settings = dict(
            debug=config.DEBUG,
            xsrf_cookies=not config.DEBUG,
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