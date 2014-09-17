#!/usr/bin/env python
from collections import deque, defaultdict
import logging
from datetime import datetime

import motor
from pymongo.errors import DuplicateKeyError
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.options import options, define

from algo_parsers.algorithm import Algorithm
from config import datetime_repr, DEBUG
from util import construct_sina_url


AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

logger = logging.getLogger(__name__)


define("skip", default=0, help="start line in stocks_all.txt", type=int)
define("limit", default=256, help="number of stocks to lookup", type=int)
define("maxConnections", default=256, help="max number of open connections allowed", type=int)
define("interval", default=2470, help="fetch data interval", type=int)


class SinaCrawler:
    num_connections = 0
    stock_catalog = {}
    segmented_catalog = []
    cur_iteration = -1L
    # keep a list of the moment recent times and pray we won't have concurrency issues here
    # i.e. if an earlier time info returns after a later time info
    stock_info_cache = defaultdict(lambda: deque(maxlen=8))
    db = motor.MotorClient().ss

    def __init__(self):
        self.time = datetime.now()

    def stock_info_generator(self, stock_vars):
        for var in stock_vars:
            try:
                stock_info_list = var.split('"')[1].split(',')
                name = stock_info_list[0]
                time_str = stock_info_list[-3] + "T" + stock_info_list[-2]
                time = datetime.strptime(time_str, datetime_repr())

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
                logger.error(str(e))

    @gen.coroutine
    def fetch_stock_info(self):
        if DEBUG:
            print "open crawler connections", SinaCrawler.num_connections
        SinaCrawler.cur_iteration += 1
        if SinaCrawler.num_connections > options.maxConnections:
            return

        # update the catalog every once in a while
        if SinaCrawler.cur_iteration % 1000 == 0:
            val = yield SinaCrawler.db.stock_catalog.find_one()
            if val:
                SinaCrawler.stock_catalog = val["name_code_dict"]
                vals = SinaCrawler.stock_catalog.values()[options.skip:options.limit]
                SinaCrawler.segmented_catalog = []

                length = len(vals)
                wanted_parts = length/30
                SinaCrawler.segmented_catalog = [vals[i*length / wanted_parts: (i+1)*length / wanted_parts] for i in range(wanted_parts)]

        if not SinaCrawler.stock_catalog:
            logger.error("no stock catalog")
            return

        fetch_tasks = []

        http_client = AsyncHTTPClient()

        for segment in SinaCrawler.segmented_catalog:
            fetch_tasks.append(http_client.fetch(construct_sina_url(segment)))
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
            logger.error("fetch_stock_info")
            logger.error(datetime.now())
            logger.error(str(e))
            return

        # TODO: compute KDJ
        # TODO: compute MACD
        # TODO: parse all algorithms, use self.time
        yield Algorithm.parse_all(self.time)
