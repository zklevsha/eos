from bs4 import BeautifulSoup,SoupStrainer
import requests



while True:
	try:
		content = requests.get("http://www.cisco.com/c/en/us/products/routers/12000-series-routers/eos-eol-notice-listing.html",timeout=10)
	except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
		print ("Error. Repeat")
		error_log.write('url_timeout' + page+'\t')
	else:
		break

all_eos = []
strainer = SoupStrainer("ul",{'class':'listing'})
soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer) 
alllinks = soup.findAll('a', href=True)
for link in alllinks:
	#print (link.text)
	#print('cheking ' + link['href'])
	if 'fr.html' not in link['href']:
		#print ('added')
		all_eos.append(link['href'])

print(all_eos)