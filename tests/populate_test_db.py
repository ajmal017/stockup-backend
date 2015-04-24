from datetime import datetime
import os
import sys
import logging

import motor
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.options import options

here = os.path.dirname(os.path.abspath(__file__))
par_here = os.path.join(here, os.pardir)
if par_here not in sys.path:
    sys.path.append(par_here)


from config import datetime_repr, TEST_IPAD_TOKEN


def generate_stock_datapoint(
        stock_name="test_stock_name",
        opening_price=0,
        closing_price=0,
        cur_price=0,
        hi=0,
        lo=0,
        buy=0,
        sell=0,
        volume=0,
        date_str="1900-01-01",
        time_str="00:00:01"):

    return [stock_name, "%.2f" % opening_price, "%.2f" % closing_price, "%.2f" % cur_price, "%.2f" % hi, "%.2f" % lo, "%.2f" % buy, "%.2f" % sell, "%d" % volume, "%d" % (cur_price * volume), "52500", "10.70", "63800", "10.69", "35599", "10.68", "48325", "10.67", "104764", "10.66", "154876", "10.71", "374400", "10.72", "94596", "10.73", "253400", "10.74", "153500", "10.75", date_str, time_str, "00"]


@gen.coroutine
def populate_test_db():

    client = motor.MotorClient(options.dbhost)
    client.drop_database("ss_test")
    db = client.ss_test

    # price algo data
    times = ["2014-09-15T15:00:00", "2014-09-15T15:00:05", "2014-09-15T15:00:10", "2014-09-15T15:00:15"]
    inserts = db.stocks.initialize_ordered_bulk_op()
    prices = [11.90, 12.00, 12.05, 12.50]
    volume = 29580362

    for i in range(len(prices)):
        info = {
            "_id": {
                "c": 600100,
                "d": datetime.strptime(times[i], datetime_repr())
            },
            "d": generate_stock_datapoint(stock_name="price_test_algo", cur_price=prices[i], volume=volume)
        }
        print info
        inserts.insert(info)

    yield inserts.execute()
    print "done"
    return

    # kdj algo data
    dates = ["2015-04-08T00:00:00", "2015-04-07T00:00:00", "2015-04-06T00:00:00", "2015-04-03T00:00:00", "2015-04-02T00:00:00", "2015-04-01T00:00:00", "2015-03-31T00:00:00", "2015-03-30T00:00:00", "2015-03-27T00:00:00", "2015-03-26T00:00:00", "2015-03-25T00:00:00", "2015-03-24T00:00:00", "2015-03-23T00:00:00", "2015-03-20T00:00:00", "2015-03-19T00:00:00", "2015-03-18T00:00:00", "2015-03-17T00:00:00", "2015-03-16T00:00:00", "2015-03-13T00:00:00", "2015-03-12T00:00:00", "2015-03-11T00:00:00", "2015-03-10T00:00:00", "2015-03-09T00:00:00", "2015-03-06T00:00:00", "2015-03-05T00:00:00", "2015-03-04T00:00:00", "2015-03-03T00:00:00", "2015-03-02T00:00:00", "2015-02-27T00:00:00", "2015-02-26T00:00:00", "2015-02-25T00:00:00"]

    closings = ["16.93", "17.6", "17.08", "17.08", "16.83", "16.95", "16.41", "16.38", "16.17", "16", "16.57", "16.84", "16.47", "15.73", "15.64", "15.5", "15.25", "15.02", "14.44", "14.2", "14.18", "14.33", "14.33", "14.08", "14.29", "14.7", "14.62", "15.21", "15.08", "14.81", "14.61"]

    yield db.users.insert({"_id": "admin", "apns_tokens": [TEST_IPAD_TOKEN]})

    yield db.algos.insert([{
   "_id": {
"algo_v": 1,"algo_id": "price_match_algo_id"
   },  "algo_name": "match_algo",  "stock_id": 600100,  "user_id": "admin",  "price_type": "market",  "trade_method": "sell",  "volume": 100,  "primary_condition": "price_condition",  "conditions": {
"price_condition": {
    "price_type": "more_than",   "price": "12.00",   "window": "60"
}
   }
      }, {
   "_id": {
"algo_v": 1,"algo_id": "price_unmatch_algo_id"
   },  "algo_name": "unmatch_algo",  "stock_id": 600100,  "user_id": "admin",  "price_type": "market",  "trade_method": "sell",  "volume": 100,  "primary_condition": "price_condition",  "conditions": {
"price_condition": {
    "price_type": "more_than",   "price": "13.00",   "window": "60"
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
    logging.basicConfig()
    populate_test_db()
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
    IOLoop.instance().start()
