def get_page(url):
	while True:
		try:
			content = requests.get(url,timeout=10)
		except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError):
			print ("Error. Repeat")
		else:
			break
	return content



https://search.cisco.com/search?query=ASA5510-AIP-NFR-K9%20eos&locale=enUS&tab=Cisco