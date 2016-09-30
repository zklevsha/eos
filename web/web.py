from flask import Flask
from flask import Flask, request, render_template
from db.schema import PidBad,PidSummary,Data
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from mylibs.utils import *
import pickle
from dateutil.parser import parse
import platform
import os


def table_generate(arr):
	res_array = []
	header = ['PN',
				'Description',
				'Replacement',
				'End-of-Sale Date',
				 'End of New Service Attachment Date',
				 'End of Service Contract Renewal Date',
				 'Last Date of Support',
				 'Source Title',
				 'Source Link','Notes']
				 #'Found as']

	res_array.append(header)

	for pn in arr:
		log.info('Processing: ' + str(pn))
		#found_as = pn
		#pn_changed = False
		# # если не нашли pn с\без "=" то пытаемся найти с\без него
		# if all(new_pn not in i for i in [data_pns,pid_summary_pns,pid_bad_pns]):
		# 	if pn[-1] == "=":
		# 		new_pn = pn[0:-2]
		# 	else:
		# 		new_pn = pn+"="

		# 	if all(new_pn not in i for i in [data_pns,pid_summary_pns,pid_bad_pns]):
		# 		log.error('Cant find this PN')
		# 		line =  [pn,'NULL','NULL','NULL','NULL','NULL','Cant find info about this PN','NULL']
		# 		res_array.append(line)
		# 		continue

		# 	else:
		# 		old_pn = pn
		# 		pn = new_pn
		# 		pn_changed = True

		# Нашли всю информацию
		if pn in data_pns:                         
			log.info('pn in data')

			row = db.session.query(Data).filter_by(pn=pn).first() 
			line = [row.pn,row.description,row.replacement,
							row.endOfSaleData,row.endOfNewServiceAttachmentDate,
							row.endOfNewServiceContractRenewalDate,
							row.lastDateOfSupport,
							row.sourceTitle,
							row.sourceLink,
							'OK']
			
		# Не смогли нормально распарсить EoS
		elif pn in pid_bad_pns: 
			row = db.session.query(Bad).filter_by(pn=pn).first()
			line =  [ pn,'N/A','N/A','N/A','N/A','N/A','N/A','N/A', row.sourceTitle,row.sourceLink, 'Error parsing EoS doc. For dates please check source link']

		# Нет самого EOS
		elif pn in pid_summary_pns: 
			log.info('pn in pid_summary')

			row = db.session.query(PidSummary).filter_by(pn=pn).first()
			
			# # Приводим даты к единому формату
			if row.endOfSaleDate != 'None Announced':
				row.endOfSaleDate = parse(row.endOfSaleDate).strftime('%B %e, %Y')
			if row.endOfSupportDate != 'None Announced':
				row.endOfSupportDate = parse(row.endOfSupportDate).strftime('%B %e, %Y')
			

			line = [ pn,row.series,'N/A',row.endOfSaleDate,'N/A',row.endOfSupportDate,row.sourceTitle,row.sourceLink, row.status + ' (No  specific EOS for this PN)']   

		
		else:
			log.error('Cant find this PN')
			line =  [pn,'NULL','NULL','NULL','NULL','NULL','NULL','NULL','NULL','Cant find info about this PN']

		# if pn_changed:
		# 	line[0] = old_pn

		res_array.append(line)
	return res_array


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/eos2.db'
db = SQLAlchemy(app)

log = get_logger('web',folder='logs')

data_pns = [i.pn for i in db.session.query(Data).all() if i.pn != '']
pid_summary_pns = [i.pn for i in db.session.query(PidSummary).all() if i.pn != '']
pid_bad_pns = [i.pn for i in db.session.query(PidBad).all() if i.pn != '']

@app.route("/",methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
    	print("I got it!")
    	arr = [s.strip() for s in request.form['input'].splitlines() if s is not ""]
    	table = table_generate(arr)
    	print (table)
    	return render_template('table.html',header=table[0], data=table[1:])

    else: 
	    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug = True)
