import urllib
import datetime

from pymongo import MongoClient, errors


client = MongoClient('119.29.16.193')
db = client.ss_test
daily = db.daily
base_url = "http://ichart.finance.yahoo.com/table.csv?s=%s.ss&a=4&b=7&c=2014&g=d&d=4&e=7&f=2015&iggnore=.csv"
stock_list = open("../stock-list.txt")
maps = {0: "open", 1: "high", 2: "low", 3: "close", 4: "volume", 5: "adj_close"}
abbrevs = {"n": "name", "c": "stock_code", "d": "date"}
lllll=stock_list.readlines()

'''sample data:
Date,Open,High,Low,Close,Volume,Adj Close
2015-04-07,59.44,59.44,57.19,57.92,17042900,57.92
2015-04-06,58.78,58.78,58.78,58.78,000,58.78
2015-04-03,55.91,59.90,55.50,58.78,23507300,58.78
2015-04-02,56.50,56.95,55.01,55.87,14876800,55.87
2015-04-01,55.45,56.99,54.35,56.23,14184700,56.23
2015-03-31,58.80,59.50,54.88,55.38,30234900,55.38
2015-03-30,53.35,57.58,52.40,57.21,28484300,57.21
2015-03-27,52.00,53.49,50.27,52.39,14977200,52.39
'''

for line in lllll:
    if line[0] == "#": continue
    line = line.strip()#.split()
    stock_number = line[2:]
    full_url = base_url % stock_number
    print full_url
    try:
        content = urllib.urlopen(full_url)
    except Exception,e:
        print "######"
        print "error reading HTTP"
        print e
        continue

    firstLine = True;

    all_elements = []
    for line in content.readlines():
        if firstLine:
            # first line is title
            firstLine = False
            continue
        elements = line.strip().split(",")
        new_d = datetime.datetime.strptime(elements[0], "%Y-%m-%d")
        id_doc = {"c": int(stock_number), "d": new_d}
        new_e = []
        for el in elements[1:]:
            new_e.append(float(el))
        new_e[4] = int(new_e[4])
        all_elements.append({"_id": id_doc, "e": new_e})

    try:
        daily.insert(all_elements)
    except errors.DuplicateKeyError:
        print "duplicate key error", stock_number

    print "saved", stock_number


