#!/usr/bin/python3
import httplib2
from bs4 import BeautifulSoup
import re

h = httplib2.Http(".cache")
page = 'http://cisco.com/c/en/us/products/switches/data-center-switches/eos-eol-notice-listing.html'

resp, content = h.request(page, "GET")
if resp['status'] != '200' :
	print ('Error code :' + str(resp['status']))
	
soup = BeautifulSoup(content)
alllinks = soup.findAll('a', href=True)
eos_listing = [ link['href'] for link in alllinks if 'notice' in link['href'] and 'listing' not in link['href']  and '-fr' not in link['href']]

if len(eos_listing) == 0:
	print ("No eos")




	#framework-column-center