import json
import requests
from bs4 import BeautifulSoup, SoupStrainer
from dateutil.parser import parse
import pickle
deviceTypes = ['routers','switches','security']
header = "http://www.cisco.com"
all_device_support_page = []
all_eos_listing_pages = []
all_eos_pages = []
error_log = open('error.log','w')
data = {}
import sys

def get_page(url):
	while True:
		try:
			content = requests.get(url,timeout=10)
		except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
			print ("Error. Repeat")
		else:
			break
	return content


#Collecting all device support pages
print('PHASE 1: COLLECTING SUPPORT PAGES')
for device in deviceTypes:
	content = get_page("http://www.cisco.com/c/dam/en/us/support/home/json/overlays/"+device+".json")

	diction = json.loads(content.text)
	#json['subCats'][0]['series'][6]

	for subcat in diction['subCats']:
		for model in  subcat['series']:
			all_device_support_page.append( (model['title'],header + model['url']) )



for i in all_device_support_page:
	print(i)

sys.exit()


# Gathering eos pages
print('PHASE 2: COLLECTING END OF SALE  PAGES')
print("\tstep 1 gathering listings")
for page in all_device_support_page:
	
	#searcing for eos-listing  link
	content = get_page(page)

	if content.status_code != 200 :
		print ('Error code :' + str(content.status_code)+" url " + page)
		continue

	strainer = SoupStrainer("div",{'class':'link'})
	soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
	eos_page_listing = [header+link['href'] for link in soup.findAll('a', href=True) if link.text == "End-of-Life and End-of-Sale Notices"]

	if len(eos_page_listing) != 0:
		all_eos_listing_pages.append(eos_page_listing[0])	

#parsing eos-listing
print("\tstep 2 gathering eos pages")
for eos_page in all_eos_listing_pages:

	content = get_page(eos_page)
	if content.status_code != 200 :
		print ('Error code :' + str(content.status_code)+" url " + page)
		continue

	strainer = SoupStrainer("ul",{'class':'listing'})
	soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer) 

	links = [header+link['href'] for link in soup.findAll('a', href=True) if 'fr.html' not in link['href'] ]
	if len(links) != 0:
		for link in links:
			all_eos_pages.append(link)



print('PHASE 3: GATHERING PN AND DATES')
for eos_page in all_eos_pages:
	content = get_page(eos_page)
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
		error_log.write("url: " + eos_page + "\n")
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
		if pn in data and eos_page not in data[pn]['url']:
			if(document_date > data[pn]['url']['date']):
				data[pn]['url'] = {'link':eos_page,'date':document_date}
		else:
			data[pn]={}
			data[pn]['url'] = {'link':eos_page,'date':document_date} 

pickle.dump(data,open('eos_json.p','wb'))