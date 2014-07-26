from pymongo import MongoClient
import urllib2
client = MongoClient()

db = client.ss
daily_info = db.daily

base_url = "http://table.finance.yahoo.com/table.csv?s=%s.ss"

stock_list = open("../stock-list.txt")

maps = {0:"open",1:"high",2:"low",3:"close",4:"volume",5:"adj_close"}
abbrevs = {"n":"name","c":"stock_code","d":"date"}
for line in stock_list.readlines():
	if line[0] == "#": continue
	line = line.strip().split()
	stock_number = line[1]
	full_url = base_url%stock_number
	print full_url
	content = urllib2.urlopen(full_url)

	firstLine = True;

	for line in content.readlines():
		if firstLine:
			# first line is title
			firstLine = False
			continue
		elements = line.strip().split(",")
		id_doc = {"c":stock_number,"d":elements[0]}
		daily_info.insert({"_id":id_doc,"e":elements[1:]}) 
