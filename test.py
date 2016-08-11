#!/usr/bin/python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from dateutil.parser import parse
import requests
import sys
import xlrd
import pickle

#pn="12000/4-AC-PEM"
unidentified = ['BUN-C2950ST-24-LRE','C2611XM-2FE','C2621XM-2FE','C2650XM-1FE','CISCO3745-MB','CISCO3845-MB','CISCO1760','CISCO1760-V','CISCO1760-V3PN/K9']
error_log = open('parse_error_log', 'w')
rb = xlrd.open_workbook('old.xlsx')
data={}


def get_page(url):
	while True:
		try:
			content = requests.get(url,timeout=10)
		except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
			print ("Error. Repeat")
		else:
			break
	return content



data = pickle.load(open('gs.p','rb'))


for key in data.keys():

	pn = key
	print("")
	print ("------------------" + pn +"------------------")
	alllinks = data[pn]

	if (len(alllinks) == 0 ):
		print("cant find " + pn)
		sys.exit()

	match_link = []
	for link in alllinks:
		print('checking ' + link )
		link = link.replace('.pdf','.html')

		content = get_page(link)
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
				try:
					devices = [row[0] for row in table ]
				except(IndexError):
					continue

		if len(devices) == 0:
			print("Cant find table with devices")
			continue


		pns = [device.replace(" ", "").replace('\n','') for device in devices]
		pns.pop(0)
		if pn not in pns:
			print(pn+' not in url. Cheking another one' )
		else:
			match_link.append((link,document_date))

	if len(match_link) == 0:
		print('Cant find eos')
		sys.exit()
		
	print(match_link)
		

	
