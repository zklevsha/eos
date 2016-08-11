import pickle



def find_index(url):
	eos_listing = pickle.load(open('eos_listing','rb'))
	for item in eos_listing:
		print(item[1])
		
		if item[1] == url:
			return(eos_listing.index(item))
	return ''





print(find_index('https://www.cisco.com/c/en/us/products/collateral/wireless/asr-5000-series/eos-eol-notice_C51-734559.html'))
