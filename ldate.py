from mylibs.utils import  get_page,get_logger,get_table
from bs4 import BeautifulSoup
import re
import sys
from dateutil.parser import parse




text = get_page('https://www.cisco.com/c/en/us/products/collateral/switches/1538-series-10-100-micro-hubs/prod_end-of-life_notice0900aecd8055eb7c.html')

s = BeautifulSoup(text.text)

ldate = []
for table in s.find_all('table'):
	t = get_table( BeautifulSoup(str(table)) )
	for i in t:
		if "Last Date" in i[0]:
			ldate.append(i)


print (ldate)