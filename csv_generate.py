import csv
import pickle
from  mylibs.utils import get_logger
import sys

data = pickle.load( open('data.p','rb') )

log = get_logger('csv_generate.txt')

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
				 'Source Link']

	cw.writerow(header)

	for data_k in data.keys():
		log.info('Writing pn: ' + data_k)
		dates = data[data_k]
		url = data[data_k]['doc'][1]

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
			print (search_k)

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

			log.info('')

			for i in dates.keys():
				log.info(repr(i))

			log.info('url:' + data[data_k]['doc'][1])
			log.info('')
			log.info(data[data_k])
			sys.exit()

		line =  [ [data_k],first,second,secondApp,third,thirdApp,forth,forthApp, [data[data_k]['doc'][1] ] ]  
		print(line)