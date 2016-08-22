from bs4 import BeautifulSoup,SoupStrainer
import requests
import logging
import datetime
import platform
import os
import sys
from  mylibs.utils import  get_page,get_logger,get_cisco_links,get_table
from dateutil.parser import parse

strange_links = ['https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-4000-series-switches/prod_end-of-life_notice0900aecd80324aee.html',
'https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-6500-series-switches/prod_end-of-life_notice09186a008023401e.html',
'https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-6500-series-switches/eol_c51-683155.html']

header = "https://www.cisco.com"
log = get_logger('get_products.log')
devices_header = ['EndofSaleProductPartNumber','ProductID','ProductNumber',
					'EndofSaleProduct']
parsed_eos = [] # some of docs may be reachable via several places
dates_header = []
data ={}
error_parse = []
start_date = datetime.datetime.now()
log.info('Starting script at' + str(datetime.datetime.now()))
if platform.system() =="Windows":
	os.system('chcp 65001') # for windows systems only


#modules and interfaces page has different html tags so parse them separatly
page = get_page('http://www.cisco.com/c/en/us/products/interfaces-modules/index.html')
s = BeautifulSoup(page.text)
int_and_mod = [ (link.text,header+link['href']) for link in s.find_all('a', {'class':'contentBoldLink'}) ]


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
				log.warning('This one was in strange_links. I cannot parse it properly')
				log.error(' ')
				continue
			if "Change in Product Part Number Announcement" in eos[0]:
				log.info('This one not EOS page but only information about EoS change. Skiping')
				log.info(' ')
				continue


			content = get_page(eos[1].replace('.pdf','.html'))

			if content.status_code != 200:
				log.warning('cant parse url. Skiping' )
				continue

			if "THIS ANNOUNCEMENT WAS REPLACED"  in content.text:
				log.info('This EOS was replaced. Skiping')
				log.info(' ')
				continue

			soup = BeautifulSoup(content.text,"html.parser")
			p = soup.find_all('p')

			dates = {}
			devices = {}
			dv_dt = []

			for item in p:
				#print(item.text)
				if "Milestones" in item.text:
					dates[item.text] = BeautifulSoup( str(item.find_next('table')) , "html.parser" )
					log.info("Added to Dates "+ item.text)
				if "Product Part Numbers Associated" in item.text or "Product Part Numbers Affected" in item.text and "Software" not in item.text and "Milestone" not in item.text:
					devices[item.text] = BeautifulSoup( str(item.find_next('table')) , "html.parser" )
					log.info("Added to Devices " + item.text)
				
			if len(dates) == 0:
				log.error('Cant parse dates')
				sys.exit()


			if len(devices) == 0:
				#some eos ( somftware mainly) not have pn
				if'Cisco IOS XE' in content.text or 'Cisco IOS Software Release' in content.text or 'OS Release' in content.text:
					log.info('Looks like this is software page, so no PN for this one')
					log.info(' ')
					continue
				#some documents were replaced
				#if 'was replaced by' in content.text:
				#	log.info('This doc was replaced')
				#	log.info('')
				#	continue
				log.error('Cant parse devices')
				sys.exit()


			if len(dates) != len(devices):
				log.error('Number of dates and devices not equal')
				sys.exit()


			if len(dates) == 1:
				dv = [i for i  in devices.keys()][0]
				dt = [i for i  in dates.keys()][0]
				dv_dt.append((dv,dt))
			else:	
				for devk in devices.keys():
					st = devk[-3:].replace(' ','')
					for datk in dates.keys():
						# print(datk)
						if st in datk: 
							dv_dt.append((devk,datk))

			if len(dates) != len(dv_dt):
				log.error('Error creating dv_dt')
				sys.exit()


			document_date = soup.find("div",{"class":"updatedDate"})
			if document_date is None:
				document_date = parse ("jun 1 100")
			else:
				document_date = parse(document_date.text.replace("Updated:",""))

			eos = (eos[0],eos[1],document_date)

			log.info('This page have '+ str(len(dates)) + ' dv dt pairs')
			for dvk,dtk in dv_dt:
				log.info('Device title ' + dvk)
				dv = get_table(devices[dvk])
				log.info('Assosiate dates title ' + dtk)
				dt = get_table(dates[dtk])
				dt.pop(0)
			

				pns = [i[0] for i in dv]
				pns.pop(0)

				new_pns = []
				for pn in pns:
					if pn not in new_pns and 'Change' not in pn :
						new_pns.append(pn.replace(" ", "").replace('\n',''))
				pns = new_pns
			
				log.info('Adding pn to dictionary')
				for pn in pns:
					log.info("pn:" + str(pn))

					# check for duplicate keys
					if pn  in data.keys():
						log.warning('Dublicate PN ' + str(pn))
						log.warning("Document date(stored):"  + str(data[pn]['doc'][2]))
						log.warning("Document date(new): " + str(document_date))
						if data[pn]['doc'][2] > document_date:
							log.warning('Stored document is newer. Sciping new values')
							continue
						else:
							log.warning('Stored document is older. Updating')
					else:
						data[pn] = {}
					
					for item in dt:
						if len(item) != 3:
							log.warning('Cant parse this string')
							log.warning(item)
							log.warning('Skiping')
						else:	
							data[pn][item[0]]=item[2]	

					data[pn]['doc'] = eos

				parsed_eos.append(eos[0])
				log.info(len(data))
				log.info('')

	log.info(len(data))
	log.info(datetime.datetime.now() - start_date)
	sys.exit()
			

# Check interfaces and modules separatly
# dont forget about strange_links
# you are skiping "softare pages" check them seperatly
#interface_page =get_page('http://www.cisco.com/c/en/us/products/interfaces-modules/index.html')
#strainer = SoupStrainer("div",{'class':'listing-ungrouped'},)
#soup = BeautifulSoup(get_page('http://www.cisco.com/c/en/us/products/index.html').content,parse_only=strainer)
#links = [ (link.text,header+link['href'].replace('index','product-listing')) for link in soup.find_all('a',href=True) ]


# some pages have tables with affected sowftware PN . Script ignores it for now