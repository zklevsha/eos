import xlrd
import pickle
from bs4 import BeautifulSoup
import requests

rb = xlrd.open_workbook('old.xlsx')
data = pickle.load(open('data_2.p','rb'))
sheet = rb.sheet_by_index(0)
vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)]
vals.pop(0)




for val in vals:
	if val[0] not in data and val[4] != "":
		print(val[0])

