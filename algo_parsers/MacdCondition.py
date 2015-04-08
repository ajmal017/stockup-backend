#/*******************************************************************************
# * Last modified: 2015-3-26 22:02
# * Filename: macd.py
# * Description: 
#       EMA(12)=LastEMA(12)* 11/13 + Close * 2/13
#       EMA(26)=LastEMA(26)* 25/27 + Close * 2/27
#       
#       DIF=EMA(12)-EMA(26)
#       DEA=LastDEA * 8/10 + DIF * 2/10
#       MACD=(DIF-DEA) * 2
# * *****************************************************************************/
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import hashlib
import MySQLdb
import yaml
class MACD():
    def __init__(self):
        config = yaml.load(open('config.yml'))
        self.sleep_time = config['btcchina']['trade_option']['sleep_time']
        self.conn = MySQLdb.connect(host=config['database']['host'],user=config['database']['username'],passwd=config['database']['password'],db =config['database']['databasename'],charset=config['database']['encoding'] )
    def _getclose(self, num):
        read = self.conn.cursor()
        sql = "select close,time from ohlc order by id desc limit %s" % num
        count = read.execute(sql)
        results = read.fetchall()
        return results[::-1]
    def _ema(self, s, n):
        """
        returns an n period exponential moving average for
        the time series s
        s is a list ordered from oldest (index 0) to most
        recent (index -1)
        n is an integer
        returns a numeric array of the exponential
        moving average
        """
        if len(s) <= n:
            return "No enough item in %s" % s
        ema = []
        j = 1
        #get n sma first and calculate the next n period ema
        sma = sum(s[:n]) / n
        multiplier = 2 / float(1 + n)
        ema.append(sma)
        #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
        ema.append(( (s[n] - sma) * multiplier) + sma)
        #now calculate the rest of the values
        for i in s[n+1:]:
            tmp = ( (i - ema[j]) * multiplier) + ema[j]
            j = j + 1
            ema.append(tmp)
        return ema
    def getMACD(self, n):
        array = self._getclose(n)
        prices = map(lambda x: x[0], array)
        t = map(lambda x: int(time.mktime(x[1].timetuple())) * 1000, array)
        short_ema = self._ema(prices, 12)
        long_ema = self._ema(prices, 26)
        diff = map(lambda x: x[0]-x[1], zip(short_ema[::-1], long_ema[::-1]))
        diff.reverse()
        dea = self._ema(diff, 9)
        bar = map(lambda x: 2*(x[0]-x[1]), zip(diff[::-1], dea[::-1]))
        bar.reverse()
        return zip(t[33:], diff[8:]), zip(t[33:], dea), zip(t[33:], bar)
