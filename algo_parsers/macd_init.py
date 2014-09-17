from collections import deque

import pymongo
from pymongo import MongoClient

client = MongoClient()
db = client.ss
daily_collection = db.daily
macd_collection  = db.macd

# algorithm 
# http://en.wikipedia.org/wiki/MACD
# http://wiki.mbalib.com/wiki/%E5%B9%B3%E6%BB%91%E5%BC%82%E5%90%8C%E7%A7%BB%E5%8A%A8%E5%B9%B3%E5%9D%87%E7%BA%BF
# 12, 26, 9
# so far the script is wrong
n1 = 12
n2 = 26
n3 = 9

INFO_ELEMENTS = "e"
L_n1 = float(2) / (  n1 + 1) # 2 / (12+1)
L_n2 =  float(2) / (  n2 + 1) # 2 / (26+1)

OPEN = 0
HIGH = 1
LOW = 2
CLOSE = 3
VOLUME = 4
ADJ_CLOSE = 5


abbrevs = {"n":"name","c":"stock_code","d":"date"}

stock_list = open("../stock-list.txt")
def shift(a,v,l):
    a.append(v)
    if len(a) > l:
        a.popleft()

#first day EMA is DI
def calcEMA(vals, n):

    #since n2 is always a larger number

    #DI = high + close + 2 * low
    if n == n1 and len(n_ema_n1) == 0 :
        ema_daily = (n_end[0] + n_high[0] + 2 * n_low[0]) / 4
        n_ema_n1.append(ema_daily)
        return ema_daily
    elif n == n2 and len(n_ema_n2) == 0 :
        ema_daily = (n_end[0] + n_high[0] + 2 * n_low[0]) / 4
        n_ema_n2.append(ema_daily)
        return ema_daily

    if n == n1:
        ema_daily = L_n1 * n_end[len(n_end)-1] + (n1 - 1) / (n1 + 1) * float(n_ema_n1[len(n_ema_n1)-1]) + n_end[len(n_end)-2]
        shift(n_ema_n1, ema_daily, n1)
    elif (n == n2) :
        ema_daily = L_n2 * n_end[len(n_end)-1] + (n2 - 1) / (n2 + 1) * float(n_ema_n2[len(n_ema_n2)-1]) + n_end[len(n_end)-2]
        shift(n_ema_n2, ema_daily, n2)
    else :
        print "data point wrong!"
        return -1
    return ema_daily

def calcDIF(ema_n1, ema_n2):
    dif_daily = ema_n1 - ema_n2
    shift(n_dif, dif_daily, n2)
    return dif_daily

def calcSignal(dif):
    signal_daily = 0
    if len(n_signal) == 0:
        signal_daily = n_dif[0]
        shift(n_signal, signal_daily, n2)
    else:
        signal_daily = 0.2 * dif + 0.8 * float(n_signal[len(n_signal)-1])
        shift(n_signal, signal_daily, n2)

    return signal_daily

for s in stock_list.readlines():
    if s[0] == "#": continue
    stock_number = s.strip().split()[1]

    #for preparing the
    n_low = deque()
    n_high = deque()
    n_end = deque()
    n_ema_n1 = deque()
    n_ema_n2 = deque()
    n_dif = deque()
    n_signal = deque()
    # n_di = deque()
    #for calculating DIF and DEA

    #calculating
    to_insert = []
    count = 0
    for stockInfo in daily_collection.find({"_id.c":int(stock_number)}, sort=[("_id.d",pymongo.ASCENDING)]):
        count += 1
        shift(n_low, stockInfo[INFO_ELEMENTS][LOW], n2)
        shift(n_high, stockInfo[INFO_ELEMENTS][HIGH], n2)
        shift(n_end, stockInfo[INFO_ELEMENTS][CLOSE], n2)
        ema_n1 = calcEMA(stockInfo[INFO_ELEMENTS], n1)
        print ema_n1
        ema_n2 = calcEMA(stockInfo[INFO_ELEMENTS], n2)
        print ema_n2

        dif = calcDIF(ema_n1, ema_n2)
        print dif
        signal = calcSignal(dif)
        print signal
        print "stock number: "
        print stock_number
        s =  str(ema_n1) + " " + str(ema_n2) + " " + str(dif) + " " + str(signal)
        print s
        print "\n"
        #if count == 2:
            #sys.exit()