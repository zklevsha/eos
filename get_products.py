from bs4 import BeautifulSoup,SoupStrainer
import requests
import logging
import datetime
import platform
import os
import sys
from  mylibs.utils import  get_page,get_logger,get_cisco_links,get_tables


strange_links = ['https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-4000-series-switches/prod_end-of-life_notice0900aecd80324aee.html']

header = "https://www.cisco.com"
log = get_logger('get_products.log')
devices_header = ['EndofSaleProductPartNumber','ProductID','ProductNumber',
					'EndofSaleProduct']
parsed_eos = [] # some of docs may be reachable via several places
dates_header = []
data ={}
error_parse = []
log.info('Starting script at' + str(datetime.datetime.now()))
if platform.system() =="Windows":
	os.system('chcp 65001') # for windows systems only

# Parse all products page
strainer = SoupStrainer("div",{'class':'product-content'},)
soup = BeautifulSoup(get_page('http://www.cisco.com/c/en/us/products/index.html').content,parse_only=strainer)
device_types = [ (link.text,header+link['href'].replace('index','product-listing')) for link in soup.find_all('a',href=True) ]

# Parse specific product page
for device_type in device_types:
	device_type = ('switches','http://www.cisco.com/c/en/us/products/switches/product-listing.html')
	content = get_page(device_type[1])
	if content.status_code != 200:
		log.info('No product listing for ' + device_type[0])
		sys.exit
		continue
	log.info('Device Type: ' + device_type[0])
	strainer = SoupStrainer("div",{'class':'list-section list-section-cat'})
	soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
	devices = [ (link.text,header+link['href']) for link in soup.find_all('a', href=True) ]
	if len(devices) == 0:
		log.error('No devices for' + str(device_type[0]))

	# Checking end of sale devices
	log.info('Checking if there are end of sale devices:')
	content = get_page(device_type[1].replace('product-listing.html','eos-eol-listing.html'))
	if content.status_code == 200:
		log.info('Found eos devices. Adding them to list')
		strainer = SoupStrainer("table",{'id':'framework-base-content'})
		soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
		eos_devices = [ (link.text,header+link['href']) for link in soup.find_all('a', href=True)  if 'End-of-Life Policy' not in link.text]
		if len(eos_devices) != 0:
			devices = devices + eos_devices
			log.info('Done.')
	else:
		log.info ("No end of sales devices for " + str(device_type[0]))

	log.info(' ')
	# Parse specific device for eos listing
	for device in devices:
		log.info('Parsing '+ device[0])
		content=get_page(device[1])
		strainer = SoupStrainer("a",{'class':'contentLink'})
		soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
		listing = [ header+link['href'] for link in soup.find_all('a', href=True) if "End-of-Life and End-of-Sale Notices" in link.text]

		if len(listing) == 0:
			log.info("No End-of-Sale for "+ device[0])
			log.info(' ')
			continue

		# Parse eos listing page (if exist)
		log.info('Found some End-of-Sale listing')
		log.info ('url:' + str( listing[0]))
		content = get_page(listing[0])
		strainer = SoupStrainer("ul",{'class':'listing'})
		soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
		eos_docs = [(link.text,header+link['href']) for link in soup.find_all('a', href=True) if "Relocation content" not in link.text and '-fr' not in link['href'] and "Frequently Asked Questions" not in link.text]
		for eos in eos_docs:
			log.info('Title:' + str(eos[0]))
			log.info('Url:' + str(eos[1]))

			if eos[0] in parsed_eos:
				log.info('This one was parsed before.Skiping')
				log.info(' ')
				continue
			if eos[1] in strange_links:
				log.error('This one was in strange_links. I cannot parse it properly')
				log.error(' ')
				continue
			if "Change in Product Part Number Announcement" in eos[0]:
				log.info('This one not EOS page but only information about EoS change. Skiping')
				log.info(' ')
				continue

			content = get_page(eos[1])
			soup = BeautifulSoup(content.text,"html.parser")
			tables = soup.findAll("table")
			arr_tables = get_tables(tables)
			devices_table = []
			dates_table = []
			
			for table in arr_tables:
				try:
					th = table[0][0].replace(" ", "").replace('\n','').replace('\xa0','').replace('-','')
					#log.info(repr(th))
				except(IndexError):
					continue

				if  th in devices_header:
					arr = [row[0] for row in table ]
					devices_table.append(arr)
				if th == 'Milestone':
					dates_table.append(table)
			
			if len(devices_table) == 0:
				if('Cisco IOS XE' in content.text ): #some eos ( somftware mainly) not have pn
					#ios_no_pn.append(doc)
					log.info('Looks like this is software page, so no PN for this one')
					log.info(' ')
					continue
				#some documents were replaced
				if 'was replaced by' in content.text:
					log.info('This doc was replaced')
					log.info('')
				continue

				log.info("Cant find table with devices")
				log.warning("url: "+eos[1])
				sys.exit()
				continue

			if len(dates_table) == 0 or len(dates_table) > 1:
				success_parse_dates = False
				tf = ""
				log.warning("ERROR: Number of tables with dates " + str(len(dates_table)))
				log.warning('ERROR url: ' + eos[1])
				error_parse.append( ("dates_table =" +str(len(dates_table)),eos[1]) )
				for dt in devices_table:
					dt.pop(0)
					if tf == "":
						tf = dt
					else:
						tf = tf+dt
				devices_table = [tf]

			else:
				success_parse_dates = True

			if len(devices_table) != 1 and success_parse_dates:
				log.warning('Multiple devices tables')
				log.warning('url ' + str(eos[1]))
				sys.exit()

			dates_table = dates_table[0]
			dates_table.pop(0)
			devices_table = devices_table[0]
			pns = [device.replace(" ", "").replace('\n','') for device in devices_table]
			new_pns = []
			for pn in pns:
				if pn not in new_pns and 'Change' not in pn :
					new_pns.append(pn)
			pns = new_pns
			pns.pop(0)	
			#print (dates_table)

			
			
			for pn in pns:
				log.info("pn:" + str(pn))

				# check for duplicate keys
				if pn  in data.keys():
					log.warning('Dublicate PN ' + str(pn))
					log.warning(data[pn])
					sys.exit()
				else:
					data[pn] = {}
				
				if success_parse_dates:
					for item in dates_table:
						data[pn][item[0]]=item[2]
					
				data[pn]['doc'] = eos
				data[pn]['success_parse_dates'] = success_parse_dates
			parsed_eos.append(eos[0])
			log.info('')		
	sys.exit()

# Check interfaces and modules separatly

#interface_page =get_page('http://www.cisco.com/c/en/us/products/interfaces-modules/index.html')
#strainer = SoupStrainer("div",{'class':'listing-ungrouped'},)
#soup = BeautifulSoup(get_page('http://www.cisco.com/c/en/us/products/index.html').content,parse_only=strainer)
#links = [ (link.text,header+link['href'].replace('index','product-listing')) for link in soup.find_all('a',href=True) ]


