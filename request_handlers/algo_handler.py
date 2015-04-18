#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import json
from tornado import gen
from tornado.web import authenticated
from urllib import parse
from tests import backtest
from request_handlers.base_request_handler import BaseRequestHandler


class AlgoHandler(BaseRequestHandler):

    @authenticated
    @gen.coroutine
    def post(self, action=None):
        if action == 'upload':
            yield self.post_upload()
        elif action == 'remove':
            yield self.post_remove()
        else:
            self.write_error(404)

    @gen.coroutine
    def post_remove(self):

        body = json.loads(self.request.body)
        algo_data_raw = body["algo"]
        #value =  urlparse.parse_qs(algo_data_raw)
        algo_data = (algo_data_raw)

        query = {"_id.algo_id": algo_data["algo_id"]}

        #if self.get_argument("test", None):
        if "test" in body:
            yield self.settings["test_db"].algos.remove(query)
        else:
            yield self.settings["db"].algos.remove(query)
        self.write({"removed": algo_data["algo_id"]})

    @gen.coroutine
    def post_upload(self):

        str_body = self.request.body.decode()
        body = json.loads(str_body)

        '''
        _data = body["data"]

        _id = {"algo_id": algo_data["algo_id"], "algo_v": algo_data["algo_v"]}
        algo_data["_id"] = _id

        del algo_data["algo_id"]
        del algo_data["algo_v"]
        '''
        if "test" in body:
            db = self.settings["test_db"]
            yield db.algos.save(body)
        else:
            yield self.settings["db"].algos.save(body)

        self.write({"saved": body["_id"]["algo_id"]})

    @authenticated
    @gen.coroutine
    def get(self, action=None):
        if action == "list":
            user_id = self.get_argument("user_id", None)

            if self.get_argument("test", None):
                db = self.settings["test_db"]
                cursor = db.algos.find(
                    {"user_id": user_id})
            else:
                cursor = self.settings["db"].algos.find({"user_id": user_id})

            algos = []
            list = yield cursor.to_list(100)
            for algo in (list):
                algos.append(algo)

            self.write({"algos": algos})
        else:
            self.write_error(404)
