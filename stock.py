import pymongo
import motor
from tornado.options import options
from tornado import gen
import time
import datetime
dd=49.65
kk=51.89
stock_dict = {}
cur_totalmoney = 10000
beginmoney = cur_totalmoney
cur_stocknum   = 0
class StockDaily:
    db = motor.MotorClient(options.dbhost).ss_test

    def __init__(self):
        self.kk=42.36

    @classmethod
    def loaddailystockfromdb(self, start,end ,stockcode):
        stock_dict  =   {}
        find_query = {
            "_id.d": {"$gte": start},
            "_id.d": {"$lte":end},
            "_id.c": stockcode
        }

        sort_query = [("_id.d", pymongo.ASCENDING)]
        cursor = self.db.stocks_daily.find(find_query,sort = sort_query)
        return cursor

    @classmethod
    def getRSV(self, stock_list , param1):
        rsv = []
        times = []
        timestr = []
        closelist = []
        begin = int(0)
        while begin+param1 < len(stock_list):
            high = max(map(lambda x: x['e'][2], stock_list[begin:begin+param1]))
            low = min(map(lambda x: x['e'][3], stock_list[begin:begin+param1]))
            close = stock_list[begin+param1-1]['e'][4]
            volume = stock_list[begin+param1-1]['e'][5]

            if 0 == high-low:
                high = high+0.1
            elif 0 == volume:
                begin += 1
                continue
 
            value = (close-low)/(high-low)*100
            rsv.append( value )
            closelist.append(close)
            print(begin)
            print(stock_list[begin:begin+param1])
            print(high)
            print(low)
            print(close)
            print(value)
            print(stock_list[begin+param1-1]["_id"]["d"]) 
            t = int(time.mktime(stock_list[begin+param1-1]["_id"]["d"].timetuple())) * 1000
            times.append(t)
            timestr.append(stock_list[begin+param1-1]["_id"]["d"])
            begin += 1
        return times,rsv,closelist,timestr

    @classmethod
    def _avg(self, a):
        length = len(a)
        return sum(a) / length

    @classmethod
    def getK(self, values, window):
        array =[]
        begin = 0
        global kk
        while begin+window < len(values):
            #average = self._avg(values[begin:begin+window])
            rsv     = values[begin]
            print("rsv%f :"%rsv)
            print("kk%f:"%kk)
            print("window:%d"%window)
            curmb   = (rsv+(window-1)*kk)/window
            print("curmb:%f"%curmb) 
            kk = curmb
            array.append(curmb )
            begin += 1
        return array
  
    @classmethod
    def getD(self, values, window):
        array =[]
        begin = 0
        global dd
        while begin+window < len(values):
            #average = self._avg(values[begin:begin+window])
            rsv     = values[begin]
            print("rsv%f :"%rsv)
            print("kk%f:"%dd)
            print("window:%d"%window)
            curmb   = (rsv+(window-1)*dd)/window
            print("curmb:%f"%curmb) 
            dd = curmb
            array.append(curmb )
            begin += 1
        return array


    @classmethod
    def is_match(self, prev_k, prev_d, curr_k, curr_d):
        if prev_d <= prev_k and curr_d > curr_k:
                return 'sell'

        if prev_k <= prev_d and curr_k > curr_d:
                return 'buy'

        return ''

    @classmethod
    def cacl(self,k,d,c,timestr):
        begin = 4
        global cur_stocknum,beginmoney,cur_totalmoney
        
        while begin < len(d):
          lenk = len(k)
          lenb = len(d)
          print("begin:%d"%begin)
          print("lenk:%d"%lenk)
          print("lenb:%d"%lenb)
          curr_k = k[begin]
          curr_d = d[begin]
          prev_k = k[begin-1]
          prev_d = d[begin-1]
          cur_price = c[begin]
          match = self.is_match(prev_k, prev_d, curr_k, curr_d)
          
          if 'buy'== match:      
             buynum = int(cur_totalmoney/cur_price)
             cur_stocknum = cur_stocknum + buynum
             print("buy%d"%buynum)
             cur_totalmoney = cur_totalmoney - cur_stocknum*cur_price  
          elif 'sell' == match:
             gainmoney    = cur_stocknum*cur_price
             prev_totalmoney = cur_totalmoney
             cur_totalmoney = cur_totalmoney +gainmoney
             cur_stocknum = 0 
             print("buy%d"%cur_stocknum)
             rate2 = gainmoney/prev_totalmoney
             
             rate1 = cur_totalmoney/beginmoney-1
             print("sell%d:"%cur_stocknum)
             print("cur_totalmoney%d"%cur_totalmoney)
             print("prev_totalmoney%d"%prev_totalmoney)
             print("gainmoney%d"%gainmoney)
             print("rate: %f "%rate1)
             print("rate: %f "%rate2)
             print(timestr[begin+3])
          begin = begin +1
        
        return

    @classmethod
    @gen.coroutine
    def getkdj(self,starttime,endtime,stock_id,n,m,m1):
        cursor = self.loaddailystockfromdb(starttime ,endtime,stock_id)
        
        stocklist = yield cursor.to_list(1000)
        i = 0 
        length = len(stocklist)
        while i < length:
            if stocklist[i]['e'][5] == 0:
               print("volume is 0")
               del stocklist[i]
               i=0
               length = len(stocklist)
            i+=1

        times ,rsv,c,timestr = self.getRSV(stocklist,n)
        k   = self.getK(rsv,m)
        d   = self.getD(k,m1)
        j   = list(map(lambda x: 3*x[0]-2*x[1], zip(k[3:], d)))
        #k.extend([7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6])
        #d.extend([-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0])
        
        print(list(zip(timestr,k)))
        print("\n")
        print(list(zip(timestr,d)))
        print("\n")
        print(j)
        print("\n")
        self.cacl(k,d,c,timestr)
        raise gen.Return([list(zip(times,k)),list(zip(times,d)),list(zip(times,j))])
 
    @classmethod
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

    @classmethod
    @gen.coroutine
    def getmacd(self, starttime,endtime,stock_id,n,m,m1):
        cursor = self.loaddailystockfromdb(starttime ,endtime,stock_id)
        array = yield cursor.to_list(1000)
        for i in range(len(array)):
            if array[i]['e'][5] == 0:
               print("volume is 0")
               del array[i]
               

        prices = list(map(lambda x: x['e'][0], array))
        #t = list(map(lambda x: int(time.mktime(x['e'][1].timetuple())) * 1000, array))
        short_ema = self._ema(prices, 12)
        long_ema = self._ema(prices, 26)
        diff = list(map(lambda x: x[0]-x[1], zip(short_ema[::-1], long_ema[::-1])))
        diff.reverse()
        dea = self._ema(diff, 9)
        bar = list(map(lambda x: 2*(x[0]-x[1]), zip(diff[::-1], dea[::-1])))
        bar.reverse()

        raise gen.Return([  diff[8:] ,  dea , bar ])


