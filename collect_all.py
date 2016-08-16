# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup,SoupStrainer
from dateutil.parser import parse
import requests
import sys
import pickle
import re
import os

header = 'https://www.cisco.com'
eos_listing = []
data = {}

#Bad pages
cant_get_page = []
cant_find_listing = []
multile_devices = []
ios_no_pn = []

accepted_header = ['EndofSaleProductPartNumber','ProductID','ProductNumber',
					'EndofSaleProduct']
def get_page(url):
	i = 0
	while True:
		if i == 10:
			cant_get_page.append(url)
			content = (500,'cant get page '+url)
			break
		try:
			content = requests.get(url,timeout=10)
		except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
			print ("Connection Error. Repeat")
			i = i+1
		else:
			break
	return content

os.system('chcp 65001')
if False: #debugging
	index_page = get_page("http://www.cisco.com/c/en/us/products/a-to-z-series-index.html#all")

	strainer = SoupStrainer("div",{'class':'list-section'})
	soup = BeautifulSoup(index_page.content,parse_only=strainer)

	#print (soup)

	links = [ (link.text,header+link['href']) for link in soup.find_all('a',href=True) ]


	print('------------- PHASE I: COLLECTING END OF SALE  PAGES ------------- ')

	print("\nStep 1 gathering listings")
	for link in links:
		print(link[0])
		content = get_page(link[1])

		if content.status_code != 200 :
			cant_get_page.append(link)
			continue

		strainer = SoupStrainer("a",{'class':'contentLink'})
		soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
		listing = [ header+link['href'] for link in soup.find_all('a', href=True) if "End-of-Life and End-of-Sale Notices" in link.text]

		if len(listing) != 0:
			eos_listing.append(listing[0])
		else:
			cant_find_listing.append(link)


	print("Found eos for " + str(len(eos_listing)) + 'pages')
	pickle.dump(eos_listing,open('eos_listing','wb'))

	print("Cant open  " + str(len(cant_get_page)) + 'pages')
	with open("cant_open.txt","w") as w:
			for item in cant_get_page:
				w.write(item[0])
				w.write(item[1])
				w.write("")

	print("Cand find Eos " + str(len(cant_find_listing)) + 'pages')
	with open("no_eos.txt","w") as w:
			for item in cant_find_listing:
				w.write(item[0] + " " + item[1])



print("")
print('------------- PHASE II: PARSING END OF SALE PAGES ------------- ')
eos_listing = pickle.load(open('eos_listing','rb'))
for page in eos_listing: # parsing eos listing
	print (page)
	content = get_page(page)
	strainer = SoupStrainer("ul",{'class':'listing'})
	soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
	eos_docs = [(link.text,header+link['href']) for link in soup.find_all('a', href=True) if "Relocation content" not in link.text and '-fr' not in link['href'] and "Frequently Asked Questions" not in link.text]

	for doc in eos_docs:#parsing eos docs
		print('')
		print('Title: '+doc[0])
		print("Url: "+doc[1])
		print("Index: "+ str(eos_docs.index(doc)) )
		content = get_page(doc[1])
		soup = BeautifulSoup(content.text,"html.parser")
		tables = soup.findAll("table")

		document_date = soup.find("div",{"class":"updatedDate"})
		if document_date is None:
			document_date = parse ("jun 1 100")
		else:
			document_date = parse(document_date.text.replace("Updated:",""))

		#Getting all tables in arr_tables list
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
				th = table[0][0].replace(" ", "").replace('\n','').replace('\xa0','').replace('-','')
				#print(repr(th))
			except(IndexError):
				continue

			if  th in accepted_header:
				arr = [row[0] for row in table ]
				devices.append(arr)
		
		if len(devices) == 0:
			if('Cisco IOS XE' in content.text ): #some eos ( somftware mainly) not have pn
				ios_no_pn.append(doc)
				continue
			#some documents were replaced
			if 'was replaced by' in content.text:
				print('OK')
			continue

			print("Cant find table with devices")
			print("url: "+doc[1])
			sys.exit()
			continue

		if len(devices) > 1:
			multile_devices.append((doc,devices))
			continue
		devices = devices[0]
		pns = [device.replace(" ", "").replace('\n','') for device in devices]
		pns.pop(0)
		for pn in pns:
			if pn not in data.keys():
				data[pn] = []
			data[pn].append({'title':doc[0],'url':doc[1],'date':document_date})

pickle.dump(data,open('data.p','wb'))

if len(multile_devices) != 0:
	pickle.dump(multile_devices,open('multile_devices.p','wb'))
	print('There are more then 1 table with pn for some documents')
	print('Please check multile_devices.p')


if len(ios_no_pn) != 0:
	pickle.dump(ios_no_pn,open('ios_no_pn.p','wb'))
	print('Some eos have no PN')
	print('Please check "ios_no_pn.p')

if len(cant_get_page) != 0:
	print('Coudl not get some of pages')
	print('Please check cant_get_page.p')
	pickle.dump(cant_get_page,open('cant_get_page.p','wb'))