import json
import requests
from bs4 import BeautifulSoup, SoupStrainer
from dateutil.parser import parse
import pickle
import sys
from mylibs.utils import *
import datetime
import platform
import os
import asyncio
import aiohttp  

def f(urls,loop): 
	for url in urls:
		response = yield  from  aiohttp.request ('GET ' , url , loop = loop) 
		content = yield  from  response.read( )
		title = BeautifulSoup(content).find('h1')
		print (title)
 





log = get_logger('my_async.txt')
header = "http://www.cisco.com"


log.info('Gathering products from http://www.cisco.com/c/en/us/products/a-to-z-series-index.html#all')
content = get_page('http://www.cisco.com/c/en/us/products/a-to-z-series-index.html#all')	
strainer = SoupStrainer("div",{'class':'list-section'},)
soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
products = [ (link.text,header+link['href']) for link in soup.findAll('a', href=True) ]

# for product in products:
# 	content = get_page(product[1])
# 	title = BeautifulSoup(content.text).find('h1')
# 	print (title)



loop = asyncio.get_event_loop()
loop.run_until_complete(f(products,loop))