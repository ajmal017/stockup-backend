#!/usr/bin/env python
import codecs

import logging
import sys
import urlparse
from datetime import datetime

import motor
from pymongo.errors import DuplicateKeyError
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import options, define, parse_command_line


AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

logger = logging.getLogger(__name__)


define("start", default=0, help="start line in stocks_all.txt")
define("count", default=300, help="number of stocks to lookup in stocks_all.txt")
define("maxConnections", default=500, help="max number of open connections allowed")
define("interval", default=2000, help="fetch data interval")
define("debug", default=False, help="print debug statements to the console")

class SinaCrawler:
    num_connections = 0
    ## TODO: make this not hard coded in
    try:
        stocks_list_all = codecs.open('stocks_all.txt', 'r', encoding='utf-8').readlines()
    except IOError, e:
        stocks_list_all = codecs.open('/var/www/stockup-backend/cron_scripts/stocks_all.txt', 'r', encoding='utf-8').readlines()

    def __init__(self):
        self.start_line = options.start
        self.count = options.count
        self.connection_limit = options.maxConnections
        self.stock_catalog = {}
        self.segmented_catalog = []
        self.db = motor.MotorClient().ss
        self.stock_info_cache = {}
        self.cur_iteration = -1L

    @property
    def datetime_repr(self):
        return '%Y-%m-%dT%H:%M:%S'

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
                    yield {"_id": {"c": int(self.stock_catalog[name][2:]), "d": time}, "d": stock_info_list}
            except Exception, e:
                logger.error('stock_info_generator ')
                logger.error(datetime.now())
                logger.error(e)

    @classmethod
    def construct_url(cls, values):
        scheme = "http"
        netloc = "hq.sinajs.cn:80"
        path = "/"
        params = ""
        query = "list=" + ",".join(str(s) for s in values)
        frags = ""
        return urlparse.urlunparse((scheme, netloc, path, params, query, frags))


    @gen.coroutine
    def fetch_stock_info(self):
        if options.debug:
            print "open connections", SinaCrawler.num_connections
        self.cur_iteration += 1
        if SinaCrawler.num_connections > self.connection_limit:
            return

        # update the catalog every once in a while
        if self.cur_iteration % 1000 == 0:
            val = yield self.db.stock_catalog.find_one()
            self.stock_catalog = val["name_code_dict"]
            vals = self.stock_catalog.values()[options.start:options.count]
            self.segmented_catalog = []

            length = len(vals)
            wanted_parts = length/30
            self.segmented_catalog = [ vals[i*length / wanted_parts: (i+1)*length / wanted_parts] for i in range(wanted_parts) ]


        if not self.stock_catalog:
            return

        fetch_tasks = []

        http_client = AsyncHTTPClient()

        for segment in self.segmented_catalog:
            fetch_tasks.append(http_client.fetch(self.construct_url(segment)))
            SinaCrawler.num_connections += 1

        responses = yield fetch_tasks
        SinaCrawler.num_connections -= len(responses)

        insert_tasks = []
        for response in responses:
            if response.error:
                logger.error(datetime.now())
                logger.error(response.error)
            else:
                stock_vars = response.body.decode(encoding='GB18030', errors='strict').strip().split('\n')
                stock_list = [item for item in self.stock_info_generator(stock_vars) if item]
                if stock_list:
                    insert_tasks.append(self.db.stocks.insert(stock_list, continue_on_error=True))

        try:
            ids = yield insert_tasks
        except DuplicateKeyError, e:
            logger.error(datetime.now())
            logger.error(str(e))
            return
        #TODO: parse the newly inserted data
        pass


def main():
    parse_command_line()
    crawler = SinaCrawler()
    crawler.fetch_stock_info()
    periodic_callback = PeriodicCallback(crawler.fetch_stock_info, options.interval)
    periodic_callback.start()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()