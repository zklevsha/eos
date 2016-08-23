import requests
import logging
from py_bing_search import PyBingWebSearch

def get_tables(soup):
	arr_tables = []
	for table in soup:
		arr_table = []
		rows = table.findAll('tr')
		for row in rows:
			cols = row.findAll('td')
			cols = [ele.text.strip() for ele in cols]
			arr_table.append(cols)
		arr_tables.append(arr_table)
	return arr_tables

def get_table(soup):
	for table in soup:
		arr_table = []
		rows = table.findAll('tr')
		header = table.find('tr').text.strip().split('\n')
		for row in rows:
			cols = row.findAll('td')
			#cols = [ele.text.strip() for ele in cols]
			cols = [ele.text.strip() for ele in cols]
			if len(header) > len(cols):
				for i in range(len(header) - len(cols)):
					cols.insert(0,'null')

			arr_table.append(cols)
	return arr_table

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
			print("Connection Error. Repeat")
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

	handler = logging.FileHandler("INFO_"+filename,mode='w')
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s %(message)s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	handler = logging.FileHandler("ERROR_"+filename,mode='w')
	handler.setLevel(logging.WARNING)
	formatter = logging.Formatter("%(asctime)s %(message)s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	return logger

def get_cisco_links(search_list):
	all_links = []
	for search_term in search_list:
		bing_web = PyBingWebSearch('IYn8qiw1XBamIWWOHKk9v1y0beHVivG75h3zPDhs0nQ', search_term, web_only=False) # web_only is optional, but should be true to use your web only quota instead of your all purpose quota
		first_fifty_result= bing_web.search(limit=50, format='json') #1-50
		cisco_links = [res.url for res in first_fifty_result if 'http://www.cisco.com' in res.url]
		for link in cisco_links:
			if link not in all_links:
				all_links.append(link)
	return all_links