from collections import deque
from decimal import Decimal
import logging
from tornado import gen
from algo_parsers.Condition import Condition

logger = logging.getLogger(__name__)

class PriceCondition(Condition):

    def __init__(self):
        Condition.__init__(self)
        self.type = None
        self.price = None

    @classmethod
    def from_dict(cls, condition_dict):
        condition = cls()
        condition.price_type = condition_dict["price_type"]
        condition.price = Decimal(condition_dict["price"])
        condition.window = condition_dict["window"]
        return condition

    @gen.coroutine
    def match_condition_secondary(self, algo):
        raise gen.Return(False)

    @gen.coroutine
    def match_condition_primary(self, algo):
        find_query = {
            "_id.d": {"$lte": algo.time},
            "_id.c": algo.stock_id
        }

        stocks = deque()

        from algo_parsers.algorithm import Algorithm
        cursor = Algorithm.db.stocks.find(find_query).sort({"_id.d": -1}).limit(2)

        for stock_dict in (yield cursor.to_list(100)):
            # most recent one is first
            stocks.append(stock_dict["d"])

        if len(stocks) < 2:
            logger.error("match_condition_primary")
            logger.error("not enough stocks data")
            raise gen.Return(False)

        # placeholder, we may want to eventually do something different for
        # market and limited
        price_curr = Decimal(stocks[0][3])
        price_prev = Decimal(stocks[1][3])
        matched = False
        if algo.price_type == "market" or algo.price_type == "limited":
            if self.type == "more_than":
                matched = price_curr > self.price > price_prev
            elif self.type == "less_than":
                matched = price_curr < self.price < price_prev

        raise gen.Return(matched)