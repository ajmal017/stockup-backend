from pymongo import MongoClient, errors
import urllib2
import datetime
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
	try:
		content = urllib2.urlopen(full_url)
	except urllib2.HTTPError:
		print "######"
		print "error reading HTTP"
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
		id_doc = {"c":int(stock_number),"d":new_d}
		new_e = []
		for el in elements[1:]:
			new_e.append(float(el))
		new_e[4] = int(new_e[4])
		all_elements.append({"_id":id_doc,"e":new_e})

	try:
		daily_info.insert(all_elements) 
	except errors.DuplicateKeyError:
		print "duplicate key error", stock_number

	print "saved",stock_number


