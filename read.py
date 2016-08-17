import xlrd
import pickle
from bs4 import BeautifulSoup
import requests
import os



rb = xlrd.open_workbook('old.xlsx')
data = pickle.load(open('data.p','rb'))
multiple_devices = pickle.load(open('multile_devices.p','rb'))
sheet = rb.sheet_by_index(0)
vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)]
vals.pop(0)




for val in vals:
	if val[0] not in data and val[4] != "":
		match = False
		for item  in multiple_devices:
			if val in item[1]:
				print(val, "in multiple devises list url:",url)
				match = True
		if not match:
			print ("Can found page for pn",val[0])
		

