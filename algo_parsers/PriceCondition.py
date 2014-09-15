from decimal import Decimal
from tornado import gen
from algo_parsers.Condition import Condition


class PriceCondition(Condition):

    def __init__(self):
        Condition.__init__(self)
        self.type = None
        self.price = None

    @classmethod
    def from_dict(cls, dict):
        condition = cls()
        condition.type = dict["type"]
        condition.price = Decimal(dict["price"])
        condition.window = dict["window"]
        return condition

    @gen.coroutine
    def match_condition_secondary(self, algo, is_test):
        raise gen.Return(False)

    @gen.coroutine
    def match_condition_primary(self, algo, is_test):
        raise gen.Return(True)