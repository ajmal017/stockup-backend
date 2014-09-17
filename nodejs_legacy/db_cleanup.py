from pymongo import MongoClient

client = MongoClient()

db = client.ss

daily = db.daily
kdj = db.kdj_933


def shorten_id(stock_number):
    for f in daily.find({"_id.c":stock_number}):
        old_id = f["_id"]
        new_id = old_id
        new_id["c"] = int(new_id["c"])

        daily.remove({"_id":old_id})
        f["_id"] = new_id
        daily.save(f)

def change_k_key(stock_number):
    for f in kdj.find({"_id.c":str(stock_number)}):
        daily.remove({"_id":f["_id"]})
        f["_id"]["c"] = int(f["_id"]["c"])

        if "kd" in f.keys():
            f["k"] = f["kd"]
            f.pop("kd")
        daily.save(f)

stock_list = open("stock-list.txt")
for s in stock_list.readlines():
    if s[0] == "#": continue
    stock_number = s.strip().split()[1]
    change_k_key(stock_number)
    print "finished", stock_number

