import pickle
import os 
from mylibs.utils import *
from aiohttp import ClientSession
import platform
import datetime
# os.system('chcp 65001')
# data=pickle.load(open('data_2016-09-202339.p','rb'))



# for i in ['SPA-1XCHSTM1/OC3','SPA-2X1GE','PWR-3900-AC','CISCO3945/K9','HWIC-4T=']:
# 	print(i)
# 	try:
# 		print(data[i])
# 	except:
# 		print("no")
# 	print('')



# all_eos_pages = pickle.load(open('all_eos_pages.p','rb'))

# arr = []
# header = "http://www.cisco.com"
# for i in all_eos_pages:
# 	if i[1][0] == '/':i = (i[0],header+i[1])
# 	if i not in arr: arr.append(i)


# for i in arr:
# 	if all_eos_pages.count(i) > 1:
# 		print (i,all_eos_pages.count(i))


# psave(all_eos_pages,'all_eos_pages')
# psave(arr,'arr')




async def fetch(url, session):
    async with session.get(url) as response:
        delay = response.headers.get("DELAY")
        date = response.headers.get("DATE")
        print("{}:{} with delay {}".format(date, response.url, delay))
        return await response.read()


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)


async def run(loop,r,pages):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for eos in pages:
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, eos[1], session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses
        type(responses)







log = get_logger('foo')

startTime = datetime.datetime.now()
log.info('Starting script at ' + str(startTime) )
if platform.system() =="Windows":
	os.system('chcp 65001') # for windows systems only




pages = pickle.load(open('all_eos_pages_2016-09-22-1841.p','rb'))[0:100]






number = 100
loop = asyncio.get_event_loop()

future = asyncio.ensure_future(run(loop, number,pages))
print (future)
loop.run_until_complete(future)

log.info("Execution time:" + str(datetime.datetime.now() - startTime))