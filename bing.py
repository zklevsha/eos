# -*- coding: utf-8 -*-

from py_bing_search import PyBingWebSearch
from bs4 import BeautifulSoup
import pickle
import requests
from dateutil.parser import parse
import xlrd

error_log = open('error.log','w')
#pns = ["12000/4-AC-PEM"]
data = {}


def get_page(url):
	while True:
		try:
			content = requests.get(url,timeout=10)
		except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
			print ("Error. Repeat")
		else:
			break
	return content

def get_links(search_list):
	all_links = []
	for search_term in search_list:
		bing_web = PyBingWebSearch('IYn8qiw1XBamIWWOHKk9v1y0beHVivG75h3zPDhs0nQ', search_term, web_only=False) # web_only is optional, but should be true to use your web only quota instead of your all purpose quota
		first_fifty_result= bing_web.search(limit=50, format='json') #1-50
		cisco_links = [res.url for res in first_fifty_result if 'http://www.cisco.com' in res.url]
		for link in cisco_links:
			if link not in all_links:
				all_links.append(link)
	return all_links


rb = xlrd.open_workbook('old.xlsx')
sheet = rb.sheet_by_index(0)
rows = [sheet.row_values(rownum) for rownum in range(sheet.nrows)]
pns = [row[0] for row in rows]
pns.pop(0)

for pn in pns:
	print("")
	print("=============CHEKING " + pn+"==============")
	search_arr = [pn + " End-Of-Sale","pn + EoS"]
	cisco_links = get_links(search_arr)
	
	for link in cisco_links:
		print("Checking " + link)
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
				devices = [row[0] for row in table ]

		if len(devices) == 0:
			print("Cant find table with devices")
			error_log.write("Cant find table with devices\n")
			error_log.write("url: " + link + "\n")
			error_log.write("\n")
			continue

		all_pns = [device.replace(" ", "").replace('\n','') for device in devices]
		all_pns.pop(0)

		if pn not in all_pns:
			print(pn + " not in this document checking another link")
			continue
		else:
			print("\033[92m"+pn+ " found in this document ")

		#try:
		#	print (all_pns)
		#	print (document_date)

		#except UnicodeEncodeError:
		#	print("Cant print pns - there some not printable characters ")

		if pn in data and link not in data[pn]['url']:
			if(document_date > data[pn]['url']['date']):
				data[pn]['url'] = {'link':eos_page,'date':document_date}
		else:
			data[pn]={}
			data[pn]['url'] = {'link':link,'date':document_date} 

pickle.dump(data,open('data.p','wb'))