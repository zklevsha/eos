from mylibs.utils import  get_page
from bs4 import BeautifulSoup
import re
content = get_page('https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-4000-series-switches/prod_end-of-life_notice09186a00801eb0ae.html')
soup = BeautifulSoup(content.text)

p = soup.find_all('p',{'class':'pTableCaptionCMT'})

dates = []
devices = []
for item in p:
	print(item.text)
	# if "Milestones" in item.text:
	# 	dates.append(item.find_next('table'))
	# if "Product Part Numbers Associated" in item.text:
	# 	devices.append(item.find_next('table'))


print(dates)
print(devices)