#!/usr/bin/python3

import httplib2
from bs4 import BeautifulSoup
import re
import time
import pickle
import requests

all_eos = ['http://www.cisco.com/c/en/us/products/collateral/switches/mgx-8850-software/prod_end-of-life_notice0900aecd80235165.html']
data ={}
for eos in all_eos:
	while True:
			try:
				content = requests.get(eos,timeout=10)
			except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
				print ("Error. Repeat")
				error_log.write('url_timeout' + page+'\t')
			else:
				break

	soup = BeautifulSoup(content.text) 

	tables = soup.findAll("table")

	arr_tables = []

	for table in tables:
		arr_table = []
		rows = table.findAll('tr')
		for row in rows:
			cols = row.findAll('td')
			cols = [ele.text.strip() for ele in cols]
			arr_table.append(cols)
		arr_tables.append(arr_table)

	dates = arr_tables[0]
	devices = arr_tables[1]
	pns = [device[0].replace(" ", "").replace('\n','') for device in devices]
	pns.pop(0)
	dates.pop(0)

	print(dates)