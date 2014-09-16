#!/usr/bin/env python

import motor
import sys
import os
import tornado.options
import tornado.httpserver
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
from tornado.web import Application
from tornado.options import options, define
from algo_parsers.apns_sender import apns_sender
from cron_scripts.crawler import SinaCrawler
from servers import config
from servers.request_handlers import *

here = os.path.dirname(os.path.abspath(__file__))
if here not in sys.path:
        sys.path.append(here)

define("port", default=9990, help="run on the given port", type=int)

client = motor.MotorClient()


class StockApplication(Application):

    def __init__(self):
        handlers = [
            (r"/?", HomeRequestHandler),
            (r"/condition/(macd|kdj|price)/?", ConditionRequestHandler),
            (r"/algo/(upload)/?", AlgoRequestHandler),
            (r"/stock-list/?", StockListRequestHandler),
            (r"/tests/(price|apns)/?", ConditionsTestHandler)
        ]

        settings = dict(
            debug=config.DEBUG,
            xsrf_cookies=not config.DEBUG,
            stock_db=client.ss

        )

        Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(StockApplication())
    http_server.listen(options.port)
    SinaCrawler().fetch_stock_info()
    PeriodicCallback(SinaCrawler().fetch_stock_info, options.interval).start()
    loop = tornado.ioloop.IOLoop.instance()
    loop.add_callback(apns_sender.connect)
    loop.start()


if __name__ == "__main__":
    main()