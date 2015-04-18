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

from algo_parsers.Apns_sender import ApnsSender
from algo_parsers.Instruction import Instruction
from stock import StockDaily
import config
from cron_scripts.crawler import SinaCrawler
from request_handlers import *


class StockApplication(Application):
    db = motor.MotorClient(options.dbhost).ss_test
    test_db = motor.MotorClient(options.dbhost).ss_test

    def __init__(self):

        settings = dict(
            debug=options.debug,
            xsrf_cookies=False,
            db=StockApplication.db,
            test_db=StockApplication.test_db,
            cookie_secret=options.cookie_secret,
            login_url="/login",
            static_path=os.path.join(here, "static")
        )
        paths = {"path": "./static"}
        handlers = [
            (r"/?", HomeHandler),
            (r"/condition/(macd|kdj|price)/?", ConditionHandler),
            (r"/algo/(upload|remove|list)/?", AlgoHandler),
            (r"/stock-list/?", StockListHandler),
            (r"/login/?", AuthLoginHandler),
            (r"/logout/?", AuthLogoutHandler),
            (r"/kdj/(day|hour|week)/?", KDJHandler),
            (r"/macd/(day|hour|week)/?", MACDHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, paths)

        ]

        Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    loop = tornado.ioloop.IOLoop.instance()
    Instruction.loadall()
    #Stock.loaddailystockfromdb()
    '''
    if options.run_crawler:
        PeriodicCallback(SinaCrawler().fetch_stock_info,
                        options.interval).start()
    '''
    if options.run_server:
        ApnsSender.connect()
        tornado.httpserver.HTTPServer(StockApplication()).listen(options.port)

    loop.start()


if __name__ == "__main__":
    main()
