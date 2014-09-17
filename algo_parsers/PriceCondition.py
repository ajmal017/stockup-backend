from collections import deque
from decimal import Decimal
import logging
from datetime import timedelta
from tornado import gen
from algo_parsers.Condition import Condition
from constants import PRICE_INDEX

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
    def match_condition_secondary(self, algo):
        min_time = algo.time - timedelta(seconds=self.window)
        max_time = algo.time + timedelta(seconds=self.window)

        find_query = {
            "_id.d": {"$lte": max_time, "$gte": min_time},
            "_id.c": algo.stock_id
        }

        stocks = deque()

        from config import get_db
        cursor = get_db().stocks.find(find_query)

        for stock_dict in (yield cursor.to_list(100)):
            # most recent one is first
            stocks.append(stock_dict["d"])

        if len(stocks) < 2:
            logger.error("match_condition_secondary")
            logger.error("not enough stocks data")
            raise gen.Return(False)

        matched = False

        for stock in stocks:
            price_curr = Decimal(stock[PRICE_INDEX])

            # if there's one price that matches in the window, return True
            if self.price_type == "more_than":
                matched = (price_curr > self.price)
            elif self.price_type == "less_than":
                matched = (price_curr < self.price)
            if matched:
                raise gen.Return(True)
        
        raise gen.Return(False)

    @gen.coroutine
    def match_condition_primary(self, algo):
        find_query = {
            "_id.d": {"$lte": algo.time},
            "_id.c": algo.stock_id
        }

        stocks = deque()

        from config import get_db
        from algo_parsers.algorithm import Algorithm
        cursor = get_db().stocks.find(find_query).sort([("_id.d", -1)]).limit(2)

        for stock_dict in (yield cursor.to_list(100)):
            # most recent one is first
            stocks.append(stock_dict["d"])

        if len(stocks) < 2:
            logger.error("match_condition_primary")
            logger.error("not enough stocks data")
            raise gen.Return(False)

        price_curr = Decimal(stocks[0][PRICE_INDEX])
        price_prev = Decimal(stocks[1][PRICE_INDEX])

        matched = None

        if self.price_type == "more_than":
            matched = price_curr > self.price > price_prev
        elif self.price_type == "less_than":
            matched = price_curr < self.price < price_prev

        raise gen.Return(matched)