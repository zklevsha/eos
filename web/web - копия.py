from flask import Flask
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from mylibs.utils import *
import pickle
from dateutil.parser import parse


def table_generate(arr):
	res_array = []
	header = ['PN',
				'End-of-Sale Date',
				 'End of New Service Attachment Date',
				 #'End of New Service Attachment Date App',
				 'End of Service Contract Renewal Date',
				 #'End of Service Contract Renewal Date App',
				 'Last Date of Support',
				 #'Last Date of Support App',
				 'Source Link','Notes','Found as']

	res_array.append(header)

	for pn in arr:
		log.info('Processing: ' + str(pn))
		found_as = pn
		pn_changed = False
		# если не нашли pn с\без "=" то пытаемся найти с\без него
		if all(pn not in i.keys() for i in [data,pid_summary,pid_bad]):
			if pn[-1] == "=":
				new_pn = pn[0:-2]
			else:
				new_pn = pn+"="

			if all(new_pn not in i.keys() for i in [data,pid_summary,pid_bad]):
				log.error('Cant find this PN')
				line =  [pn,'NULL','NULL','NULL','NULL','NULL','Cant find info about this PN','NULL']
				res_array.append(line)
				print('')
				continue

			else:
				old_pn = pn
				pn = new_pn
				pn_changed = True

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

			

			if len(first) != 1 or any( len(i) > 1 for i in nonMandatory ): # Проверяем на ошибке в сборе pn
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
				for item in [first,second,third,forth]:
					try:
						item = item[0]
					except:
						item = 'N/A'
					arr.append(item)

				line = [pn] + arr + [ data[pn]['doc'][1] , 'OK' ,found_as ]


		# Не смогли нормально распарсить EoS
		elif pn in pid_bad.keys(): 
			log.info('pn in pid_bad')
			print ( pid_bad[pn] )
			line =  [ pn,'N/A','N/A','N/A','N/A', pid_bad[pn][1] , 'Error parsing EoS doc. For dates please check source link',found_as]

		# Нет самого EOS
		elif pn in pid_summary: 
			log.info('pn in pid_summary')

			# Приводим даты к единому формату
			if pid_summary[pn]['End-of-Sale Date:'] != 'None Announced':
				pid_summary[pn]['End-of-Sale Date:'] = parse(pid_summary[pn]['End-of-Sale Date:']).strftime('%B %e, %Y')
			if pid_summary[pn]['End-of-Support Date:'] != 'None Announced':
				pid_summary[pn]['End-of-Support Date:'] = parse(pid_summary[pn]['End-of-Support Date:']).strftime('%B %e, %Y')

			line = [ pn,pid_summary[pn]['End-of-Sale Date:'],'N/A','N/A',pid_summary[pn]['End-of-Support Date:'], 
					pid_summary[pn]['doc'][1] ,'EOS status ' + pid_summary[pn]['Status:'] + ' (No  specific EOS for this PN)' ,found_as]   

		
		if pn_changed:
			line[0] = old_pn

		res_array.append(line)
	return res_array









app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
log = get_logger('web',folder='logs')
data = pickle.load(open('data.p','rb'))
pid_summary = pickle.load(open('pid_summary.p','rb'))
pid_bad= pickle.load(open('pid_bad.p','rb'))


@app.route("/",methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
    	print("I got it!")
    	arr = [s.strip() for s in request.form['input'].splitlines() if s is not ""]
    	table = table_generate(arr)
    	for i in table_generate(arr):
        	print (i)
    	print(table[0])
    	return render_template('table.html',header=table[0], data=table[1:])

    else: 
	    return '''
	  <form role="form" method='POST' action='/'>
	   <textarea name="input" cols="40" rows="5"></textarea><br>
	    <input type="submit" value="Submit">
	</form> '''


if __name__ == "__main__":
    app.run(debug = True)
