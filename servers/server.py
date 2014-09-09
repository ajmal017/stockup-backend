import motor
import tornado.options
import tornado.httpserver
import tornado.ioloop
from tornado.web import Application

from tornado.options import options, define

import config
from request_handlers import *


define("port", default=9990, help="run on the given port", type=int)

client = motor.MotorClient()


class StockApplication(Application):

    def __init__(self):
        handlers = [
            (r"/", HomeRequestHandler),
            (r"/macd", MacdRequestHandler),
            (r"/price", PriceRequestHandler)
        ]

        settings = dict(
            debug=config.DEBUG,
            xsrf_cookies=True,
            stock_db=client.ss

        )

        Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(StockApplication())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()