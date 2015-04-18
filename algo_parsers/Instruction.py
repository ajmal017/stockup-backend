import logging

import motor
from tornado import gen

from algo_parsers.KdjCondition import KdjCondition
from algo_parsers.PriceCondition import PriceCondition
from algo_parsers.Apns_sender import ApnsSender
from config import debug_log
from tornado.options import options

__author__ = 'guo'
logger = logging.getLogger(__name__)
algos = []

class Instruction:
    db = motor.MotorClient(options.dbhost).ss_test

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
        self.period = None
        self.match_price = None  # price that matched

    @classmethod
    @gen.coroutine
    def loadall(cls,filter_query=None):
        cursor = Instruction.db.instructions.find(filter_query)

        '''
        find all the conditions of this user,then put them all into conditions{condition's name : condition}
        '''
        for algo_json in (yield cursor.to_list(1000)):
            algoinstance = cls.from_json(algo_json)
            algos.append(algoinstance)
            # debug_log(logger, "parsing algos %s "%algoinstance.algo_id)

    @classmethod
    def from_json(cls, json_dict, time=None):
        algo = cls()
        algo.algo_name = json_dict["algo_name"]
        algo.algo_v = json_dict["_id"]["algo_v"]
        algo.algo_id = json_dict["_id"]["algo_id"]
        algo.stock_id = int(json_dict["stock_id"])
        algo.user_id = json_dict["user_id"]
        algo.price_type = json_dict["price_type"]
        algo.trade_method = json_dict["trade_method"]
        algo.volume = json_dict["volume"]
        algo.period = int(json_dict["period"])
        algo.conditions = cls.conditions_from_dict(json_dict)
        return algo

    @classmethod
    def conditions_from_dict(cls, condition_dict):
        conditions = {}
        for k, v in condition_dict["conditions"].items():
            if not v:
                continue
            if k == "price_condition":
                conditions[k] = PriceCondition.from_dict(v)
            elif k == "kdj_condition":
                conditions[k] = KdjCondition.from_dict(v)
            
            conditions[k].db = Instruction.db
        
        conditions[condition_dict["primary_condition"]].is_primary = True
        return conditions

    @classmethod
    @gen.coroutine
    def parse_all(cls, time, filter_query=None):
        """

        :param time:
        :param filter_query: filter out a subset of messages
        :return:

        algos = []

        cursor = Instruction.db.instructions.find(filter_query)

        '''
        find all the conditions of this user,then put them all into conditions{condition's name : condition}
        '''
        for algo_json in (yield cursor.to_list(100)):
            algoinstance = cls.from_json(algo_json, time)
            algos.append(algoinstance)
            # debug_log(logger, "parsing algos %s "%algoinstance.algo_id)
        """

        debug_log(logger, "parsing algos " + str(len(algos)))
        algo_futures = []
        for algo in algos:
            algo_futures.append(algo.matchconditions(time))

        match_responses = yield algo_futures

        match_futures = []

        matches = []
        for i in range(len(match_responses)):
            if match_responses[i]:
                # algorithm matched
                debug_log(logger, "algorithm matched")
                matches.append(algos[i])
                match_futures.append(algos[i].process_match())

        yield match_futures

        raise gen.Return(matches)

    @gen.coroutine
    def matchconditions(self,time):
        yield [condition.match_condition(self,time) for condition in self.conditions.values()]
        for condition in self.conditions.values():
            if not condition.matched:
                raise gen.Return(False)
        raise gen.Return(True)

    @gen.coroutine
    def process_match(self):
        # save the match record for future reference
        match_id = yield Instruction.db.matches.insert(self.to_match_dict())

        # send a notification to the user
        user_dict = yield self.db.users.find_one({"_id": self.user_id}, {"apns_tokens": 1})

        for token in user_dict["apns_tokens"]:
            sent = yield ApnsSender.send(token, self.algo_name[:30] + " matched!", custom={"algo_id": str(match_id)})
            if not sent:
                pass
                # TODO: if a notification/transaction failed, do something meaningful

        raise gen.Return(True)


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
        json_dict["match_price"] = str(self.match_price)
        return json_dict
