from mylibs.utils import *
from bs4 import BeautifulSoup,SoupStrainer



content = get_page('http://www.cisco.com/c/en/us/support/switches/nexus-1010-virtual-services-appliance/model.html')

strainer = SoupStrainer("ul",{'id':'birth-cert-pids'})
soup = BeautifulSoup(content.text,'html.parser',parse_only=strainer)


if soup is not None:
	pids = [ li.text for li in soup.findAll('li') ]
else: 
	continue

strainer = SoupStrainer("table",{'class':'birth-cert-table'})
soup = BeautifulSoup(content.text,'html.parser',parse_only=strainer)

what_we_need = ['Series:','Product ID:','Status:','End-of-Sale Date:','End-of-Support Date:']
result_arr
for row in soup.findAll('tr'):
	try:
		k_w = (row.find('th').getText,row.find('td').getText().strip().replace('\n','')
	except:
		pass

	if any(k_w[0] == i in what_we_need):
		result_arr = append(k_w) 


print (result_arr)