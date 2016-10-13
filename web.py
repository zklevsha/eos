import platform
import os
import pickle
from flask import Flask, request, render_template, Response,redirect,url_for,flash
from functools import wraps
from dateutil.parser import parse
from flask_sqlalchemy import SQLAlchemy
from mylibs.utils import *
from db.schema import PidBad,PidSummary,Data,DataManual
from sqlalchemy.exc import IntegrityError




def table_generate(arr,add_remove_eq=False):
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

	if add_remove_eq:
		new_arr = []
		for pn in arr:
			new_arr.append(pn)
			if pn[-1] == '=':
				new_arr.append(pn[:-1])
			else:
				new_arr.append(pn + "=")
		arr = new_arr

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
app.secret_key = '0330431079'
db = SQLAlchemy(app)

log = get_logger('web')
res_array = []
data_manual_pns = [i.pn for i in db.session.query(DataManual).all() if i.pn != '']
data_pns = [i.pn for i in db.session.query(Data).all() if i.pn != '']
pid_summary_pns = [i.pn for i in db.session.query(PidSummary).all() if i.pn != '']
pid_bad_pns = [i.pn for i in db.session.query(PidBad).all() if i.pn != '']

@app.route("/",methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
    	arr = [s.strip() for s in request.form['input'].splitlines() if s is not ""]
    	add_remove_eq = 'check' in request.form # Если true ищем с = и без =
    	table = table_generate(arr,add_remove_eq)
    	return render_template('table.html',header=table[0], data=table[1:])


    else: 
	    return render_template('index.html')


@app.route("/add",methods=['GET', 'POST'])
def add():

	form = [
			['PN','pn'],
			['Description','description'],
			['Replacement','replacement'],
			['End-of-Sale Date','endOfSaleDate'],
			['End of New Service Attachment Date','endOfNewServiceAttachmentDate'],
			['End of Service Contract Renewal Date','endOfNewServiceContractRenewalDate'],
			['Last Date of Support','lastDateOfSupport'],
			['Source Title','sourceTitle'],
			['Source Link','sourceLink'],
			['Notes','notes']
	]

	if request.method == 'POST':
		data = request.form.to_dict()
		print (data)
		print('here!!!')
		try:
			print('i am here')
			add = db.session.add(DataManual(**data))
			print(add)
			db.session.commit()

		except IntegrityError: # Если нарушаем UNIQE CONSTRAIN
			print ('error')
			db.session.rollback()   
			res = db.session.query(DataManual).filter_by(pn=data['pn']).update(data)
			print('res is',res)
			print(data['pn'])
			db.session.commit()
		finally:
			db.session.close()
			print('SESSION CLOSED')

		flash('Device '+ data['pn'] + ' was added to db')
		data_manual_pns = [i.pn for i in db.session.query(DataManual).all() if i.pn != '']
		table = table_generate([data['pn']],False)
		return render_template('table.html',header=table[0], data=table[1:])


	return render_template('add.html',form=form)

if __name__ == "__main__":
	app.run(debug = True,)

