#!/usr/bin/env python
import sys

import motor
import tornado
from tornado.options import define


if "/var/www/stockup-backend/" not in sys.path:
    sys.path.append("/var/www/stockup-backend/")
"""
Script to update the list of valid stocks
"""
from datetime import datetime
import os
import logging

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop, PeriodicCallback

here = os.path.dirname(os.path.abspath(__file__))
par_here = os.path.join(here, os.pardir)
if par_here not in sys.path:
    sys.path.append(par_here)

from util import construct_sina_url

logger = logging.getLogger("update_stock_list")

AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

define("env", default="dev", help="environment: prod|dev|stage|test", type=str)

db = motor.MotorClient().ss


@gen.coroutine
def fetch_info():
    name_code_dict = {}
    code_name_dict = {}

    tasks = []
    client = AsyncHTTPClient()

    for i in range(0, 2000):
        a = "sh60" + str(i).zfill(4)
        url = construct_sina_url([a])
        tasks.append(gen.Task(client.fetch, url))

    responses = yield tasks

    for response in responses:
        body = response.body.decode(encoding='GB18030', errors='strict').strip()
        stock_info_list = body.split('"')[1].split(',')
        sid = body.split('"')[0].strip("=").split("_")[-1]
        if len(stock_info_list) > 1:
            name = stock_info_list[0]
            code_name_dict[sid] = name
            name_code_dict[name] = sid

    try:
        _id = yield db.stock_catalog.save({"_id": "stock_catalog",
                                           "name_code_dict": name_code_dict,
                                           "code_name_dict": code_name_dict})
        logger.info("saved stock catalog")
        logger.info(str(_id))

    except Exception, e:
        logger.error(datetime.now())
        logger.error(str(e))


def main():
    tornado.options.parse_command_line()
    fetch_info()
    PeriodicCallback(fetch_info, 2 * 3600 * 1000).start()
    IOLoop.instance().start()


if __name__ == "__main__":
    main()