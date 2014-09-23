from tornado import gen


class Condition:
    def __init__(self):
        self.is_primary = False
        self.window = 0
        self.db = None
        self.matched = False

    @classmethod
    def from_dict(cls, dict):
        return None

    @gen.coroutine
    def match_condition(self, algo):
        if self.is_primary:
            yield self.match_condition_primary(algo)
        else:
            yield self.match_condition_secondary(algo)

    def match_condition_secondary(self, algo):
        raise Exception("not implemented in child class")

    def match_condition_primary(self, algo):
        raise Exception("not implemented in child class")
