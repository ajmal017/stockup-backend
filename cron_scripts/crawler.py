#!/usr/bin/env python
import codecs
from collections import deque, defaultdict

import logging
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
define("count", default=256, help="number of stocks to lookup in stocks_all.txt")
define("maxConnections", default=256, help="max number of open connections allowed")
define("interval", default=2470, help="fetch data interval")
define("debug", default=False, help="print debug statements to the console")


class SinaCrawler:
    num_connections = 0
    stock_catalog = {}
    segmented_catalog = []
    db = motor.MotorClient().ss
    cur_iteration = -1L
    # keep a list of the moment recent times and pray we won't have concurrency issues here
    # i.e. if an earlier time info returns after a later time info
    stock_info_cache = defaultdict(lambda: deque(maxlen=8))

    def __init__(self):
        self.time = datetime.now()

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

                if name in SinaCrawler.stock_info_cache and time in SinaCrawler.stock_info_cache[name]:
                    # already saved this
                    continue
                else:
                    self.time = time
                    SinaCrawler.stock_info_cache[name].append(time)
                    yield {"_id": {"c": int(SinaCrawler.stock_catalog[name][2:]), "d": time}, "d": stock_info_list}
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
        SinaCrawler.cur_iteration += 1
        if SinaCrawler.num_connections > options.maxConnections:
            return

        # update the catalog every once in a while
        if SinaCrawler.cur_iteration % 1000 == 0:
            val = yield SinaCrawler.db.stock_catalog.find_one()
            SinaCrawler.stock_catalog = val["name_code_dict"]
            vals = SinaCrawler.stock_catalog.values()[options.start:options.count]
            SinaCrawler.segmented_catalog = []

            length = len(vals)
            wanted_parts = length/30
            SinaCrawler.segmented_catalog = [ vals[i*length / wanted_parts: (i+1)*length / wanted_parts] for i in range(wanted_parts) ]


        if not SinaCrawler.stock_catalog:
            return

        fetch_tasks = []

        http_client = AsyncHTTPClient()

        for segment in SinaCrawler.segmented_catalog:
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
                    insert_tasks.append(SinaCrawler.db.stocks.insert(stock_list, continue_on_error=True))

        try:
            yield insert_tasks
        except DuplicateKeyError, e:
            # only most recent error is reported because of the bulk insert API
            logger.error(datetime.now())
            logger.error(str(e))
            return

        # TODO: computer KDJ
        # TODO: computer MACD
        # TODO: parse all algorithms, use self.time



def main():
    parse_command_line()
    # create a new instance
    SinaCrawler().fetch_stock_info()
    periodic_callback = PeriodicCallback(SinaCrawler().fetch_stock_info, options.interval)
    periodic_callback.start()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()