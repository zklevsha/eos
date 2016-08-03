#!/usr/bin/python3
from bs4 import BeautifulSoup
import re
import time
import pickle
import requests
from dateutil.parser import parse

error_log = open('parse_error_log', 'w')

all_eos = pickle.load(open("eos.p",'rb'))
data ={}
for eos in all_eos:
	eos = "https://cisco.com"+eos
	print ("Checking " + eos)
	while True:
			try:
				content = requests.get(eos,timeout=10)
			except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
				print ("Error. Repeat")
				error_log.write('url_timeout' + eos+'\t')
			else:
				break

	soup = BeautifulSoup(content.text,"html.parser") 

	tables = soup.findAll("table")
	document_date = soup.find("div",{"class":"updatedDate"})
	if document_date is None:
		document_date = parse ("jun 1 100")
	else:
		document_date = parse(document_date.text.replace("Updated:",""))

	arr_tables = []
	devices = []

	for table in tables:
		arr_table = []
		rows = table.findAll('tr')
		for row in rows:
			cols = row.findAll('td')
			cols = [ele.text.strip() for ele in cols]
			arr_table.append(cols)
		arr_tables.append(arr_table)

	
	for table in arr_tables:
		try:
			header = " ".join(table[0])
		except(IndexError):
			continue

		if "Number" in header:
			devices = [row[0] for row in table ]

	if len(devices) == 0:
		print("Cant find table with devices")
		error_log.write("Cant find table with devices\n")
		error_log.write("url: " + eos + "\n")
		error_log.write("\n")
		continue


	pns = [device.replace(" ", "").replace('\n','') for device in devices]
	pns.pop(0)
	
	try:
		print (pns)
		print (document_date)

	except UnicodeEncodeError:
		print("Cant print pns - there some not printable characters ")

	print("")

	for pn in pns:
		if pn in data and eos not in data[pn]['url']:
			if(document_date > data[pn]['url']['date']):
				data[pn]['url'] = {'link':eos,'date':document_date}
		else:
			data[pn]={}
			data[pn]['url'] = {'link':eos,'date':document_date} 

pickle.dump(data,open('data.p','wb'))
