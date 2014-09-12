#!/usr/bin/env python

"""
Script to update the list of valid stocks
"""
from datetime import datetime
import logging

import motor
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop, PeriodicCallback
from crawler import SinaCrawler

db = motor.MotorClient().ss
coll = db.stock_catalog
logger = logging.getLogger("update_stock_list")

AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

@gen.coroutine
def fetch_info():
    name_code_dict = {}
    code_name_dict = {}
    for i in range(0, 2000):
        a = "sh60" + str(i).zfill(4)
        url = SinaCrawler.construct_url([a])
        client = AsyncHTTPClient()

        task = gen.Task(client.fetch, url)
        yield task
        response = task.result()
        body = response.body.decode(encoding='GB18030', errors='strict').strip()
        stock_info_list = body.split('"')[1].split(',')
        sid = body.split('"')[0].strip("=").split("_")[-1]
        if len(stock_info_list) > 1:
            name = stock_info_list[0]
            code_name_dict[sid] = name
            name_code_dict[name] = sid
    coll.save({"_id": "stock_catalog",
               "name_code_dict": name_code_dict,
               "code_name_dict": code_name_dict}, callback=inserted)

def inserted(self, result, error):
    if error:
        logger.error(datetime.now())
        logger.error(str(error))
    else:
        print result


fetch_info()
PeriodicCallback(fetch_info, 2*3600*1000).start()
IOLoop.instance().start()