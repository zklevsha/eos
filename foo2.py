import pickle
import os 
from mylibs.utils import *
from aiohttp import ClientSession
import platform
import datetime





log = get_logger('foo')

startTime = datetime.datetime.now()
log.info('Starting script at ' + str(startTime) )
if platform.system() =="Windows":
	os.system('chcp 65001') # for windows systems only


pages = pickle.load(open('all_eos_pages_2016-09-22-1841.p','rb'))[0:10]
a = []
for page in pages:
	content = get_page(page[1])
	a.append((page[0],content))
psave(a,'a')
log.info("Execution time:" + str(datetime.datetime.now() - startTime))