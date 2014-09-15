from datetime import datetime
from tornado import gen


class Condition:


    def __init__(self):
        self.is_primary = False
        self.window = 0


    @classmethod
    def from_dict(cls, dict):
        return None

    @gen.coroutine
    def match_condition(self, algo):
        if self.is_primary:
            yield self.match_condition_primary(algo)
        else:
            yield self.match_condition_secondary(algo)

    @gen.coroutine
    def match_condition_secondary(self, algo):
        raise gen.Return(False)

    @gen.coroutine
    def match_condition_primary(self, algo):
        raise gen.Return(False)
