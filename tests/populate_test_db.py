from datetime import datetime
import os
import sys

import motor
from tornado import gen
from tornado.ioloop import IOLoop


here = os.path.dirname(os.path.abspath(__file__))
par_here = os.path.join(here, os.pardir)
if par_here not in sys.path:
    sys.path.append(par_here)

from config import datetime_repr, TEST_IPAD_TOKEN


@gen.coroutine
def populate_test_db():
    client = motor.MotorClient()
    client.drop_database("ss_test")
    db = client.ss_test

    prices = ["10.05", "11.05", "12.05", "13.05"]
    times = [
        "2014-09-15T15:00:00",
        "2014-09-15T15:00:05",
        "2014-09-15T15:00:10",
        "2014-09-15T15:00:15",
        ]
    inserts = []

    for i in range(len(prices)):
        info = {
            "_id": {
                "c": 600100,
                "d": datetime.strptime(times[i], datetime_repr())
            },
            "d": [
                "test_stock",
                "10.66",
                "10.72",
                prices[i],
                "10.84",
                "10.65",
                "10.70",
                "10.71",
                "29580362",
                "316949714",
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

        inserts.append(db.stocks.insert(info))

    yield inserts

    yield db.users.insert({ "_id" : "admin", "apns_tokens" : [ TEST_IPAD_TOKEN ] })

    yield db.algos.insert([{
                               "_id": {
                                   "algo_v": 1,
                                   "algo_id": "match_algo_id"
                               },
                               "algo_name": "match_algo",
                               "stock_id": 600100,
                               "user_id": "admin",
                               "price_type": "market",
                               "trade_method": "sell",
                               "volume": 100,
                               "primary_condition": "price_condition",
                               "conditions": {
                                   "price_condition": {
                                       "price_type": "more_than",
                                       "price": "12.00",
                                       "window": "60"
                                   }
                               }
                           }, {
                               "_id": {
                                   "algo_v": 1,
                                   "algo_id": "unmatch_algo_id"
                               },
                               "algo_name": "unmatch_algo",
                               "stock_id": 600100,
                               "user_id": "admin",
                               "price_type": "market",
                               "trade_method": "sell",
                               "volume": 100,
                               "primary_condition": "price_condition",
                               "conditions": {
                                   "price_condition": {
                                       "price_type": "more_than",
                                       "price": "13.00",
                                       "window": "60"
                                   }
                               }
                           }])

    print "done"
    IOLoop.current().stop()


def main():
    populate_test_db()


if __name__ == "__main__":
    populate_test_db()
    IOLoop.instance().start()
