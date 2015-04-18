from collections import deque
from decimal import Decimal
import logging
from datetime import timedelta
import json
from tornado import gen

from algo_parsers.Condition import Condition
from constants import CUR_PRICE


logger = logging.getLogger(__name__)

class PriceCondition(Condition):

    @classmethod
    def from_dict(cls, condition_dict):
        condition = cls()
        condition.price_type = condition_dict["price_type"]
        condition.price = Decimal(condition_dict["price"])
        condition.window = condition_dict["window"]
        return condition

    def __init__(self):
        Condition.__init__(self)
        self.price_type = None
        self.price = None

    @gen.coroutine
    def match_condition_secondary(self, algo,time):
        """
        :param algo:
        :return:
        """
        min_time = algo.time - timedelta(seconds=self.window)
        max_time = algo.time + timedelta(seconds=self.window)

        find_query = {
            "_id.d": {"$lte": max_time, "$gte": min_time},
            "_id.c": algo.stock_id
        }

        stocks = deque()

        cursor = self.db.stocks_second.find(find_query)

        for stock_dict in (yield cursor.to_list(1000)):
            # most recent one is first
            stocks.append(stock_dict["d"])

        if len(stocks) < 2:
            logger.error("match_condition_secondary")
            logger.error("not enough price data fit the query conditon ")
            return

        for stock in stocks:
            price_curr = Decimal(stock[CUR_PRICE])

            # if there's one price that matches in the window, return True
            if self.price_type == "more_than":
                self.matched = (price_curr > self.price)
            elif self.price_type == "less_than":
                self.matched = (price_curr < self.price)

            if self.matched:
                logger.debug('match %s ok '%algo.algo_id)
                algo.match_price = price_curr
                break
            else:
                logger.error('%s not matched '%algo.algo_id)

    @gen.coroutine
    def match_condition_primary(self, algo,time):
        find_query = {
            "_id.d": {"$lte": algo.time},
            "_id.c": algo.stock_id
        }

        stocks = deque()

        cursor = self.db.stocks_second.find(find_query).sort([("_id.d", -1)]).limit(2)

        for stock_dict in (yield cursor.to_list(100)):
            # most recent one is first
            stocks.append(stock_dict["d"])

        if len(stocks) < 2:
            logger.error("match price condition primary , not enough stocks data fit query condition  ")

            return
        price_curr = Decimal(stocks[0][CUR_PRICE])
        price_prev = Decimal(stocks[1][CUR_PRICE])

        if self.price_type == "more_than":
            self.matched = (price_curr > self.price >= price_prev)
        elif self.price_type == "less_than":
            self.matched = (price_curr < self.price <= price_prev)

        if self.matched:
            logger.debug('match %s ok '%algo.algo_id)
            algo.match_price = price_curr
        else:
            logger.error(' %s not matched '%algo.algo_id)