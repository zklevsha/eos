from  mylibs.utils import  get_page,get_logger,get_cisco_links


pns = ['WS-SVC-AGM-1-K9','XENPAK-10GB-ZR','WS-C3750-48TS-S','WS-C2970G-24T-E','WIC-4ESW']


for pn in pns:
	print("PN:",pn)
	links = get_cisco_links([pn])
	for link in links:
		print(link)

	print('')