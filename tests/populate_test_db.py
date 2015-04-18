from datetime import datetime
import os
import sys
import random

import motor
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.options import options

here = os.path.dirname(os.path.abspath(__file__))
par_here = os.path.join(here, os.pardir)
if par_here not in sys.path:
    sys.path.append(par_here)

from config import datetime_repr, TEST_IPAD_TOKEN


@gen.coroutine
def populate_test_db():
    client = motor.MotorClient(options.dbhost)
    #client.drop_database("ss_test")
    db = client.ss_test

    curPrice = 12.05
    times = [
        "2015-03-31T15:00:00",
        "2015-03-31T15:00:05",
        "2015-03-31T15:00:10",
        "2015-03-31T15:00:15",
        ]
    inserts = []
    prices = [12.40,12.40,12.25,12.40]
    for i in range(len(prices)):
        lastPrice = curPrice
        curPrice = prices[i]  #*= (random.gauss(0.005,0.01) + 1)
        volume = 29580362
        info = {
            "_id": {
                "c": 600100,
                "d": datetime.strptime(times[i], datetime_repr())
            },
            "d": [
                "test_stock",
                "10.66",
                "10.72",
                "%.2f" % curPrice,
                "10.84",
                "10.65",
                "10.70",
                "10.71",
                "%d" % volume,
                "%d" % volume,
                "52500",
                "10.70",
                "63800",
                "10.69",
                "35599",
                "10.68",
                "48325",
                "10.67",
                "104764",
                "10.66",
                "154876",
                "10.71",
                "374400",
                "10.72",
                "94596",
                "10.73",
                "253400",
                "10.74",
                "153500",
                "10.75",
                "2014-09-15",
                "15:03:03",
                "00"
            ]
        }

        inserts.append(db.stocks_second.insert(info))

    yield inserts

    yield db.users.insert({ "_id" : "admin", "apns_tokens" : [ TEST_IPAD_TOKEN ] })

    yield db.instructions.insert([{
                               "_id": {
                                   "algo_v": 1,
                                   "algo_id": "price_match_algo_id"
                               },
                               "algo_name": "match_algo",
                               "price_type": "market",
                               "trade_method": "sell",
                               "stock_id": 600006,
                                "user_id": "admin",
                               "volume": 100,
                               "period":1,
                               "primary_condition": "price_condition",
                               "conditions": {
                                   "price_condition": {
                                       "price_type": "more_than",
                                       "price": "12.30",
                                       "window": "60"
                                   }
                               }
                           }, {
                               "_id": {
                                   "algo_v": 1,
                                   "algo_id": "price_unmatch_algo_id"
                               },
                               "algo_name": "unmatch_algo",
                               "stock_id": 600006,
                               "user_id": "admin",
                               "price_type": "market",
                               "trade_method": "sell",
                               "volume": 100,
                               "period":1,
                               "primary_condition": "price_condition",
                               "conditions": {
                                   "price_condition": {
                                       "price_type": "more_than",
                                       "price": "13.00",
                                       "window": "60"
                                   }
                               }
                           }])

    yield db.instructions.insert([{
                               "_id": {
                                   "algo_v": 1,
                                   "algo_id": "kdj_match_algo_id"
                               },
                               "algo_name": "match_algo",
                               "stock_id": 600006,
                               "user_id": "admin",
                               "price_type": "market",
                               "trade_method": "sell",
                               "volume": 100,
                               "period":1,
                               "primary_condition": "kdj_condition",
                               "conditions": {
                                   "kdj_condition": {
                                       "n": 9,
                                       "m": 3,
                                       "m1": 3,
                                       "window": "60"
                                   }
                               }
                           }, {
                               "_id": {
                                   "algo_v": 1,
                                   "algo_id": "kdj_unmatch_algo_id"
                               },
                               "algo_name": "unmatch_algo",
                               "stock_id": 600006,
                               "user_id": "admin",
                               "price_type": "market",
                               "trade_method": "sell",
                               "volume": 100,
                               "period": 1,
                               "primary_condition": "kdj_condition",
                               "conditions": {
                                   "kdj_condition": {
                                       "n": 9,
                                       "m": 1,
                                       "m1": 1,
                                       "window": "60"
                                   }
                               }
                           }])

    print("done")
    IOLoop.current().stop()


def main():
    populate_test_db()


if __name__ == "__main__":
    main()
    IOLoop.instance().start()
