#!/usr/bin/env python

import logging
import sys
import urlparse
from datetime import datetime

import motor
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import options, define


AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

logging.basicConfig(filename='../../crawler_log',level=logging.INFO)
logger = logging.getLogger(__name__)

db = motor.MotorClient().ss

define("start", default=20, help="start line in stocks_all.txt")
define("count", default=30, help="number of stocks to lookup in stocks_all.txt")
define("maxConnections", default=50, help="max number of open connections allowed")
define("interval", default=2000, help="max number of open connections allowed")

class SinaCrawler:
    num_connections = 0
    stocks_list_all = open('stocks_all.txt', 'r').readlines()

    def __init__(self):
        self.start_line = options.start
        self.count = options.count
        self.connection_limit = options.maxConnections
        self.stock_ids = []
        self.coll = db.stocks
        self.parse_stocks_list()
        self.stock_info_cache = {}

    @property
    def datetime_repr(self):
        return '%Y-%m-%dT%H:%M:%S'

    def inserted(self, result, error):
        if error:
            logger.error(str(error))
        else:
            #TODO: parse the newly inserted data
            pass


    def stock_info_generator(self, stock_vars):
        for var in stock_vars:
            try:
                stock_info_list = var.split('"')[1].split(',')
                name = stock_info_list[0]
                time_str = stock_info_list[-3] + "T" + stock_info_list[-2]
                time = datetime.strptime(time_str, self.datetime_repr)
                if name in self.stock_info_cache and self.stock_info_cache[name] == time:
                    # already saved this
                    continue
                else:
                    self.stock_info_cache[name] = time
                    yield {"_id": {"c": name, "d": time}, "d": stock_info_list}
            except Exception, e:
                logger.error(sys.exc_info()[0])


    def handle_request(self, response):
        SinaCrawler.num_connections -= 1

        if response.error:
            logger.error(response.error)
        else:
            stock_vars = response.body.decode(encoding='GB18030', errors='strict').strip().split('\n')
            stock_list = [item for item in self.stock_info_generator(stock_vars) if item]
            if stock_list:
                self.coll.insert(stock_list, callback=self.inserted, continue_one_error=True)




    def parse_stocks_list(self):
        cur_line = -1
        for line in SinaCrawler.stocks_list_all:
            if line[0] == "#": continue
            cur_line += 1
            if cur_line < self.start_line:
                continue
            if cur_line >= self.start_line + self.count:
                break
            name, sid = line.strip().split()
            self.stock_ids.append(sid)


    def construct_url(self):
        scheme = "http"
        netloc = "hq.sinajs.cn:80"
        path = "/"
        params = ""
        query = "list=" + ",".join("sh"+str(s) for s in self.stock_ids)
        frags = ""
        return urlparse.urlunparse((scheme, netloc, path, params, query, frags))


    def fetch_stock_info(self):
        if SinaCrawler.num_connections > self.connection_limit:
            return

        http_client = AsyncHTTPClient()
        http_client.fetch(self.construct_url(), self.handle_request)
        SinaCrawler.num_connections += 1


def main():
    crawler = SinaCrawler()
    periodic_callback = PeriodicCallback(crawler.fetch_stock_info, 500)
    periodic_callback.start()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()