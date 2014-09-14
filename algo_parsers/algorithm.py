import json

__author__ = 'guo'

class Algorithm:

    def __init__(self):
        self.algo_id = None
        self.algo_v = 0
        self.user_id = None
        self.stock_id = None
        self.algo_name = None
        self.price_condition = None
        self.kdj_condition = None

    def from_json(self, json_str):
        json_dict = json.loads(json_str)

