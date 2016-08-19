from mylibs.utils import  get_page,get_logger,get_table
from bs4 import BeautifulSoup
import re
import sys

url_list = ['https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-4000-series-switches/prod_end-of-life_notice09186a00801eb0ae.html']
log = get_logger('new_way.txt')	
with open('out.html', "w"):
        pass
data = {}
for url in url_list:
	log.info('Parsing: ' + url)
	content = get_page(url)
	soup = BeautifulSoup(content.text,"html.parser")

	p = soup.find_all('p')

	dates = {}
	devices = {}
	dv_dt = []

	for item in p:
		#print(item.text)
		if "Milestones" in item.text:
			dates[item.text] = BeautifulSoup( str(item.find_next('table')) , "html.parser" )
		if "Product Part Numbers Associated" in item.text or "Product Part Numbers Affected" in item.text:
			devices[item.text] = BeautifulSoup( str(item.find_next('table')) , "html.parser" )
	

	if len(dates) != len(devices):
		log.error('Number of dates and devices not equal')
		sys.exit()

	if len(dates) == 0:
		log.error('Cant parse dates')
		sys.exit()


	if len(devices) == 0:
		log.error('Cant parse devices')
		sys.exit()


	if len(dates) == 1:
		print (devices.keys())
		dv = [i for i  in devices.keys()][0]
		dt = [i for i  in dates.keys()][0]
		print(dv)
		dv_dt.append((dv,dt))
	else:	
		for devk in devices.keys():
			st = devk[-3:].replace(' ','')
			for datk in dates.keys():
				# print(datk)
				if st in datk: 
					dv_dt.append((devk,datk))

	if len(dates) != len(dv_dt):
		log.error('Error creating dv_dt')
		sys.exit()



	log.info('This page have '+ str(len(dates)) + ' dv dt pairs')
	for dvk,dtk in dv_dt:
		log.info('Device title ' + dvk)
		dv = get_table(devices[dvk])
		log.info('Assosiate dates title ' + dtk)
		dt = get_table(dates[dtk])
		dt.pop(0)
	

		pns = [i[0] for i in dv]
		pns.pop(0)
		new_pns = []
		for pn in pns:
			if pn not in new_pns and 'Change' not in pn :
				new_pns.append(pn.replace(" ", "").replace('\n',''))
		pns = new_pns

		
		log.info('Adding pn to dictionary')
		for pn in pns:
			log.info("pn:" + str(pn))

			# check for duplicate keys
			if pn  in data.keys():
				log.warning('Dublicate PN ' + str(pn))
				log.warning(data[pn])
				sys.exit()
			else:
				data[pn] = {}
			
			for item in dt:
				data[pn][item[0]]=item[2]	
			data[pn]['doc'] = url


print(data)


	# for i in dv_dt:
	# 	log.info('Device title ' + i[0])
	# 	log.info(get_table(devices[i[0]]))
	# 	log.info('Assosiate dates title ' + i[1])
	# 	log.info(get_table(dates[i[1]]))
		# log.info('Writing to out.html')
		# with open('out.html','a') as fl:
		# 	fl.write(i[0])
		# 	fl.write(str(devices[i[0]]))
		# 	fl.write(i[1])
		# 	fl.write(str(dates[i[1]]))
		# 	fl.write('<p>==============================================================</p>')
		# log.info('Done')
		# log.info(' ')
	# print('Dates k')
	# for key in dates.keys():
	# 	print (key)

	# print('')
	# print('Devices k')

	# for key in devices.keys():
	# 	print (key)


