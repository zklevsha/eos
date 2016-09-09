import csv
from mylibs.utils import get_logger 
import sys
from dateutil.parser import parse

log = get_logger('test_csv.txt')
old = [row for row in csv.reader(open('old.csv','r'), delimiter=';')]
new = [row for row in csv.reader(open('csv_out.csv','r'), delimiter=',') if len(row) != 0 ]
#for i in new: print(i)

#['PN', 'End-of-Sale Date', 'End of New Service Attachment Date', 'End of Service Contract Renewal Date', 'Last Date of Support']


for i in range(1,950):

	ol = old[i]
	nl = new[i]
	log.info('Checking ' + ol[0])
	if ol[0] != nl[0]:
		log.error('PN not match')
		log.error('Old = ' +  ol[0])
		log.error('New = ' + nl[0])
		sys.exit()

	if ol[1] == "":
		log.error('old date is null skipping')
		log.error('')
		continue

	for a in range(1,len(ol) - 1):
		#print(ol[a])
		if nl[a] == 'NULL' or nl[a] == 'N/A':
			continue  
		try:
			if parse(ol[a]).strftime('%B %e, %Y') != parse(nl[a]).strftime('%B %e, %Y'):
				log.error(old[0][a] + ' is not equal')
				log.error('Old: ' + str(ol[a]))
				log.error('New: ' + str(nl[a]))
				sys.exit()
		except:
			if ol[a] == "":
				continue
			print('Error')
			print('Old value', ol[a])
			print('New value',nl[a])
			sys.exit()

	log.error('')