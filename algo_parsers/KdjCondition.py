from collections import deque
from decimal import Decimal
from datetime import timedelta, datetime
import logging
import pymongo

from tornado import gen
from algo_parsers.Condition import Condition
from constants import CUR_PRICE
from util import shift, avg

logger = logging.getLogger(__name__)

class KdjCondition(Condition):

    @classmethod
    def from_dict(cls, condition_dict):
        condition = cls()
        condition.n = condition_dict["n"]
        condition.m = Decimal(condition_dict["m"])
        condition.m1 = condition_dict["m1"]
        condition.window = condition_dict["window"]
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
        self.kdj = deque()
        self.n_low = deque()
        self.n_high = deque()
        self.m_rsv = deque()
        self.m1_k = deque()

    def calc_rsv(self, cur_price):
        shift(self.n_low, cur_price, self.n)
        shift(self.n_high, cur_price, self.n)
        if len(self.n_low) == self.n:
            denominator = (max(self.n_high) - min(self.n_low))  # TODO: 0 caused by price staying same after 3pm, fix it
            return (cur_price - min(self.n_low)) / denominator * 100
        return -1

    def calc_k(self, rsv):
        shift(self.m_rsv, rsv, self.m)
        return avg(self.m_rsv)

    def calc_d(self, k):
        shift(self.m1_k, k, self.m1)
        return avg(self.m1_k)

    @gen.coroutine
    def kdj_init(self, algo):
        self.trade_method = algo.trade_method
        time = algo.time

        lookback_limit = time - timedelta(seconds=self.n * 10)

        find_query = {
            "_id.d": {"$gte": lookback_limit},
            "_id.c": algo.stock_id
        }

        sort_query = [("_id.d", pymongo.ASCENDING)]

        cursor = self.db.stocks.find(find_query, sort=sort_query)
        for stock_dict in (yield cursor.to_list(1000)):
            price = Decimal(stock_dict["d"][CUR_PRICE])
            rsv = self.calc_rsv(price)
            if rsv != -1:
                k = self.calc_k(rsv)
                d = self.calc_d(k)
                j = 3 * k - 2 * d
                from config import datetime_repr
                ts = datetime.strptime(stock_dict["_id"]["d"], datetime_repr())
                self.kdj.append([k, d, j, ts])

        if len(self.kdj) < 2:
            logger.error("match_condition_primary")
            logger.error("not enough kdj data")
            raise gen.Return(False)

        raise gen.Return(True)


    @gen.coroutine
    def match_condition_secondary(self, algo):
        if (yield self.kdj_init(algo)):

            min_time = algo.time - timedelta(seconds=self.window)

            prev_k, prev_d, _, _ = self.kdj.popleft()

            for curr_k, curr_d, _, ts in self.kdj:
                if ts >= min_time:
                    self.matched = self.is_match(prev_k, prev_d, curr_k, curr_d, algo.trade_method)

                    if self.matched:
                        return


    @gen.coroutine
    def match_condition_primary(self, algo):

        if (yield self.kdj_init(algo)):

            prev_d = self.kdj[-2][1]
            prev_k = self.kdj[-2][0]
            curr_d = self.kdj[-2][1]
            curr_k = self.kdj[-2][0]

            self.matched = self.is_match(prev_k, prev_d, curr_k, curr_d, algo.trade_method)


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