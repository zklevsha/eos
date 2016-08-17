from splinter import Browser
import xlrd
import time


rb = xlrd.open_workbook('old.xlsx')
sheet = rb.sheet_by_index(0)
vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)]
vals.pop(0)

browser = Browser('chrome')
# Visit URL
url = "http://www.google.com"
browser.visit(url)
for val in vals:

	browser.fill('q', 'End EoS ' +val[0]+' site:www.cisco.com')
	# Find and click the 'search' button
	button = browser.find_by_name('btnG')
	button.click()
	# Interact with elements
	time.sleep(1) 

print button.html