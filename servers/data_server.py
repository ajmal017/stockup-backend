#!/usr/bin/env python

import motor
import tornado.options
import tornado.httpserver
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
from tornado.web import Application
from tornado.options import options, define
from cron_scripts.crawler import SinaCrawler

from request_handlers import *
import config


define("port", default=9990, help="run on the given port", type=int)

client = motor.MotorClient()


class StockApplication(Application):

    def __init__(self):
        handlers = [
            (r"/?", HomeRequestHandler),
            (r"/condition/(macd|kdj|price)/?", ConditionRequestHandler),
            (r"/algo/(upload)/?", AlgoRequestHandler),
            (r"/stock-list/?", StockListRequestHandler)
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
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()