#!/usr/bin/python
import httplib2
from bs4 import BeautifulSoup,SoupStrainer
import re
import time
import pickle
import requests

devices = ['switches', 'routers']
all_eos = []
error_log = open('error.log','w')

for device in devices:

	print ("++++++++COLECTING INFORMATION FOR CISCO " + device + " ++++++++++++++++")
	

	h = httplib2.Http(".cache")
	resp, content = h.request("http://www.cisco.com/c/en/us/products/" + device + "/product-listing.html", "GET")
	soup = BeautifulSoup(content)
	#print(response)
	#print(soup.prettify())


	print('Phase one collecting index pages')
	# Find page for all device series page
	pattern = re.compile('^/c/en/us/products/.*/.*/index.html')
	alllinks = soup.findAll('a', href=True)
	devices_page = [ 'http://cisco.com' + link['href'] for link in alllinks if pattern.search(link['href']) ]
	print('Done')
	#print (devices_page)




	# Find all eos listings for each device page
	print('Phase two collecting eos_listning documents')
	for page in devices_page:
		page = page.replace('index','eos-eol-notice-listing')
		print ('Checking page ' + str(page) )

		while True:
			try:
				content = requests.get(page,timeout=10)
			except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
				print ("Error. Repeat")
				error_log.write('url_timeout' + page+'\t')
			else:
				break

		if content.status_code != 200 :
			print ('Error code :' + str(content.status_code))
			continue

		strainer = SoupStrainer("ul",{'class':'listing'})
		soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer) 
		alllinks = soup.findAll('a', href=True)
		for link in alllinks:
			if 'fr.html' not in link['href']:
				all_eos.append(link['href'])

			
		print('Eos lenght:' + str(len(all_eos)))
		print('Done')
		print ('=='*50)
		print('')
		

print(all_eos)
pickle.dump(all_eos,open('eos.p','wb'))

error_log.close()