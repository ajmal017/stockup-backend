import json

__author__ = 'guo'

class Algorithm:

    def __init__(self):
        self.description = "algorithm"

    def from_json(self, json_str):
        json_dict = json.loads(json_str)
