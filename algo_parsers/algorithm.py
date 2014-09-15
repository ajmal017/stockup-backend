import json
import logging
import motor
from tornado import gen
from algo_parsers.KdjCondition import KdjCondition
from algo_parsers.PriceCondition import PriceCondition
from servers import config

__author__ = 'guo'
logger = logging.getLogger(__name__)

class Algorithm:
    db = motor.MotorClient().ss

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
        self.matched = False
        self.time = False

    @classmethod
    def from_json(cls, json_dict, time):
        algo = cls()
        algo.algo_name = json_dict["algo_name"]
        algo.algo_v = json_dict["algo_v"]
        algo.stock_id = json_dict["stock_id"]
        algo.user_id = json_dict["user_id"]
        algo.algo_id = json_dict["_id"]
        algo.price_type = json_dict["price_type"]
        algo.trade_method = json_dict["trade_method"]
        algo.volume = json_dict["volume"]
        algo.time = time
        algo.conditions = cls.conditions_from_dict(json_dict)
        print algo.conditions
        return algo

    @classmethod
    def conditions_from_dict(cls, condition_dict):
        conditions = {}
        for k, v in condition_dict["conditions"].iteritems():
            if k == "price_condition":
                conditions[k] = PriceCondition.from_dict(v)
            elif k == "kdj_condition":
                conditions[k] = KdjCondition.from_dict(v)

        conditions[condition_dict["primary_condition"]].is_primary = True
        return conditions

    @gen.coroutine
    def match(self):
        for condition in self.conditions.values():
            if ((yield condition.match_condition(self)) == False):
                raise gen.Return(False)

        raise gen.Return(True)

    @classmethod
    @gen.coroutine
    def parse_all(cls, time):
        algos = []
        cursor = cls.db.algos.find()

        for algo_json in (yield cursor.to_list(length=100)):
            algos.append(cls.from_json(algo_json, time))

        if config.DEBUG:
            logger.info("parsing algos " + str(len(algos)))

        algo_futures = []
        for algo in algos:
            algo_futures.append(algo.match())

        match_responses = yield algo_futures

        match_futures = []
        for i in range(len(match_responses)):
            if match_responses[i]:
                # algorithm matched
                match_futures.append(algos[i].process_match())

        match_responses = yield match_futures


    @gen.coroutine
    def process_match(self):
        print "matched " + self.algo_name
        #TODO: store in DB
        #TODO: send notification
        raise gen.Return(True)

        #TODO: if a notification/transaction failed, do something meaningful





