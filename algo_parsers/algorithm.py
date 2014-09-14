import json
from algo_parsers.ConditionFactory import ConditionFactory

__author__ = 'guo'

class Algorithm:

    def __init__(self):
        self.algo_id = None
        self.algo_v = 0
        self.user_id = None
        self.stock_id = None
        self.algo_name = None
        self.conditions = []

    @property
    def primary_condition(self):
        return self.conditions[0]

    @classmethod
    def from_json(cls, json_str):
        algo = cls()
        json_dict = json.loads(json_str)
        algo.algo_name = json_dict["algo_name"]
        algo.algo_v = json_dict["algo_v"]
        algo.stock_id = json_dict["stock_id"]
        algo.algo_id = json_dict["algo_id"]
        algo.conditions = ConditionFactory.conditions_from_dict(json_dict)





