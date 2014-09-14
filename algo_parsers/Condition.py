from datetime import datetime


class Condition:

    def __init__(self):
        self.stock = None
        self.ts = datetime.now()
        self.is_primary = True

    @classmethod
    def from_dict(cls, dict):
        return None

    def match_condition(self, ts):
        self.ts = ts
        if  self.is_primary:
            return self.match_condition_primary()
        else:
            return self.match_condition_secondary()

    def match_condition_secondary(self):
        return False

    def match_condition_primary(self):
        return False
