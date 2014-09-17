import logging

import motor
from tornado import gen

from algo_parsers.KdjCondition import KdjCondition
from algo_parsers.PriceCondition import PriceCondition
from config import debug_log


__author__ = 'guo'
logger = logging.getLogger(__name__)


class Algorithm:
    db = motor.MotorClient().stocks

    @classmethod
    def from_json(cls, json_dict, time):
        algo = cls()
        algo.algo_name = json_dict["algo_name"]
        algo.algo_v = json_dict["_id"]["algo_v"]
        algo.algo_id = json_dict["_id"]["algo_id"]
        algo.stock_id = json_dict["stock_id"]
        algo.user_id = json_dict["user_id"]
        algo.price_type = json_dict["price_type"]
        algo.trade_method = json_dict["trade_method"]
        algo.volume = json_dict["volume"]
        algo.time = time
        algo.conditions = cls.conditions_from_dict(json_dict)
        return algo

    @classmethod
    def conditions_from_dict(cls, condition_dict):
        conditions = {}
        for k, v in condition_dict["conditions"].iteritems():
            if k == "price_condition":
                conditions[k] = PriceCondition.from_dict(v)
            elif k == "kdj_condition":
                conditions[k] = KdjCondition.from_dict(v)
            conditions[k].db = Algorithm.db

        conditions[condition_dict["primary_condition"]].is_primary = True
        return conditions

    @classmethod
    @gen.coroutine
    def parse_all(cls, time):
        algos = []

        cursor = Algorithm.db.algos.find()

        for algo_json in (yield cursor.to_list(100)):
            algos.append(cls.from_json(algo_json, time))

        debug_log(logger, "parsing algos " + str(len(algos)))

        algo_futures = []
        for algo in algos:
            algo_futures.append(algo.match())

        match_responses = yield algo_futures

        match_futures = []

        matches = []
        for i in range(len(match_responses)):
            if match_responses[i]:
                # algorithm matched
                debug_log(logger, "algorithm matched")
                matches.append(algos[i])
                match_futures.append(algos[i].process_match())

        match_responses = yield match_futures

        raise gen.Return(matches)

    def __init__(self):
        self.algo_id = None
        self.algo_v = 0
        self.user_id = None
        self.stock_id = None
        self.algo_name = None
        self.price_type = None
        self.trade_method = None
        self.volume = None
        self.conditions = None
        self.time = None

    def to_match_dict(self):
        """
        Creates a match reference in the matches collection

        :return: the match reference
        """
        json_dict = dict()
        json_dict["algo_v"] = self.algo_v
        json_dict["stock_id"] = self.stock_id
        json_dict["user_id"] = self.user_id
        json_dict["algo_id"] = self.algo_id
        json_dict["price_type"] = self.price_type
        json_dict["trade_method"] = self.trade_method
        json_dict["volume"] = self.volume
        json_dict["time"] = self.time
        return json_dict

    @gen.coroutine
    def match(self):
        for condition in self.conditions.values():

            if not (yield condition.match_condition(self)):
                raise gen.Return(False)
        raise gen.Return(True)

    @gen.coroutine
    def process_match(self):
        # save the match record for future reference
        yield Algorithm.db.matches.insert(self.to_match_dict())

        # apns_sender.send()
        # TODO: if a notification/transaction failed, do something meaningful
        raise gen.Return(True)
