
from sqlalchemy import create_engine
from db.schema import PidBad,PidSummary,Data
from sqlalchemy.orm import sessionmaker
import pickle
import sys
import os
engine = create_engine('sqlite:///db/eos.db',echo=True) 
session = sessionmaker(bind=engine)()
os.system('chcp 65001')


# pid_summary_pns = [i.pn for i in session.query(PidSummary).all() if i.pn != '']
# print(pid_summary_pns)



# pid_bad = pickle.load(open('pid_bad.p','rb'))

# for pk in pid_bad:
# 	print(pk)
# 	row = PidBad(
# 		pn = pk,
# 		sourceTitle = pid_bad[pk][0],
# 		sourceLink=pid_bad[pk][1]
# 	)
# 	session.add(row)
# 	session.commit()

# pid_summary = pickle.load(open('pid_summary.p','rb'))


# for pid_summary_k in pid_summary.keys():
# 	print(pid_summary_k)
# 	device = pid_summary[pid_summary_k]

# 	keys = ['Status:','End-of-Sale Date:','End-of-Support Date:','Series:','doc']

# 	for k in keys:
# 		try:
# 			device[k]
# 		except KeyError:
# 			device[k] = 'N/A'

# 	row = PidSummary(
# 				pn=pid_summary_k,
# 				status=device['Status:'],
# 				endOfSaleDate = device['End-of-Sale Date:'],
# 				endOfSupportDate=device['End-of-Support Date:'],
# 				series=device['Series:'],
# 				sourceTitle = device['doc'][0],
# 				sourceLink = device['doc'][1]
# 			)

# 	session.add(row)
# 	session.commit()
	






def data_normalize(data):
	res = []
	for data_k in data.keys():
		endofsale = []
		attachment = []
		renewal = []
		lastdateofsupport = []
		description = []
		sourceLink= ""
		sourceTitle = ""
		replacement = []
		dev = data[data_k]
		#print (dev)
		for k in dev.keys():
			search_k = k.lower().replace('-','').replace(' ','').replace('\n','')
			if 'endofsale' in search_k:
				if len(k.split(':')) == 2:
					dev[k] = k.split(':')[1]+":"+dev[k] # Добавляем HW,SW,OS
				endofsale.append(dev[k])

			if 'attachment' in search_k:
				if len(k.split(':')) == 2:
					dev[k] = k.split(':')[1]+":"+dev[k]
				attachment.append(dev[k])

			if 'renewal' in search_k:
				if len(k.split(':')) == 2:
					dev[k] = k.split(':')[1]+":"+dev[k]
				renewal.append(dev[k])

			if 'lastdateofsupport' in search_k and 'phone' not in search_k:
				if len(k.split(':')) == 2:
					dev[k] = k.split(':')[1]+":"+dev[k]
				lastdateofsupport.append(dev[k])

			if k == 'description':
				description.append(dev[k])

			if k == 'replacement':
				replacement = dev[k]

			if k == "doc":
				sourceTitle = dev[k][0]
				sourceLink = dev[k][1]

		# device = Data(
		# 		pn=data_k,
		# 		description=' '.join(description),
		# 		endOfSaleData=' '.join(endofsale),
		# 		endOfNewServiceAttachmentDate = ' '.join(attachment),
		# 		endOfNewServiceContractRenewalDate = ' '.join(renewal),
		# 		lastDateOfSupport=' '.join(lastdateofsupport),
		# 		replacement = ' '.join(replacement),
		# 		sourceTitle = sourceTitle,
		# 		sourceLink = sourceLink	
		# 	)


		device = {
				'pn':data_k,
				'description':' '.join(description),
				'endOfSaleData':' '.join(endofsale),
				'endOfNewServiceAttachmentDate' : ' '.join(attachment),
				'endOfNewServiceContractRenewalDate' : ' '.join(renewal),
				'lastDateOfSupport':' '.join(lastdateofsupport),
				'replacement' : ' '.join(replacement),
				'sourceTitle' : sourceTitle,
				'sourceLink' : sourceLink	
			}
		#print('resulted device is ', device.pn,device.description)
		res.append(device)
	return res
			


def pid_bad_normalize(pid_bad):
	rows = []
	for k in pid_bad.keys():
		item = pid_bad[k]
		row = {'pn':k, 'sourceTitle':item[0], 'sourceLink':item[1] } 
		rows.append(row)
	return rows




def pid_summary_normalize(pid_summary):
	rows = []
	for k in pid_summary.keys():
		item = pid_summary[k]
		for   check  in ['series','endOfSaleData','endOfSupportDate','series','sourceTitle','sourceLink']:
			if check not in item.keys(): 
				item[check] = 'N/A'

		row = {
				'pn':k, 
				'status':item['status'],
				'endOfSaleDate':item['endOfSaleDate'],
				'endOfSupportDate':item['endOfSupportDate'],
				'series':item['series'],
				'sourceTitle':item['sourceTitle'], 
				'sourceLink':item['sourceLink'] 
			} 
		rows.append(row)
	return rows