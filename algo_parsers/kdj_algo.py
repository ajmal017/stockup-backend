import pymongo
from pymongo import MongoClient

client = MongoClient()
db = client.ss

kdj_933_collection = db.kdj_933
daily_collection = db.daily

kdjVals = []
buyPoints = []
sellPoints = []

buyDates = []
sellDates = []

d_upper = 0
d_lower = 100

curIndex = 0


def algo():
    global curIndex
    while curIndex < len(kdjVals):
        find_next_buy()
        curIndex += 1
        if curIndex < len(kdjVals):
            find_next_sell()
            curIndex += 1
        else:
            break;


def find_next_buy():
    global curIndex
    k_on_top = True
    while curIndex < len(kdjVals):
        curVal = kdjVals[curIndex]
        k = "kd"
        if "kd" not in curVal.keys(): k = "k"
        k = curVal[k]
        d = curVal["d"]
        if (not k_on_top) and k > d and d < d_lower:
            price = _get_close_price(curVal["_id"])
            buyPoints.append(float(price))
            buyDates.append(curVal["_id"]["d"])
            break
        k_on_top = (k >= d)
        curIndex += 1


def find_next_sell():
    global curIndex
    k_on_top = False
    while curIndex < len(kdjVals):
        curVal = kdjVals[curIndex]
        k = "kd"
        if "kd" not in curVal.keys(): k = "k"
        k = curVal[k]
        d = curVal["d"]
        if k_on_top and k < d and d > d_upper:
            # D passed K, should sell
            price = _get_close_price(curVal["_id"])
            sellPoints.append(float(price))
            sellDates.append(curVal["_id"]["d"])
            break
        k_on_top = (k < d)
        curIndex += 1


def _get_close_price(_id):
    prices = daily_collection.find_one({"_id": _id})
    return prices["e"][3]


stock_number = "600601"

for stockInfo in kdj_933_collection.find({"_id.c": stock_number}, sort=[("id.d", pymongo.ASCENDING)]):
    kdjVals.append(stockInfo)

algo()

s = 0
for i in range(3, len(sellPoints)):
    print buyPoints[i], ",", buyDates[i], ",", sellPoints[i], ",", sellDates[i]
    s = sellPoints[i] - buyPoints[i]
print s
