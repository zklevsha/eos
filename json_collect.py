import json
import requests
from bs4 import BeautifulSoup, SoupStrainer
from dateutil.parser import parse
import pickle
import sys
from mylibs.utils import *
import datetime
import platform
import os




deviceTypes = ['routers','switches','security','wireless','serversunifiedcomputing','applicationnetworkingservices',
				'cloudandsystemsmanagement',
				'collaborationendpoints','conferencing','connectedsafetyandsecurity',
				'customercollaboration','ciscointerfacesandmodules',
				'opticalnetworking','serviceexchange','storagenetworking',
				'video']

header = "http://www.cisco.com"
all_device_support_page = []

parsed_eos = []


data = {}
pid_summary = {}
pid_bad = {}
log = get_logger('json_collect.txt')

startTime = datetime.datetime.now()
log.info('Starting script at ' + str(startTime) )
if platform.system() =="Windows":
	os.system('chcp 65001') # for windows systems only

#Collecting all device support pages 
log.info('PHASE 1: COLLECTING SUPPORT PAGES')
for device in deviceTypes:
	log.info('Gathering ' + device)
	content = get_page("http://www.cisco.com/c/dam/en/us/support/home/json/overlays/"+device+".json")
	#print (content.text)
	diction = json.loads(content.text)
	#json['subCats'][0]['series'][6]

	for subcat in diction['subCats']:
		for model in  subcat['series']:
			all_device_support_page.append( (model['title'],header + model['url']) )
log.info("Done.")
log.info('')

# Gathering eos pages
log.info('PHASE 2: COLLECTING END OF SALE  INFORMATION')
for device in all_device_support_page:
	#device = ('1100 Cloud', 'http://www.cisco.com/c/en/us/support/switches/nexus-1100-series-cloud-services-platforms/tsd-products-support-series-home.html')
	log.info('Checking ' + str(device[0]) + ' series')
	log.info("url:" + device[1])
	#searcing for eos-listing  link
	content = get_page(device[1])

	if content.status_code != 200 :
		log.error('Error code :' + str(content.status_code)+" url " + device[1])
		continue

	
	soup = BeautifulSoup(content.text,"html.parser")
	strainer = SoupStrainer("div",{'id':'models-in-series'},)
	soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)


	devices_in_series = [ (link.text,header+link['href']) for link in soup.findAll('a', href=True) ]


	if len(devices_in_series) == 0:
		log.error('Cant find devices for this serices')
		log.error(device)
		continue

	log.info('Found ' + str( len(devices_in_series) )  + ' models')
	log.info(" ")

	for model in devices_in_series:
		#model  = ('asr','http://www.cisco.com/c/en/us/support/routers/asr-901-6cz-f-a-router/model.html')
		log.info('Parsing ' + model[0])
		log.info(model[1])
		content = get_page(model[1])


		log.info('Gathering PN assosiated with this device and some eos info')
		strainer = SoupStrainer("ul",{'id':'birth-cert-pids'})
		soup = BeautifulSoup(content.text,'html.parser',parse_only=strainer)

		if soup is not None:
			pids = [ li.text for li in soup.findAll('li') ]
		else: 
			pass

		strainer = SoupStrainer("table",{'class':'birth-cert-table'})
		soup = BeautifulSoup(content.text,'html.parser',parse_only=strainer)

		what_we_need = ['Series:','Status:','End-of-Sale Date:','End-of-Support Date:']
		pid_info = {}
		for row in soup.findAll('tr'):
			try:
				k = row.find('th').text
				v = row.find('td').text
				if any(k == i for i in what_we_need):
					v = ' '.join(v.replace('Details','').split())
					if k == 'Status:': # Удаляем лишнее. Оставляем только Orderable, End Of Sale, End Of Support
						pid_info[k] = v.replace('End-of-Sale','EndOfSale').replace('End-of-Support','EndOfSupport').split()[0]
					else:
						pid_info[k] = v
			except:
				pass
		pid_info['doc'] = model

		for p in pids: pid_summary[p] =  pid_info
		log.info('Done. Found ' + str(len(pids)) + ' pids' )

		log.info('Searching for EOS documents')
		soup = BeautifulSoup(content.text,"html.parser")
		a = soup.find('a',{'id':'End-of-LifeandEnd-of-SaleNotices'})
		if a is None:
			log.info('There are no EOS for this device. Skiping')
			log.info(' ')
			continue
		uls = a.find_next('ul')
		
		eos_pages = [(link.text,link['href']) for link in uls.findAll('a', href=True) if '-fr' not in link['href']]

		log.info('Found '+ str(len(eos_pages)) + ' docs')
		log.info('Begin parsing them.')
			
		# Цикл 3. Парсим EOS документы
		for eos in eos_pages:
			#eos = ('title','http://www.cisco.com/c/en/us/support/switches/small-business-unmanaged-switches/tsd-products-support-series-home.html')
			if eos[1][0] == '/':eos = (eos[0],header+eos[1]) # Нужен абсолютный путь

			log.info('Title:' + str(eos[0]))
			log.info('Url:' + str(eos[1]))

			if eos[1] in parsed_eos:
				log.info('This one was parsed before.Skiping')
				log.info(' ')
				continue
			if "Change in Product Part Number Announcement" in eos[0]:
				log.info('This one not EOS page but only information about EoS change. Skiping')
				log.info(' ')
				parsed_eos.append(eos[1])
				continue


			content = get_page(eos[1].replace('.pdf','.html'))

			if content.status_code != 200:
				log.error('cant open url ' + eos[1] +  ' Skiping' )
				log.error('')
				parsed_eos.append(eos[1])
				continue

			soup = BeautifulSoup(content.text,"html.parser")
			p = soup.find_all('p',{'class':'pTableCaptionCMT'})

			dates = {}
			devices = {}
			dv_dt = []

			for item in p:
				if "milestone" in item.text.lower().replace(' ','').replace('-','').replace('\n',''):
					date_soup = BeautifulSoup( str(item.find_next('table')) , "html.parser" )
					if date_soup.string != 'None':
						dates[item.text] = date_soup
						log.info("Added to Dates "+ item.text)

				devices_caption = ['productpartnumbersassociated','productpartnumbersaffected',
				'productpartnumberaffected','productpartnumbersbeingaffected','endofsalepartnumbers']
				search = item.text.lower().replace('-','').replace(' ','').replace('\n','')\

				if any( i in search for i in devices_caption) and "Software" not in item.text and "Milestone" not in item.text:
					device_soup = BeautifulSoup( str(item.find_next('table')) , "html.parser" )
					if device_soup.string != 'None':
						devices[item.text] = device_soup
						log.info("Added to Devices " + item.text)

			if len(devices) == 0:
				#some eos ( somftware mainly) not have pn
				if 'Cisco IOS' in content.text or 'Cisco IOS Software Release' in content.text or 'OS Release' in content.text:
					log.info('Looks like this is software page, so no PN for this one')
					log.info(' ')
					parsed_eos.append(eos[1])
					continue
			
				log.error('Cant find table with devices.Skiping')
				log.error(eos)
				log.error('')
				parsed_eos.append(eos[1])
				continue

			if len(dates) == 0:
				if "has been replaced" in content.text or "THIS ANNOUNCEMENT WAS REPLACED" in content.text or 'THIS ANNOUNCEMENT HAS BEEN REDIRECTED' in content.text:
					log.info('This EOS was replaced. Skiping')
					log.info('')
					parsed_eos.append(eos[1])
					continue 
				try:
					retraction_header = ['retraction', 'retracted' ]
					search = soup.find('h1',{'id':'fw-pagetitle'}).text.lower().replace(' ','').replace('-','').replace('\n','')
					if  any(i in search for i in retraction_header):
						log.info('This is page about retraction of some PN. Skiping')
						log.info('')
						parsed_eos.append(eos[1])
						continue
				except:
						log.error('Error parsing page. Cant find header(id=fw-pagetitle):')
						
					

				log.error('Cant parse dates. Adding PN to pid_bad dictionary')
				log.error(eos)
				for dvk in devices.keys():
					dv = get_table(devices[dvk])
					pns = [i[0] for i in dv]
					pns.pop(0)

					new_pns = []
					for pn in pns:
						if pn not in new_pns and 'Change' not in pn and 'null' not in pn :
							new_pns.append(pn.replace(" ", "").replace('\n',''))
					pns = new_pns
					for pn in pns:
						pid_bad[pn] = eos
					log.error('Added ' + str(len(pns)) + 'pns')
				log.error('Done.')
				log.error('')
				parsed_eos.append(eos[1])
				continue
				#sys.exit()

			if len(dates) != len(devices):
				log.error('Number of table with devices  and  table with devices  are not equal')
				log.error(eos)
				if len(devices) > 0:
					log.error('Adding PN to pid_bad dictionary')
					for dvk in devices.keys():
						dv = get_table(devices[dvk])
						pns = [i[0] for i in dv]
						pns.pop(0)

						new_pns = []
						for pn in pns:
							if pn not in new_pns and 'Change' not in pn and 'null' not in pn :
								new_pns.append(pn.replace(" ", "").replace('\n',''))
						pns = new_pns
						for pn in pns:
							pid_bad[pn] = eos
						log.error(' Added ' + str(len(pns)) + 'pns')
					log.error('Done')
					log.error('')
					parsed_eos.append(eos[1])
					continue
				else:
					log.error('Cant find any device for this page. Skipping')
					log.error('')
					parsed_eos.append(eos[1])
					continue

			if len(dates) == 1:
				dv = [i for i  in devices.keys()][0]
				dt = [i for i  in dates.keys()][0]
				dv_dt.append((dv,dt))
			else:	
				for devk in devices.keys():
					st = devk[-3:].replace(' ','')
					for datk in dates.keys():
						log.info(datk)
						if st in datk: 
							dv_dt.append((devk,datk))


			if len(dates) != len(dv_dt):
				log.error('Error creating dv_dt')
				log.error(eos)
				log.error('Adding PN to pid_bad dictionary')
				for dvk in devices.keys():
					dv = get_table(devices[dvk])
					pns = [i[0] for i in dv]
					pns.pop(0)

					new_pns = []
					for pn in pns:
						if pn not in new_pns and 'Change' not in pn and 'null' not in pn :
							new_pns.append(pn.replace(" ", "").replace('\n',''))
					pns = new_pns
					for pn in pns:
						pid_bad[pn] = eos
				log.error(' Added ' + str(len(pns)) + 'pns')
				log.error('Done')
				log.info('')
				parsed_eos.append(eos[1])
				continue


			document_date = soup.find("div",{"class":"updatedDate"})
			if document_date is None:
				document_date = parse ("jun 1 100")
			else:
				document_date = parse(document_date.text.replace("Updated:",""))

			eos = (eos[0],eos[1],document_date)

			log.info('This page have '+ str(len(dates)) + ' dv dt pairs')
			for dvk,dtk in dv_dt:
				log.info('Device title ' + dvk)
				dv = get_table(devices[dvk])
				log.info('Assosiate dates title ' + dtk)
				dt = get_table(dates[dtk])
				dt.pop(0)
			

				pns = [ (i[0],i[1]) for i in dv if all(i[0] != a for a in ['Change','null']) ]
				pns.pop(0)
				


				# new_pns = []
				# for pn in pns:
				# 	if pn not in new_pns and 'Change' not in pn and 'null' not in pn :
				# 		new_pns.append(pn.replace(" ", "").replace('\n',''))
				# pns = new_pns
			
				log.info('Adding pn to dictionary')
				for pn_descr in pns:
					pn = pn_descr[0]
					log.info("pn:" + str(pn))

					# check for duplicate keys
					if pn  in data.keys():
						log.error('Duplicate PN ' + str(pn))
						log.error('Stored doc url :'+ data[pn]['doc'][1])
						log.error("Document date(stored):"  + str(data[pn]['doc'][2]))
						log.error("Document date(new): " + str(document_date))
						if data[pn]['doc'][2] > document_date:
							log.error('Stored document is newer. Sciping new values')
							log.error('')
							parsed_eos.append(eos[1])
							continue
						else:
							log.error('Stored document is older. Updating')
					else:
						data[pn] = {}
					
					for item in dt:
						if len(item) != 3:
							log.error('Cant parse this string')
							log.error(item)
							log.error('Skiping')
						else:	
							data[pn][item[0]]=item[2]	

					data[pn]['doc'] = eos
					data[pn]['descr'] = pn_descr[1]
					pickle.dump(data,open('data.p' ,'wb'))

				parsed_eos.append(eos[1])
				log.info(len(data))
				log.info('')

log.info("data length: " + str(len(data)))
pickle.dump(data,open('data.p' ,'wb'))

log.info("pid_summary length: " + str(len(pid_summary))  )
pickle.dump(pid_summary,open('pid_summary.p' ,'wb'))

log.info('pid_bad lenght:' + str(len(pid_bad)))
pickle.dump(pid_bad,open('pid_bad.p' ,'wb'))

log.info("Execution time:" + str(datetime.datetime.now() - startTime))



