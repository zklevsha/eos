#!/usr/bin/python3

import httplib2
from bs4 import BeautifulSoup
import re
import time
import pickle
import requests

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
				error_log.write('url_timeout' + page+'\t')
			else:
				break

	soup = BeautifulSoup(content.text,"html.parser") 

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

	dates = []
	devices = []
	for table in arr_tables:
		try:
			header = " ".join(table[0])
		except(IndexError):
			error_log.write("ERROR:Error parsing " + eos+"\n")
			error_log.write("Table " + str(table) + "is null\n\n")
			continue
		if "Milestone" in header:
			dates = table
		elif "Number" in header:
			devices = [row[0] for row in table ]


	if len(dates) == 0 or len(devices) == 0:
		print ("ERROR:Error parsing " + eos)
		error_log.write("ERROR:Error parsing " + eos+"\n")
		if len(dates) == 0: 
			print("Cant find table with dates")
			error_log.write("Cant find table with dates\n")
		if len(devices) == 0:
			print("Cant find table with devices")
			error_log.write("Cant find table with devices\n")
		print ("")
		error_log.write("\n")
		continue


	pns = [device.replace(" ", "").replace('\n','') for device in devices]
	pns.pop(0)
	dates.pop(0)

