from tornado import gen
from tornado.web import authenticated
import datetime
from request_handlers.base_request_handler import BaseRequestHandler
import pymongo
import motor
from tests import backtest

class MACDHandler(BaseRequestHandler):
    client = motor.MotorClient('119.29.16.193')
    db = client.ss_test

    @authenticated
    @gen.coroutine
    def get(self, action=None):
        if action == 'day':
            yield self.getday()
        elif action == 'hour':
            yield self.gethour()
        else:
            self.write_error(404)

    @gen.coroutine
    def getday(self):
         stockcode = int(self.get_argument("stockcode", None))
         n = int(self.get_argument("n", None))
         m = int(self.get_argument("m", None))
         m1 = int(self.get_argument("m1", None))
         starttime = self.get_argument("starttime", None)
         endtime = self.get_argument("endtime", None)

         if starttime == "":
             start = datetime.datetime.strptime("2014-04-07-10-00-00", "%Y-%m-%d-%H-%M-%S")
         else:
             start = datetime.datetime.strptime(starttime, '%Y-%m-%d-%H-%M-%S')

         if endtime   == "":
             end = datetime.datetime.strptime("2015-04-07-10-00-00", "%Y-%m-%d-%H-%M-%S")
         else:
             end   = datetime.datetime.strptime(endtime, '%Y-%m-%d-%H-%M-%S')

         macdlist = yield backtest.backtestmacd(n,m,m1,stockcode,start,end)
         macddict = {}
         macddict["k"] = macdlist[0]
         macddict["d"] = macdlist[1]
         macddict["j"] = macdlist[2]

         self.write(macddict)

    @gen.coroutine
    def gethour(self):
        coll = self.settings["db"].kdj_second
        doc = yield coll.find().to_list[1000]

        self.write(doc["d"])