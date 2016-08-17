from bs4 import BeautifulSoup,SoupStrainer
import requests
import logging
import datetime
import platform
import os 
header = "https://www.cisco.com"

def get_page(url):
	i = 0
	while True:
		if i == 5:
			cant_get_page.append(url)
			content = Object()
			content.text = 'Cant open url '+ url
			content.status_code = 504
			break
		try:
			content = requests.get(url,timeout=5)
		except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
			log.info ("Connection Error. Repeat")
			i = i+1
		else:
			break
	return content


def get_logger(filename):
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	# create console handler and set level to info
	handler = logging.StreamHandler()
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter(" %(message)s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	handler = logging.FileHandler(filename)
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter("%(message)s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	return logger


log = get_logger('get_products.log')
log.info('Starting script at' + str(datetime.datetime.now()))
if platform.system() =="Windows":
	os.system('chcp 65001') # for windows systems only

# Parse all products page
strainer = SoupStrainer("div",{'class':'product-content'},)
soup = BeautifulSoup(get_page('http://www.cisco.com/c/en/us/products/index.html').content,parse_only=strainer)
device_types = [ (link.text,header+link['href'].replace('index','product-listing')) for link in soup.find_all('a',href=True) ]

# Parse specific product page
for device_type in device_types:
	content = get_page(device_type[1])
	if content.status_code != 200:
		log.info('No product listing for ' + device_type[0])
		continue
	log.info('Device Type: ' + device_type[0])
	strainer = SoupStrainer("div",{'class':'list-section list-section-cat'})
	soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
	devices = [ (link.text,header+link['href']) for link in soup.find_all('a', href=True) ]
	print(devices)

	# Parse specific device for eos listing
	for device in devices:
		log.info('Parsing '+ device[0])
		content=get_page(device[1])
		strainer = SoupStrainer("a",{'class':'contentLink'})
		soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
		listing = [ header+link['href'] for link in soup.find_all('a', href=True) if "End-of-Life and End-of-Sale Notices" in link.text]

		if len(listing) == 0:
			log.info("No End-of-Sale for "+ device[0])
			continue

		# Parse eos listing page (if exist)
		log.log('Found some End-of-Sale listing')
		
		

# Check interfaces and modules separatly

interface_page =get_page('http://www.cisco.com/c/en/us/products/interfaces-modules/index.html')
strainer = SoupStrainer("div",{'class':'listing-ungrouped'},)
soup = BeautifulSoup(get_page('http://www.cisco.com/c/en/us/products/index.html').content,parse_only=strainer)
links = [ (link.text,header+link['href'].replace('index','product-listing')) for link in soup.find_all('a',href=True) ]


#Не забыть про End-of-Sale devices