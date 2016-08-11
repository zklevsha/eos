# -*- coding: utf-8 -*-
from GoogleScraper import scrape_with_config, GoogleSearchError
import xlrd
import sys
import pickle

unidentified = ['BUN-C2950ST-24-LRE','C2611XM-2FE','C2621XM-2FE','C2650XM-1FE','CISCO3745-MB','CISCO3845-MB','CISCO1760','CISCO1760-V','CISCO1760-V3PN/K9']
error_log = open('parse_error_log', 'w')
rb = xlrd.open_workbook('old-test.xlsx')
sheet = rb.sheet_by_index(0)
rows = [sheet.row_values(rownum) for rownum in range(sheet.nrows)]
rows.pop(0)
data={}

for row in rows:
	if row[4] == "" or row[0] in unidentified:
		continue

	pn = row[0]
	print("")
	print("---------------------------------------------------- "+ pn + " ----------------------------------------------------")
	config = {
	'use_own_ip': True,
	'keywords': ["End-of-Sale and End-of-Life " + pn, "EoL/EoS " + pn], 
	'search_engines': ['duckduckgo'],
	'num_pages_for_keyword': 1,
	'num_results_per_page':10,
	'num_workers':1,
	'scrape_method': 'http',
	'do_caching': False
	}

	try:
		search = scrape_with_config(config)
	except GoogleSearchError as e:
		print(e)
		sys.exit()

	all_links = []
	for serp in search.serps:
		for link in serp.links:
			if "http://www.cisco.com/c/en/us/" in link.link:
				all_links.append(link.link)


	data[pn]=all_links

print('')
print (data)
pickle.dump(data,open('gs.p','wb'))
