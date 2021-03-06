#!/usr/bin/env python
from collections import deque, defaultdict
import logging
from datetime import datetime

import motor
from pymongo.errors import DuplicateKeyError
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.options import options, define

from algo_parsers.Instruction import Instruction
from config import datetime_repr, debug_log
from util import construct_sina_url

# AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

logger = logging.getLogger(__name__)

class SinaCrawler:
    num_connections = 0
    stock_catalog = {}
    segmented_catalog = []
    cur_iteration = -1
    # keep a list of the moment recent times and pray we won't have concurrency issues here
    # i.e. if an earlier time info returns after a later time info
    stock_info_cache = defaultdict(lambda: deque(maxlen=8))
    db = motor.MotorClient(options.dbhost).ss_test

    def __init__(self):
        self.time = datetime.now()

    def stock_info_generator(self, stock_vars):
        for var in stock_vars:
            try:
                stock_info_list = var.split('"')[1].split(',')
                name = stock_info_list[0]
                time_str = stock_info_list[-3] + "T" + stock_info_list[-2]
                time = datetime.strptime(time_str, datetime_repr())

                if name in SinaCrawler.stock_info_cache and time in \
                        SinaCrawler.stock_info_cache[name]:
                    # already saved this
                    continue
                else:
                    self.time = time
                    SinaCrawler.stock_info_cache[name].append(time)
                    yield {
                        "_id": {"c": int(SinaCrawler.stock_catalog[name][2:]),
                                "d": time}, "d": stock_info_list}
            except Exception as e:
                logger.error('stock_info_generator ')
                logger.error(datetime.now())
                logger.error(str(e))

    @gen.coroutine
    def fetch_stock_info(self, commit=True):

        SinaCrawler.cur_iteration += 1

        if SinaCrawler.num_connections > options.maxConnections:
            debug_log(logger, "open crawler connections {0}".format(
            SinaCrawler.num_connections))
            return

        # update the catalog every once in a while
        if SinaCrawler.cur_iteration % 1800 == 0:
            val = yield SinaCrawler.db.stock_catalog.find_one()

            if val:
                SinaCrawler.stock_catalog = val["name_code_dict"]
                temp = SinaCrawler.stock_catalog.values()
                vallist = sorted(list(temp))
                vals    = vallist[options.skip:options.limit] #[0:256]
                print(vals)
                SinaCrawler.segmented_catalog = []

                length = len(vals)
                wanted_parts = int(length / options.segmentSize)+1 # 20

                for i in range(wanted_parts):
                    SinaCrawler.segmented_catalog.append(vals[int(i * options.segmentSize): int((i + 1) *options.segmentSize)])
            else:
                logger.error("no stock_catalog in db")


        if not SinaCrawler.stock_catalog:
            logger.error("no stock catalog")
            return

        fetch_tasks = []

        http_client = AsyncHTTPClient()
        for segment in SinaCrawler.segmented_catalog:
            urllist = construct_sina_url(segment)

            print(urllist)

            fetch_tasks.append(http_client.fetch(urllist, request_timeout=20))
            SinaCrawler.num_connections += 1
        try:
            responses = yield fetch_tasks
            SinaCrawler.num_connections -= len(responses)
        except HTTPError as e:
            logger.error("fetch_stock_info")
            logger.error(str(e))
            SinaCrawler.num_connections = 0
            return

        insert_tasks = []
        for response in responses:
            if response.error:
                logger.error(str(datetime.now()))
                logger.error(str(response.error))
            else:
                stock_vars = response.body.decode(encoding='GB18030', errors='strict').strip().split('\n')
                stock_list = [item for item in self.stock_info_generator(stock_vars) if item]
                if stock_list:
                    if commit:
                        print("insert :")
                        print(stock_list)
                        insert_tasks.append(SinaCrawler.db.stocks_second.insert(stock_list, continue_on_error=True))
                    else:
                        print("nothing new info needed to insert")
                        raise gen.Return(stock_list)

        try:
            yield insert_tasks
            print('insert new stocks data done!')
        except DuplicateKeyError as e:
            # only most recent error is reported because of the bulk insert API
            logger.error("fetch_stock_info")
            logger.error(datetime.now())
            logger.error(str(e))
            return

        # TODO: compute KDJ
        # TODO: compute MACD
        # TODO: parse all algorithms, use self.time
        yield Instruction.parse_all(self.time)
