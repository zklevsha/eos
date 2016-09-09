import csv
import pickle
from  mylibs.utils import get_logger
import sys
import xlrd
import os
from dateutil.parser import parse

if len(sys.argv) != 2:
	print('Usage :' + sys.argv[0] + ' filename.xlsx')
	sys.exit(0) 

filename = sys.argv[1]

if not os.path.isfile(filename):
	print('Cant find file ' + filename)
	sys.exit()

# if '-app' in sys.argv:
# 	need_app = True
# if '-os' in sys.argv:
# 	need_os = True


data = pickle.load( open('data.p','rb') )
pid_summary = pickle.load( open('pid_summary.p','rb') )
pid_bad = pickle.load( open('pid_bad.p','rb') )
log = get_logger('csv_generate.txt')




rb = xlrd.open_workbook(filename)
sheet = rb.sheet_by_index(0)
pns = [sheet.row_values(rownum)[0] for rownum in range(sheet.nrows)]
pns.pop(0)


with open('csv_out.csv', 'w') as csvfile:
	cw = csv.writer(csvfile, delimiter=',')
	header = ['PN',
				'End-of-Sale Date',
				 'End of New Service Attachment Date',
				 #'End of New Service Attachment Date App',
				 'End of Service Contract Renewal Date',
				 #'End of Service Contract Renewal Date App',
				 'Last Date of Support',
				 #'Last Date of Support App',
				 'Source Link','Notes']

	cw.writerow(header)

	for pn in pns:
		log.info('Processing: ' + str(pn))

		# Нашли всю информацию
		if pn in data.keys():                         
			log.info('pn in data')

			dates = data[pn]
			url = data[pn]['doc'][1]

			first = []

			second = []
			#secondApp = []

			third= []
			#thirdApp = []

			forth = []
			#forthApp = []

			#nonMandatory = [second,secondApp,third,thirdApp,forth,forthApp]
			nonMandatory = [second,second,third,forth]
			for k in dates.keys():
				search_k = k.lower().replace('-','').replace(' ','').replace('\n','')

				if 'endofsale' in search_k:
					first.append(dates[k])

				if 'attachment' in search_k:
					#if 'app.sw' in search_k:
					#	secondApp.append(dates[k])
					if 'hw' in search_k:
						second.append(dates[k])

				if 'renewal' in search_k:
					#if 'app.sw' in search_k:
					#	thirdApp.append(dates[k])
					if 'hw' in search_k:
						third.append(dates[k])

				if 'lastdateofsupport' in search_k and 'phone' not in search_k:
					#if 'app.sw' in search_k:
					#	forthApp.append(dates[k])
					if 'hw' in search_k:
						forth.append(dates[k])

			

			if len(first) != 1 or any( len(i) > 1 for i in nonMandatory ):
				log.error('Cant parse ' + pn)

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
				arr = []
				#for item in [first,second,secondApp,third,thirdApp,forth,forthApp]: # Преобразуем массивы в строки
				for item in [first,second,third,forth]:
					try:
						item = item[0]
					except:
						item = 'N/A'
					arr.append(item)
				#line =  [ pn,first,second,secondApp,third,thirdApp,forth,forthApp, data[pn]['doc'][1] , 'OK' ]
				line = [pn] + arr + [ data[pn]['doc'][1] , 'OK' ]
		# Не смогли нормально распарсить EoS
		elif pn in pid_bad.keys(): 
			log.info('pn in pid_bad')
			print ( pid_bad[pn] )
			#line =  [ pn,'N/A','N/A','N/A','N/A','N/A','N/A','N/A', pid_bad[pn][1] , 'Error parsing EoS doc. For dates please check source link']
			line =  [ pn,'N/A','N/A','N/A','N/A', pid_bad[pn][1] , 'Error parsing EoS doc. For dates please check source link']
		# Нет самого EOS
		elif pn in pid_summary: 
			log.info('pn in pid_summary')

			if pid_summary[pn]['End-of-Sale Date:'] != 'None Announced':
				pid_summary[pn]['End-of-Sale Date:'] = parse(pid_summary[pn]['End-of-Sale Date:']).strftime('%B %e, %Y')

			if pid_summary[pn]['End-of-Support Date:'] != 'None Announced':
				pid_summary[pn]['End-of-Support Date:'] = parse(pid_summary[pn]['End-of-Support Date:']).strftime('%B %e, %Y')

			line = [ pn,pid_summary[pn]['End-of-Sale Date:'],'N/A','N/A',pid_summary[pn]['End-of-Support Date:'], 
					pid_summary[pn]['doc'][1] ,'EOS status ' + pid_summary[pn]['Status:'] + ' (No  specific EOS for this PN)' ]   

		else:
			log.error('Cant find this PN')
			line =  [ pn,'NULL','NULL','NULL','NULL','NULL','Cant find info about this PN' ]

		cw.writerow(line)
		print('')


		# dont forget return doc