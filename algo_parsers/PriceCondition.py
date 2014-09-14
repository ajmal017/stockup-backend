from tornado import gen
from algo_parsers.Condition import Condition


class PriceCondition(Condition):

    @classmethod
    def from_dict(cls, dict):
        condition = cls()

    @gen.coroutine
    def match_condition_secondary(self, algo):
        pass

    @gen.coroutine
    def match_condition_primary(self, algo):
        raise gen.Return(True)