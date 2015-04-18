from collections import deque
from decimal import Decimal
from datetime import timedelta, datetime
import logging
import pymongo
import json
from tornado import gen
from algo_parsers.Condition import Condition
import constants
from util import shift, avg
import stock

logger = logging.getLogger(__name__)

class KdjCondition(Condition):

    @classmethod
    def from_dict(cls, condition_dict):
        condition = cls()
        condition.n = int(condition_dict["n"])
        condition.m = Decimal(condition_dict["m"])
        condition.m1 = int(condition_dict["m1"])
        condition.window = int(condition_dict["window"])
        condition.d_upper = 100  # not used for now
        condition.d_lower = 0  # not used for now
        return condition

    def __init__(self):
        Condition.__init__(self)
        self.n = None
        self.m = None
        self.m1 = None
        self.d_upper = None
        self.d_lower = None
        self.trade_method = None
        self.stockcollection = None
        self.kdjcollection = None
        self.kdj = deque()
        self.n_low = deque()
        self.n_high = deque()
        self.m_rsv = deque()
        self.m1_k = deque()
        self.match_list=None
    def calc_rsv(self, cur_price):
        shift(self.n_low, cur_price, self.n)  # n_low.append(cur_price)
        shift(self.n_high, cur_price, self.n)
        if len(self.n_low) == self.n:
            logger.debug("max n_high is %d"%max(self.n_high))
            logger.debug("min n_low is %d"%min(self.n_low))
            denominator = (max(self.n_high) - min(self.n_low))  # TODO: 0 caused by price staying same after 3pm, fix it
            print(denominator)

            if 0 == denominator:
                logger.error("0 == denominator")
                return -1

            return (cur_price - min(self.n_low)) / denominator * 100
        return -1

    def calc_k(self, rsv):
        shift(self.m_rsv, rsv, self.m)
        return avg(self.m_rsv)

    def calc_d(self, k):
        shift(self.m1_k, k, self.m1)
        return avg(self.m1_k)

    def ccccc(self, algo,time):
        self.trade_method = algo.trade_method
        #time = algo.referencetime

        lookback_limit = time - timedelta(seconds=self.n *10*algo.period+constants.XINADISTANCE)

        find_query = {
            "_id.d": {"$gte": lookback_limit},
            "_id.c": algo.stock_id
        }

        sort_query = [("_id.d", pymongo.ASCENDING)]

        if 1 == algo.period:
            self.stockcollection = self.db.stocks_second
            self.kdjcollection =  self.db.kdj_second
        else :
            self.stockcollection = self.db.stocks_daily
            self.kdjcollection   = self.db.kdj_daily
        print(find_query)
        cursor = self.stockcollection.find(find_query, sort=sort_query)
        return cursor

    @gen.coroutine
    def kdj_calc(self, algo,time):
        cursor = self.cachefromdb(algo,time)
        for stock_dict in (yield cursor.to_list(100)):
            if 1 == algo.period:
                self.cur_price = Decimal(stock_dict["d"][constants.CUR_PRICE])
                shift(self.n_low, self.cur_price, self.n) # n_low.append(cur_price)
                shift(self.n_high,self.cur_price, self.n)
            else:
                self.cur_price = Decimal(stock_dict["e"][constants.CLOSE_Y])
                low     =   Decimal(stock_dict["e"][constants.LO_Y])
                high    =   Decimal(stock_dict["e"][constants.HI_Y])
                shift(self.n_low, low, self.n) # n_low.append(cur_price)
                shift(self.n_high,high, self.n)

        print("self.n_low:")
        print(self.n_low)
        print(algo.stock_id)
        if len(self.n_low) != self.n:
            raise gen.Return(False)

        rsv = self.calc_rsv(self.cur_price)
        if rsv != -1:
            k = self.calc_k(rsv)
            d = self.calc_d(k)
            j = 3 * k - 2 * d
            #from config import datetime_repr
            #ts = datetime.strptime(stock_dict["_id"]["d"], datetime_repr())
            ts = stock_dict["_id"]["d"]
            self.kdj =[]
            self.kdj.append(k)
            self.kdj.append(d)
            self.kdj.append(j)
            self.kdj.append(ts)
            print("new kdj:")
            print(self.kdj)
            self.kdjcollection.insert({"_id":{"c":algo.stock_id,"d":ts},"d":{"k":self.kdj[0],"d":self.kdj[1],"j":self.kdj[2]}})
            raise gen.Return(True)
        else:
            raise gen.Return(False)


    @gen.coroutine
    def match_condition_secondary(self, algo,time):
        if (yield self.kdj_init(algo)):

            min_time = algo.time - timedelta(seconds=self.window)

            prev_k, prev_d, _, _ = self.kdj.popleft()

            for curr_k, curr_d, _, ts in self.kdj:
                if ts >= min_time:
                    self.matched = self.is_match(prev_k, prev_d, curr_k, curr_d, algo.trade_method)

                    if self.matched:
                        logger.debug('match %s ok '%algo.algo_id)
                        return


    @gen.coroutine
    def match_condition_primary(self, algo,time):
        global stock_dict
        if (yield self.kdj_calc(algo,time)):

            kdjlist =  stock_dict[algo.stock_id]

            klist  = kdjlist[0]
            dlist  = kdjlist[1]
            jlist  = kdjlist[2]

            index =1
            for index in range(len(klist)):
                curr_k = self.klist[0]
                curr_d = self.dlist[1]
                prev_k = kdjlist[0]["d"]["k"]
                prev_d = kdjlist[0]["d"]["d"]

            self.matched = self.is_match(prev_k, prev_d, curr_k, curr_d, algo.trade_method)

            if(self.matched):
                if self.match_list == None:
                    self.match_list = open("../match-list.txt")
                self.match_list.write("match ")
                logger.debug('match %s ok '%algo.algo_id)
                return
            else:
                logger.error('%s not matched '%algo.algo_id)

    def is_match(self, prev_k, prev_d, curr_k, curr_d, trade_method):
        if trade_method == "sell":
            # D should pass K
            if prev_d <= prev_k and curr_d > curr_k:
                return True

        if trade_method == "buy":
            # K should pass D
            if prev_k <= prev_d and curr_k > curr_d:
                return True


        return False