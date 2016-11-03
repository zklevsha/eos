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
	data_manual_pns = [i.pn for i in db.session.query(DataManual).all() if i.pn != '']
	print ('Checking from func: ',arr[0] in data_manual_pns)
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

		#PN был добавлен вручную
		row = db.session.query(DataManual).filter_by(pn=pn).first()
		if row is not None:
			log.info('pn in data_manual_pns')
			line = [row.pn,row.description,row.replacement,
							row.endOfSaleDate,row.endOfNewServiceAttachmentDate,
							row.endOfNewServiceContractRenewalDate,
							row.lastDateOfSupport,
							row.sourceTitle,
							row.sourceLink,
							row.notes + ' (Added manually)']
			res_array.append(line)
			continue

		# Нашли всю информацию
		row = db.session.query(Data).filter_by(pn=pn).first()
		if row is not None:                         
			log.info('pn in data') 
			line = [row.pn,row.description,row.replacement,
							row.endOfSaleData,row.endOfNewServiceAttachmentDate,
							row.endOfNewServiceContractRenewalDate,
							row.lastDateOfSupport,
							row.sourceTitle,
							row.sourceLink,
							'OK']
			res_array.append(line)
			continue
			
		# Не смогли нормально распарсить EoS
		row = db.session.query(PidBad).filter_by(pn=pn).first()
		if row is not None:
			line =  [ pn,'N/A','N/A','N/A','N/A','N/A','N/A', row.sourceTitle,row.sourceLink, 'Error parsing EoS doc. For dates please check source link']
			res_array.append(line)
			continue

		# Нет самого EOS
		row = db.session.query(PidSummary).filter_by(pn=pn).first()
		if row is not None:
			log.info('pn in pid_summary')

			# # Приводим даты к единому формату
			if row.endOfSaleDate != 'None Announced':
				row.endOfSaleDate = parse(row.endOfSaleDate).strftime('%B %e, %Y')
			if row.endOfSupportDate != 'None Announced':
				row.endOfSupportDate = parse(row.endOfSupportDate).strftime('%B %e, %Y')
			

			line = [ pn,row.series,'N/A',row.endOfSaleDate,'N/A','N/A',row.endOfSupportDate,row.sourceTitle,row.sourceLink,row.status +  ' (No  specific EOS for this PN)']   
			res_array.append(line)
			continue
		
		else:
			log.error('Cant find this PN')
			line =  [pn,'NULL','NULL','NULL','NULL','NULL','NULL','NULL','NULL','Cant find info about this PN']
			res_array.append(line)
		# if pn_changed:
		# 	line[0] = old_pn

		
	return res_array



def can_delete(pn=None):  
	if pn is not None:
		row = db.session.query(DataManual).first()
		if row is not None:
			return True

	return False

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/eos.db'
app.secret_key = '0330431079'
db = SQLAlchemy(app)

log = get_logger('web')
res_array = []

@app.route("/",methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
    	arr = [s.strip() for s in request.form['input'].splitlines() if s is not ""]
    	if len(arr) == 0:
    		flash('Не указан ни один PN','warning')
    		return redirect(url_for('index'))
    	add_remove_eq = 'check' in request.form # Если true ищем с = и без =
    	table = table_generate(arr,add_remove_eq)
    	return render_template('table.html',header=table[0], data=table[1:])


    else: 
	    return render_template('index.html')


@app.route("/add_update",methods=['GET', 'POST'])
def add():

	form = [
			['PN','pn',''],
			['Description','description',''],
			['Replacement','replacement',''],
			['End-of-Sale Date','endOfSaleDate',''],
			['End of New Service Attachment Date','endOfNewServiceAttachmentDate',''],
			['End of Service Contract Renewal Date','endOfNewServiceContractRenewalDate',''],
			['Last Date of Support','lastDateOfSupport',''],
			['Source Title','sourceTitle',''],
			['Source Link','sourceLink',''],
			['Notes','notes','']
	]

	

	if request.method == 'POST':
		data = request.form.to_dict()
		#print (data)
		#print('here!!!')
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

		flash('Устройсво '+ data['pn'] + ' добавлено','success')
		table = table_generate([data['pn']],False)
	 
		return render_template('table.html',header=table[0], data=table[1:])

	else:
			
		if 'pn' in request.args:	# Изменяем старое
			pn = request.args.get('pn')
			table = table_generate([pn])[1]
			print(table)
			i=0
			for row in form:
				row[-1] =table[i]
				print (row)
				i = i+1 
			form[-1][-1]=''

			return render_template('add_update.html',form=form, can_delete=can_delete(pn))
		else:
			return render_template('add_update.html',form=form, can_delete=False)



@app.route("/delete",methods=['GET', 'POST'])
def delete():
	try:
		print(request.args.get('pn'))
		row = db.session.query(DataManual).filter_by(pn=request.args.get('pn')).first()
		db.session.delete(row)
		db.session.commit()
		flash('Устройство удалено','success')
		return redirect(url_for('index'))
	except Exception as e:
		flash('Не удалось удалить устройство ' +  str(e),'danger')
		return redirect(url_for('index'))

if __name__ == "__main__":
	app.run(debug = True,)



## НЕ ДОЛЖНА ПРИ ЗАПУСКЕ СКРИПТА ПРОИСХОДИТЬ ВЫБОРКА ВСЕХ ДАННЫХ
## ВОТ ЭТО 
#data_manual_pns = [i.pn for i in db.session.query(DataManual).all() if i.pn != '']
#data_pns = [i.pn for i in db.session.query(Data).all() if i.pn != '']
#pid_summary_pns = [i.pn for i in db.session.query(PidSummary).all() if i.pn != '']
#pid_bad_pns = [i.pn for i in db.session.query(PidBad).all() if i.pn != '']

# Убрать!!