#!/usr/bin/python3
import httplib2
from bs4 import BeautifulSoup
import re





h = httplib2.Http(".cache")
resp, content = h.request("http://www.cisco.com/c/en/us/products/routers/product-listing.html", "GET")
soup = BeautifulSoup(content)
#print(response)
#print(soup.prettify())


print('Phase one')
# Find page for all router series page
pattern = re.compile('^/c/en/us/products/.*/.*/index.html')
alllinks = soup.findAll('a', href=True)
routers_page = [ 'http://cisco.com/' + link['href'] for link in alllinks if pattern.search(link['href']) ]
print('Done')
#print (routers_page)

# Find all eos listings for each router page
print('Phase two')
all_eos = []
for page in routers_page:
	page = page.replace('index','eos-eol-notice-listing')
	#print ('Checking page ' + str(page) )
	h = httplib2.Http(".cache")
	resp, content = h.request(page, "GET")
	soup = BeautifulSoup(content)
	alllinks = soup.findAll('a', href=True)
	eos_listing = [ link['href'] for link in alllinks if 'notice' in link['href'] and 'listing' not in link['href']  and '-fr' not in link['href']]
	all_eos.append(eos_listing)
	#print('Done')
	if len(eos_listing) == 0 :
		print ("No eos for " + page)
	print ("==" * 60)
	print ("")
print (len(all_eos))

