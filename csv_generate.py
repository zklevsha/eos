import csv
import pickle
from  mylibs.utils import get_logger
data = pickle.load( open('data.p','rb') )

log = get_logger('csv_generate.txt')

with open('csv_out.csv', 'w') as csvfile:
	cw = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
	header = ['End-of-Sale Date',
				 'End of New Service Attachment Date',
				 'End of New Service Attachment Date App'
				 'End of Service Contract Renewal Date',
				 'End of Service Contract Renewal Date App',
				 'Last Date of Support',
				 'Last Date of Support App']

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
			if 'End-of-Sale' in k:
				first.append(dates[k])

			if 'Attachment' in k:
				if 'App' in k:
					secondApp.append(dates[k])
				else:
					second.append(dates[k])

			if 'Renewal' in k and 'App' not in k:
				if 'App' in 'k':
					thirdApp.append(dates[k])
				else:
					third.append(dates[k])

			if 'Support' in k and 'Phone' not in k:
				if 'App' in k:
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

			sys.exit()

		else:
			
			for i in nonMandatory:
				if len(i) == 0:
					i = ['N/A']

			cw.writerow( [ i[0] for i in [first + nonMandatory] ] )