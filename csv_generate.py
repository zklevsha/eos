import csv
import pickle
from  mylibs.utils import get_logger
import sys

data = pickle.load( open('data.p','rb') )
pid_summary = pickle.load( open('pid_summary.p','rb') )
cant_find_dates_pn = pickle.load( open('cant_find_dates_pn.p','rb') )
log = get_logger('csv_generate.txt')


rb = xlrd.open_workbook('old.xlsx')
sheet = rb.sheet_by_index(0)
pns = [sheet.row_values(rownum) for rownum in range(sheet.nrows)]
pns.pop(0)


with open('csv_out.csv', 'w') as csvfile:
	cw = csv.writer(csvfile, delimiter=',')
	header = ['PN',
				'End-of-Sale Date',
				 'End of New Service Attachment Date',
				 'End of New Service Attachment Date App'
				 'End of Service Contract Renewal Date',
				 'End of Service Contract Renewal Date App',
				 'Last Date of Support',
				 'Last Date of Support App',
				 'Source Link','Notes']

	cw.writerow(header)

	for pn in pns:
	log.info('Processing: ' + pn)

	if pn in data.keys()                          # Нашли всю информацию
		log.info('pn in data')

		dates = data[pn]
		url = data[pn]['doc'][1]

		first = []

		second = []
		secondApp = []

		third= []
		thirdApp = []

		forth = []
		forthApp = []

		nonMandatory = [second,secondApp,third,thirdApp,forth,forthApp]

		for k in dates.keys():
			search_k = k.lower().replace('-','').replace(' ','').replace('\n','')

			if 'endofsale' in search_k:
				first.append(dates[k])

			if 'attachment' in search_k:
				if 'app' in search_k:
					secondApp.append(dates[k])
				else:
					second.append(dates[k])

			if 'renewal' in search_k:
				if 'app' in search_k:
					thirdApp.append(dates[k])
				else:
					third.append(dates[k])

			if 'lastdateofsupport' in search_k and 'phone' not in search_k:
				if 'app' in search_k:
					forthApp.append(dates[k])
				else:
					forth.append(dates[k])

		

		if len(first) != 1 or any( len(i) > 1 for i in nonMandatory ):
			log.error('Cant parse ' + data_k)

			for i in [first + nonMandatory]:
				log.error(i)

			log.error('')

			for i in dates.keys():
				log.error(repr(i))

			log.info('url:' + data[pn]['doc'][1])
			log.info('')
			log.info(data[pn])
			sys.exit()
		else:
			line =  [ [pn],first,second,secondApp,third,thirdApp,forth,forthApp, [data[pn]['doc'][1] ], ['OK']  

	elif pn in cant_find_dates_pn.keys(): # Не смогли нормально распарсить EoS
		log.info('pn in cant_find_dates_pn')
		line =  [ [pn],['N/A'],['N/A'],['N/A'],['N/A'],['N/A'],['N/A'],['N/A'], [data[pn]['doc'][1] ], ['Error parsing EoS doc. For dates please check source link']]

	elif pn in pid_summary:
		log.info('pn in pid_summary')
		line = [ [pn],pid_summary['EndOfSale:'],second,secondApp,third,thirdApp,forth,pid_summary['EndOfSupport:'], [data[pn]['doc'][1] ], ['EoS status: ' +pid_summary['Status:'] + ' (No EOS for this PN)' ] ]  

	else:
		log.error('Cant find this PN')
		line =  [ [pn],['NULL'],['NULL'],['NULL'],['NULL'],['NULL'],['NULL'],['NULL'], ['NULL'] ], ['Cant find info about this PN']]


	csvfile.writerow(line)