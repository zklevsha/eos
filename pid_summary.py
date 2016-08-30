from mylibs.utils import *
from bs4 import BeautifulSoup,SoupStrainer


pid_summary = {}
pid_info = {}
content = get_page('http://www.cisco.com/c/en/us/support/security/identity-services-engine-1-4/model.html')

strainer = SoupStrainer("ul",{'id':'birth-cert-pids'})
soup = BeautifulSoup(content.text,'html.parser',parse_only=strainer)


if soup is not None:
	pids = [ li.text for li in soup.findAll('li') ]
else: 
	pass

strainer = SoupStrainer("table",{'class':'birth-cert-table'})
soup = BeautifulSoup(content.text,'html.parser',parse_only=strainer)

what_we_need = ['Series:','Status:','End-of-Sale Date:','End-of-Support Date:']
result_arr = []
for row in soup.findAll('tr'):
	try:
		k = row.find('th').text
		v = row.find('td').text
		if any(k == i for i in what_we_need):
			#result_arr.append( (k,' '.join(v.split())) ) 
			pid_info[k] = ' '.join(v.split())
	except:
		pass



for p in pids:
	pid_summary[p] =  pid_info



print (pid_summary)
