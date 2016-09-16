import pickle


eos = pickle.load(open('all_eos_pages.p','rb'))
print(len(eos))

check_url = ['http://www.cisco.com/c/en/us/products/collateral/interfaces-modules/shared-port-adapters-spa-interface-processors/eos-eol-notice-c51-731944.html',
	'http://www.cisco.com/c/en/us/products/collateral/interfaces-modules/shared-port-adapters-spa-interface-processors/end_of_life_notice_c51-575355.html',
	'http://www.cisco.com/c/en/us/products/collateral/routers/3900-series-integrated-services-routers-isr/eos-eol-notice-c51-737830.html',
	 'http://www.cisco.com/c/en/us/products/collateral/routers/3900-series-integrated-services-routers-isr/eos-eol-notice-c51-737830.html',
	 'http://www.cisco.com/c/en/us/products/collateral/routers/3900-series-integrated-services-routers-isr/eos-eol-notice-c51-737830.html',
	'http://www.cisco.com/c/en/us/products/collateral/routers/2900-series-integrated-services-routers-isr/eos-eol-notice-c51-737888.html'
	]


links = [i[1] for i in eos]
print(links[0])

for url in check_url:
	test_link = url.split('/')[-1]
	
	print (test_link, url in links)
