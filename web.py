import platform
import os
import pickle
from flask import Flask
from flask import Flask, request, render_template
from dateutil.parser import parse
from flask_sqlalchemy import SQLAlchemy
from mylibs.utils import *
from db.schema import PidBad,PidSummary,Data




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
			row = db.session.query(PidBad).filter_by(pn=pn).first()
			line =  [ pn,'N/A','N/A','N/A','N/A','N/A','N/A', row.sourceTitle,row.sourceLink, 'Error parsing EoS doc. For dates please check source link']

		# Нет самого EOS
		elif pn in pid_summary_pns: 
			log.info('pn in pid_summary')

			row = db.session.query(PidSummary).filter_by(pn=pn).first()
			
			# # Приводим даты к единому формату
			if row.endOfSaleDate != 'None Announced':
				row.endOfSaleDate = parse(row.endOfSaleDate).strftime('%B %e, %Y')
			if row.endOfSupportDate != 'None Announced':
				row.endOfSupportDate = parse(row.endOfSupportDate).strftime('%B %e, %Y')
			

			line = [ pn,row.series,'N/A',row.endOfSaleDate,'N/A','N/A',row.endOfSupportDate,row.sourceTitle,row.sourceLink,row.status +  ' (No  specific EOS for this PN)']   

		
		else:
			log.error('Cant find this PN')
			line =  [pn,'NULL','NULL','NULL','NULL','NULL','NULL','NULL','NULL','Cant find info about this PN']

		# if pn_changed:
		# 	line[0] = old_pn

		res_array.append(line)
	return res_array


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/eos.db'
db = SQLAlchemy(app)

log = get_logger('web')

data_pns = [i.pn for i in db.session.query(Data).all() if i.pn != '']
pid_summary_pns = [i.pn for i in db.session.query(PidSummary).all() if i.pn != '']
pid_bad_pns = [i.pn for i in db.session.query(PidBad).all() if i.pn != '']

@app.route("/",methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
    	arr = [s.strip() for s in request.form['input'].splitlines() if s is not ""]
    	table = table_generate(arr)
    	return render_template('table.html',header=table[0], data=table[1:])

    else: 
	    return render_template('index.html')


if __name__ == "__main__":
	app.run(debug = True,host='0.0.0.0')
