import pymongo
import datetime
from pymongo import MongoClient, errors
client = MongoClient()
db = client.ss
daily_collection = db.daily
kdj_933_collection = db.kdj_933


# algorithm 
# http://jingyan.baidu.com/article/e73e26c0ec3b3824adb6a70a.html
kdjArray = []

n = 9
m = 3
m1 = 3



OPEN = 0
HIGH = 1
LOW = 2
CLOSE = 3
VOLUME = 4
ADJ_CLOSE = 5

INFO_ELEMENTS = "e"

abbrevs = {"n":"name","c":"stock_code","d":"date"}

def shift(a,v,l):
	a.append(v)
	if len(a) > l: a.pop(0)


def calcRsv(vals):
	shift(n_low, vals[LOW], n)
	shift(n_high, vals[HIGH], n)
	denominator = (max(n_high) - min(n_low))
	if abs(denominator) < 0.000001:
		return m_rsv[-1]
	return (vals[CLOSE] - min(n_low))/denominator*100

def calcK(rsv):
	shift(m_rsv, rsv, m)
	return avg(m_rsv)

def calcD(k):
	shift(m1_k, k, m1)
	return avg(m1_k)

def avg(a):
	return float(sum(a))/len(a)

stock_list = open("../stock-list.txt")

for s in stock_list.readlines():
	if s[0] == "#": continue
	stock_number = s.strip().split()[1]

	n_low = []
	n_high = []
	m_rsv = []
	m1_k = []

	for stockInfo in daily_collection.find({"_id.c":stock_number},sort=[("_id.d",pymongo.ASCENDING)]):
		new_e = []
		for num in stockInfo[INFO_ELEMENTS]:
			new_e.append(float(num))
		new_e[VOLUME] = int(new_e[VOLUME])

		rsv = calcRsv(new_e)
		k = calcK(rsv)
		d = calcD(k)
		j = 3*k-2*d


		dat = stockInfo["_id"]["d"]

		# some dates are stored as string, conver to datetime
		if type(dat) != datetime.datetime:
			daily_collection.remove({"_id":stockInfo["_id"]})
			new_d = datetime.datetime.strptime(dat, "%Y-%m-%d")
			stockInfo["_id"]["d"] = new_d
			stockInfo[INFO_ELEMENTS] = new_e
			daily_collection.save(stockInfo)

		kdj_933_collection.save({"_id":stockInfo["_id"],"kd":k,"d":d,"j":j})

	print "finished", stock_number




