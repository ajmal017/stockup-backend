import datetime
from algo_parsers.Instruction import Instruction
from datetime import timedelta
from stock import StockDaily
from tornado import gen


def backtestkdj(n,m,m1,stockcode,starttime=None,endtime=None):
    #instruction = Instruction.from_json(algojson,)

    return  StockDaily.getkdj(starttime ,endtime,stockcode,n,m,m1)

def backtestmacd(n,m,m1,stockcode,starttime=None,endtime=None):
    #instruction = Instruction.from_json(algojson,)

    return  StockDaily.getmacd(starttime ,endtime,stockcode,n,m,m1)
