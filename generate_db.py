import json
import pickle
import sys
import datetime
import platform
import os
import threading
import queue
import time
import shutil
from db.db_utils import *
from db.schema import Data,PidSummary,PidBad
from mylibs.utils import *
from bs4 import BeautifulSoup, SoupStrainer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from dateutil.parser import parse
import traceback


#FUNCTIONS

def support_get_eos(name,q):
    while not exitFlag:
        queueLock.acquire()
        log.info('Lock acquried')
        try:
            if not q.empty():
                device = q.get()
                queueLock.release()
                log.info('Lock released')
                log.info("%s processing %s" % (name, device))
                log.info('Checking ' + str(device[0]) + ' series')
                log.info("url:" + device[1])
                #searcing for eos-listing  link
                content = get_page(device[1])
                if content.status_code != 200 :
                    log.error('Error code :' + str(content.status_code)+" url " + device[1])
                    continue

                
                soup = BeautifulSoup(content.text,"html.parser")
                strainer = SoupStrainer("div",{'id':'models-in-series'},)
                soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)


                devices_in_series = [ (link.text,header+link['href']) for link in soup.findAll('a', href=True) ]


                if len(devices_in_series) == 0:
                    log.error('Cant find devices for this serices')
                    log.error(device)
                    continue

                log.info('Found ' + str( len(devices_in_series) )  + ' models')
                log.info(" ")
                for model in devices_in_series:
                    log.info('Parsing ' + model[0])
                    log.info(model[1])


                    content = get_page(model[1])


                    log.info('Gathering PN assosiated with this device and some eos info')
                    strainer = SoupStrainer("ul",{'id':'birth-cert-pids'})
                    soup = BeautifulSoup(content.text,'html.parser',parse_only=strainer)

                    if soup is not None:
                        pids = [ li.text for li in soup.findAll('li') ]
                    else: 
                        pass

                    strainer = SoupStrainer("table",{'class':'birth-cert-table'})
                    soup = BeautifulSoup(content.text,'html.parser',parse_only=strainer)

                    what_we_need = ['Series:','Status:','End-of-Sale Date:','End-of-Support Date:']
                    pid_info = {}
                    for row in soup.findAll('tr'):
                        try: # Если не найдем k или v, то пропускаем
                            k = row.find('th').text
                            v = row.find('td').text
                            if any(k == i for i in what_we_need):

                                v = ' '.join(v.replace('Details','').split())
                                k = k.replace('Status:','status').replace('End-of-Sale Date:','endOfSaleDate')
                                k = k.replace('Series:','series').replace('End-of-Support Date:','endOfSupportDate')

                                if k == 'Status:': # Удаляем лишнее. Оставляем только Orderable, End Of Sale, End Of Support
                                    pid_info[k] = v.replace('End-of-Sale','EndOfSale').replace('End-of-Support','EndOfSupport').split()[0]
                                else:
                                    pid_info[k] = v

                        except Exception as e: 
                            pass  

                    pid_info['sourceTitle'] = model[0]
                    pid_info['sourceLink'] = model[1]
                    
                    queueLock.acquire()
                    log.info('Lock acquried')
                    for p in pids:          # Стараемся найти хоть один сайт в котором есть None Annonced для нашей железки. Если находим
                        log.info(p)
                        if p in pid_summary:# такую то записываем самую позднюю дату
                            if  'None' in pid_summary[p]['endOfSaleDate']:
                                pass
                            elif 'None' in pid_info['endOfSaleDate']:
                                pid_summary[p]=pid_info
                            else:
                                old = parse(pid_summary[p]['endOfSaleDate'])
                                new = parse(pid_info['endOfSaleDate'])
                                if new > old:
                                    pid_summary[p] = pid_info
        
                                # try:
                                #     old = parser(pid_summary[p]['endOfSaleDate'])
                                #     new = parser(pid_info['endOfSaleDate'])
                                #     if new > old :
                                #         pid_summary[p] = pid_info[p]
                                # except:
                                #     log.critical('dateparse error at pid_summary. old:' + repr(pid_summary[p]['endOfSaleDate'])+' '+ 'new:' +repr(pid_info['endOfSaleDate']) )
                                #     log.critical('saving old data')
                                #     log.critical('old data',pid_summary[p])
                                #     log.critical('new data',pid_info)
                        else:

                             pid_summary[p]=pid_info
                    queueLock.release()
                    log.info('Lock released')

                    log.info('Done. Found ' + str(len(pids)) + ' pids' )

                    log.info('Searching for EOS documents')
                    soup = BeautifulSoup(content.text,"html.parser")
                    a = soup.find('a',{'id':'End-of-LifeandEnd-of-SaleNotices'})
                    if a is None:
                        log.info('There are no EOS for this device. Skiping')
                        log.info(' ')
                        continue
                    uls = a.find_next('ul')
                    
                    eos_pages = [(link.text,link['href']) for link in uls.findAll('a', href=True) if '-fr' not in link['href']]
                    queueLock.acquire()
                    log.info('Lock acquried')
                    for eos_page in eos_pages:
                        if eos_page[1][0] == '/':eos_page = (eos_page[0],header+eos_page[1])

                        if eos_page not in all_eos_pages:
                            all_eos_pages.append(eos_page)

                    queueLock.release()
                    log.info('Lock released')
            else:
                queueLock.release()
                log.info('Queue is empty. Lock is released')
        except:
            log.exception('Exeption:')


def products_get_eos(name,q):
   while not exitFlag:
        queueLock.acquire()
        try:
            if not q.empty():
                url = q.get()
                queueLock.release()
                log.info('Lock released')
                log.info("%s processing %s" % (name, url))
                content = get_page(url[1])
                soup = BeautifulSoup(content.text,"html.parser")
                listings = [link['href'] for link in soup.findAll('a', href=True)  if 'eos-eol-notice-listing.html' in link['href']]
                log.info('Done')
                log.info('Gathering eos pages')
                for listing in listings:
                    if listing[0] == '/': listing = header+listing

                    if listing not in parsed_eos_listing_products:
                        content = get_page(listing)
                        strainer = SoupStrainer("ul",{'class':'listing'},)
                        soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
                        eos_product_page = [ (link.text,header+link['href']) for link in soup.findAll('a', href=True)  if '-fr' not in link['href']]
                        queueLock.acquire()
                        log.info('Lock acquried')
                        for i in eos_product_page:
                            if i[1][0] == '/':i = (i[0],header+i[1])
                            if i not in all_eos_pages:
                                all_eos_pages.append(i)
                        parsed_eos_listing_products.append(listing)
                        queueLock.release()
                        log.info('Lock released')
                log.info('Done')
            else:
                queueLock.release()
                log.info('Queue is empty. Lock  released')

        except Exception as e:
            log.exception('Exeption:')

def parse_eos(name,q):
    while not exitFlag:
        queueLock.acquire()
        log.info('Lock acquried')
        try:
            if not q.empty():
                eos = q.get()
                queueLock.release()
                log.info('Lock released')
                log.info("%s processing %s" % (name, eos))
                if eos[1][0] == '/':eos = (eos[0],header+eos[1]) # Нужен абсолютный путь

                log.info('Title:' + str(eos[0]))
                log.info('Url:' + str(eos[1]))

                if "Change in Product Part Number Announcement" in eos[0]:
                    log.info('This one not EOS page but only information about EoS change. Skiping')
                    log.info(' ')
                    continue

                content = get_page(eos[1].replace('.pdf','.html'))

                if content.status_code != 200:
                    log.error('cant open url ' + eos[1] +  ' Skiping' )
                    log.error('')
                    continue

                soup = BeautifulSoup(content.text,"html.parser")

                document_date = soup.find("div",{"class":"updatedDate"})
                if document_date is None:
                    document_date = parse ("jun 1 100")
                else:
                    document_date = parse(document_date.text.replace("Updated:",""))

                eos = (eos[0],eos[1],document_date)
                
                dates = {}
                devices = {}
                dv_dt = []

                p = soup.find_all('p',{'class':'pTableCaptionCMT'})
                for item in p:
                    if "milestone" in item.text.lower().replace(' ','').replace('-','').replace('\n',''):
                        date_soup = BeautifulSoup( str(item.find_next('table')) , "html.parser" )
                        if date_soup.string != 'None':
                            dates[item.text] = date_soup
                            log.info("Added to Dates "+ item.text)

                    devices_caption = ['productpartnumbersassociated','productpartnumbersaffected',
                    'productpartnumberaffected','productpartnumbersbeingaffected','endofsalepartnumbers']
                    search = item.text.lower().replace('-','').replace(' ','').replace('\n','')\

                    if any( i in search for i in devices_caption) and "Software" not in item.text and "Milestone" not in item.text:
                        device_soup = BeautifulSoup( str(item.find_next('table')) , "html.parser" )
                        if device_soup.string != 'None':
                            devices[item.text] = device_soup
                            log.info("Added to Devices " + item.text)

                if len(devices) == 0:
                    #some eos ( somftware mainly) not have pn
                    if 'Cisco IOS' in content.text or 'Cisco IOS Software Release' in content.text or 'OS Release' in content.text:
                        log.info('Looks like this is software page, so no PN for this one')
                        log.info(' ')
                        continue
                
                    log.error('Cant find table with devices.Skiping')
                    log.error(eos)
                    log.error('')
                    continue

                if len(dates) == 0:
                    if "has been replaced" in content.text or "THIS ANNOUNCEMENT WAS REPLACED" in content.text or 'THIS ANNOUNCEMENT HAS BEEN REDIRECTED' in content.text:
                        log.info('This EOS was replaced. Skiping')
                        log.info('')
                        continue
                    try:
                        retraction_header = ['retraction', 'retracted' ]
                        search = soup.find('h1',{'id':'fw-pagetitle'}).text.lower().replace(' ','').replace('-','').replace('\n','')
                        if  any(i in search for i in retraction_header):
                            log.info('This is page about retraction of some PN. Skiping')
                            log.info('')
                            continue
                    except:
                            log.error('Error parsing page. Cant find header(id=fw-pagetitle):')
                            

                    log.error('Cant parse dates. Adding PN to pid_bad dictionary')
                    log.error(eos)
                    for dvk in devices.keys():
                        dv = get_table(devices[dvk],log)
                        pns = [ i[0].replace(" ", "").replace('\n','') for i in dv if all(i[0] != a for a in ['Change','null']) ]
                        pns.pop(0)

                        for pn in pns:
                            queueLock.acquire()
                            log.info('Lock acquried')
                            pid_bad[pn] = eos
                            queueLock.release()
                            log.info('Lock released')
                        log.error('Added ' + str(len(pns)) + 'pns')
                    log.error('Done.')
                    log.error('')
                    continue

                if len(dates) != len(devices):
                    log.error('Number of table with devices  and  table with devices  are not equal')
                    log.error(eos)
                    if len(devices) > 0:
                        log.error('Adding PN to pid_bad dictionary')
                        for dvk in devices.keys():
                            dv = get_table(devices[dvk],log)
                            pns = [ i[0].replace(" ", "").replace('\n','') for i in dv if all(i[0] != a for a in ['Change','null']) ]
                            pns.pop(0)

                            for pn in pns:
                                queueLock.acquire()
                                log.info('Lock acquried')
                                pid_bad[pn] = eos
                                queueLock.release()
                                log.info('Lock released')
                            log.error(' Added ' + str(len(pns)) + 'pns')
                        log.error('Done')
                        log.error('')
                        continue
                    else:
                        log.error('Cant find any device for this page. Skipping')
                        log.error('')
                        continue

                if len(dates) == 1:
                    dv = [i for i  in devices.keys()][0]
                    dt = [i for i  in dates.keys()][0]
                    dv_dt.append((dv,dt))
                else:   
                    for devk in devices.keys():
                        st = devk[-3:].replace(' ','')
                        for datk in dates.keys():
                            log.info(datk)
                            if st in datk: 
                                dv_dt.append((devk,datk))


                if len(dates) != len(dv_dt):
                    log.error('Error creating dv_dt')
                    log.error(eos)
                    log.error('Adding PN to pid_bad dictionary')
                    for dvk in devices.keys():
                        dv = get_table(devices[dvk],log)
                        pns = [ i[0].replace(" ", "").replace('\n','') for i in dv if all(i[0] != a for a in ['Change','null']) ]
                        pns.pop(0)
                        for pn in pns:
                            queueLock.acquire()
                            log.info('Lock acquried')
                            pid_bad[pn] = eos
                            queueLock.release()
                            log.info('Lock released')

                        log.error(' Added ' + str(len(pns)) + 'pns')
                    log.error('Done')
                    log.info('')
                    continue

                
               

                log.info('This page have '+ str(len(dates)) + ' dv dt pairs')
                for dvk,dtk in dv_dt:
                    log.info('Device title ' + dvk)
                    dv = get_table(devices[dvk],log)
                    log.info('Assosiate dates title ' + dtk)
                    dt = get_table(dates[dtk],log)
                    dt.pop(0)
                    dv_header = [i.replace(" ","").replace('\n','').replace('\xa0','') for i in dv[0]]
                    pns = [ [i[0].replace(" ", "").replace('\n','')] + i[1:] for i in dv if all(i[0] != a for a in ['Change','null']) ] 
                    
                    dv_index = {}
                    for i in dv_header:
                         if i == "ProductDescription":
                            dv_index['description'] = dv_header.index(i)
                         if i == "ReplacementProductPartNumber":
                            dv_index['replacement'] = dv_header.index(i)
                            
                        
                    pns.pop(0)
                    log.info('Adding pn to dictionary')
                    for pn_row in pns:
                        pn = pn_row[0]
                        log.info("pn:" + str(pn))

                        # check for duplicate keys
                        queueLock.acquire() #  < ------------------------------------------ lock starts here 
                        log.info('Lock acquried')
                        if pn in data.keys():
                            log.error('Duplicate PN ' + str(pn))
                            log.error('Stored doc url :'+ data[pn]['doc'][1])
                            if data[pn]['doc'][1] == eos[1] :
                                log.info('There are duplicate pn in same eos document')
                                log.info('Adding replacement device pn to our PN')
                                try:
                                    data[pn]['replacement'].append(pn_row[dv_index['replacement']])
                                except KeyError:
                                    log.error('No Replacement column. Here are table header: '+ str(dv_header))
                                queueLock.release()
                                log.info('Lock released')
                                continue 
                            log.error("Document date(stored):"  + str(data[pn]['doc'][2]))
                            log.error("Document date(new): " + str(document_date))
                            if data[pn]['doc'][2] > document_date:
                                log.error('Stored document is newer. Sciping new values')
                                log.error('')
                                queueLock.release() # < -------------------------------- lock finishied here (first case)
                                log.info('Lock released')
                                continue
                            else:
                                log.error('Stored document is older. Updating')
                                data[pn]={}
                                data[pn]['replacement'] = []
                        
                        else:
                            data[pn] = {}
                            data[pn]['replacement'] = []
                        
                        for item in dt:
                            if len(item) != 3:
                                log.error('Cant parse this string')
                                log.error(item)
                                log.error('Skiping')
                            else:   
                                data[pn][item[0]]=item[2]
                                
                        data[pn]['doc'] = eos

                        try:
                            data[pn]['description'] = pn_row[dv_index['description']]
                        except KeyError:
                            log.error('No Description column. Here are table header: '+ str(dv_header)  )
                            data[pn]['description'] = "N/A"

                        try:
                            data[pn]['replacement'] = [ pn_row[ dv_index['replacement'] ] ]
                        except KeyError:
                            log.error('No Replacement column. Here are table header: '+ str(dv_header) )
                            data[pn]['replacement'].append("N/A")
                            
                        queueLock.release() # < ------------------------------------------ lock finished here (second case)
                        log.info('Lock released')
            else:
                queueLock.release()
                log.info('Queue is empty. Release Lock')

        except Exception as e:
            log.exception('Exeption:')


def control(name,q):
    last_qs = 0
    err_counter = 0
    while not exitFlag:
        try:
            if not q.empty():
                qs = q.qsize()
                if last_qs == qs:
                    if err_counter == 4:
                        log.critical('Queue does not changed for 60 seconds, releasing stucked lock')
                        queueLock.release()
                        err_counter = 0
                    else:
                        err_counter = err_counter + 1
                        log.critical ('Queue does not changed for '  + str(15*err_counter) + ' seconds')
                else:
                    err_counter = 0

                last_qs = qs
                log.info('CONTROL: Queue length:'  + str(q.qsize()))
                time.sleep(15)
            else:
                log.info('Queue is empty.')
        except Exception as e:
            log.critical(e)


class myThread(threading.Thread):
    def __init__(self,name,worker_func,q,log):  
        threading.Thread.__init__(self)
        self.name = name
        self.worker_func = worker_func
        self.q = q

    def run(self):
        log.info("Starting " + self.name)
        self.worker_func(self.name,self.q)
        log.info("Exiting " + self.name)



# VARIABLES
header = "http://www.cisco.com"
all_device_support_page = []
workers_names = ['Wokrer-' + str(i) for i in range(100)]
support_deviceTypes = ['routers','switches','security','wireless','serversunifiedcomputing','applicationnetworkingservices',
                'cloudandsystemsmanagement',
                'collaborationendpoints','conferencing','connectedsafetyandsecurity',
                'customercollaboration','ciscointerfacesandmodules',
                'opticalnetworking','serviceexchange','storagenetworking',
                'video']

DEBUG = False


# SHARED VARIABLES
data = {}
pid_summary = {}
pid_bad = {}
log = get_logger('treads')
parsed_eos_listing_products = []
all_eos_pages = []  # - для всех eos которые нашли
parsed_pages = [] # для пропасенных eos и support страниц
pid_info_array =[] # В данном списке будут строки для добавления в PidSummary
root = os.path.dirname(os.path.abspath(sys.argv[0]))





# ENTRY POINT

if os.path.isfile(os.path.join(root,'db/eos.db')):
    log.info('Backing old eos.db')
    shutil.copy('db/eos.db','db/bak/eos_bak.db' )
engine = create_engine('sqlite:///db/eos.db',echo=False) 
session = sessionmaker(bind=engine)()

startTime = datetime.datetime.now()
log.info('Starting script at ' + str(startTime) )
if platform.system() =="Windows":
	os.system('chcp 65001') # for windows systems only


#Парсим http://www.cisco.com/c/en/us/products/index.html#products
log.info('PHASE 1: GATHERING EOS FROM PRODUCTS  ')
log.info('Gathering products from http://www.cisco.com/c/en/us/products/a-to-z-series-index.html#all')
content = get_page('http://www.cisco.com/c/en/us/products/a-to-z-series-index.html#all')	
strainer = SoupStrainer("div",{'class':'list-section'},)
soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
products = [ (link.text,header+link['href']) for link in soup.findAll('a', href=True) ]
log.info('Done')

log.info('Gathering devices from eos list (http://www.cisco.com/c/en/us/products/eos-eol-listing.html) ')
content = get_page('http://www.cisco.com/c/en/us/products/eos-eol-listing.html')	
strainer = SoupStrainer("div",{'class':'eol-listing-cq section'},)
soup = BeautifulSoup(content.text,"html.parser",parse_only=strainer)
eos_products = [ (link.text,header+link['href']) for link in soup.findAll('a', href=True) ]
products  = products + eos_products
log.info('Done')

q = queue.Queue()
queueLock = threading.Lock()
for i in products: q.put(i)
log.info('Starting workers')
exitFlag = 0
workers =[]
for name in workers_names:
    thread = myThread(name,products_get_eos,q,log)
    thread.start()
    workers.append(thread)

thread = myThread('control',control,q,log)
thread.start()
workers.append(thread)
   
# Wait for queue to empty
while not q.empty():
    pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in workers:
    t.join()

log.info('P1: All treads have finished')

log.info('PHASE 2: COLLECTING EOS FROM SUPPORT')
for device in support_deviceTypes:
  log.info('Gathering ' + device)
  content = get_page("http://www.cisco.com/c/dam/en/us/support/home/json/overlays/"+device+".json")
  diction = json.loads(content.text)
  #json['subCats'][0]['series'][6]

  for subcat in diction['subCats']:
      for model in subcat['series']:
          all_device_support_page.append( (model['title'],header + model['url']) )

if DEBUG:
    psave(all_device_support_page,'all_device_support_page')

log.info("Done.")


q = queue.Queue()
queueLock = threading.Lock()
for i in all_device_support_page: q.put(i)
exitFlag = 0
workers =[]
for name in workers_names:
    thread = myThread(name,support_get_eos,q,log)
    thread.start()
    workers.append(thread)

thread = myThread('control',control,q,log)
thread.start()
workers.append(thread)


   
# Wait for queue to empty
while True:
    if  q.empty():
        break

# Notify threads it's time to exit
log.info('seting Exit flag')
exitFlag = 1

# Wait for all threads to complete
for t in workers:
    t.join()

log.info(' Phase 2: All treads have finished')

if DEBUG:
    psave(pid_summary,'pid_summary')


#Пишем в pid_summary
pid_summary = pid_summary_normalize(pid_summary)
log.info('P2: Start to adding  PNs to PidSummary Table')
for pid_info in pid_summary:
    log.info(pid_info['pn'])

    session = sessionmaker(bind=engine)()
    result = session.query(PidSummary).filter_by(pn=pid_info['pn']).update(pid_info)
    if result == 0:
        session.add(PidSummary(**pid_info))

    session.commit()
    session.close()
    # try:
    #     session.add(PidSummary(**pid_info))
    #     session.commit()

    # except IntegrityError: # Если нарушаем UNIQE CONSTRAIN Логика такая: если есть хоть 1 железка с None Annonced то считаем что pn тоже None Annonced, если такой нет то 
    #                        # то пишем самую позднюю дату
    #     session.rollback()
    #     session.query(PidSummary).filter_by(pn = pid_info['pn']).update(pid_info)
    #     session.commit()
    #     # query = session.query(PidSummary).filter_by(pn = pid_info['pn']).first()
    #     # if query.endOfSaleDate == "None Announced":
    #     #     pass
    #     # elif pid_info['endOfSaleDate'] == "None Announced" :
    #     #     session.query(PidSummary).filter_by(pn = pid_info['pn']).update(pid_info)
    #     #     session.commit()
    #     # else:
    #     #     try:
    #     #         if parse(pid_info['endOfSaleDate']) < parse(query.endOfSaleDate): # Записываем более ранюю дату End of Sale
    #     #             session.query(PidSummary).filter_by(pn = pid_info['pn']).update(pid_info)
    #     #             session.commit()
    #     #     except:
    #     #         log.critical('pn:' + pid_info['pn']+ " " +  'row:'+ row['endOfSaleData'] +" "+ "db:"+ query.endOfSaleData)
    #     #     else: 
    #     #         pass
    # finally:
    #     session.close()

log.info('P2: All PNs are added to tables')


log.info('PHASE 3 PARSING EOS PAGES')
q = queue.Queue()
queueLock = threading.Lock()
for i in all_eos_pages: q.put(i)
#q.put(('title','http://www.cisco.com/c/en/us/products/collateral/application-networking-services/ace-gss-4400-series-global-site-selector-appliances/eol_C51-728977.html'))
log.info('Starting workers')
exitFlag = 0
workers =[]
for name in workers_names:
    thread = myThread(name,parse_eos,q,log)
    thread.start()
    workers.append(thread)

thread = myThread('Control',control,q,log)
thread.start()
workers.append(thread)
   
# Wait for queue to empty
while not q.empty():
    pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in workers:
    t.join()

if DEBUG:
    psave(pid_bad,'pid_bad')
    psave(data,'data')

log.info('Phase 3: All treads are finished')
data = data_normalize(data)

#Пишем в таблицу data
session = sessionmaker(bind=engine)()
for row in data:
    log.info(row['pn'])

    session = sessionmaker(bind=engine)()
    result = session.query(Data).filter_by(pn=row['pn']).update(row)
    if result == 0:
        session.add(Data(**row))
    session.commit()
    session.close()
    try:
            session.add(Data(**row))
            session.commit()

    except IntegrityError: # Если нарушаем UNIQE CONSTRAIN
        session.rollback()
        session.query(Data).filter_by(pn = row['pn']).update(row)
        session.commit()
        
       
    finally:
        session.close()
log.info(' All PNs added to table Data')

log.info('P3: start adding data to PidBad table')
pid_bad = pid_bad_normalize(pid_bad)
for row in pid_bad:
    log.info(row)
    log.info(row['pn'])

    session = sessionmaker(bind=engine)()
    result = session.query(PidBad).filter_by(pn=row['pn']).update(row)
    if result == 0:
        session.add(PidBad(**row))
    session.commit()
    session.close()

    # try:
    #         session.add(PidBad(**row))
    #         session.commit()

    # except IntegrityError: # Если нарушаем UNIQE CONSTRAIN
    #     session.rollback()   
    #     session.query(PidBad).filter_by(pn = row['pn']).update(row)
    #     session.commit()
    # finally:
    #     session.close()
log.info('All Pns are added to table PidBad')



log.info("Exiting Main Thread")
log.info("Execution time:" + str(datetime.datetime.now() - startTime))
