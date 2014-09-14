from algo_parsers.Condition import Condition


class PriceCondition(Condition):

    def match_condition_primary(self):
        return False

    def match_condition_secondary(self):
        return False

