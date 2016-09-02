#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
from mylibs.utils import *
import pickle
import sys
log = get_logger('test.py')
start_date = datetime.datetime.now()


pid_summary = pickle.load(open('pid_summary_debug.p','rb'))
i = 0
states = []
for k in pid_summary.keys():
	i = i+1
	log.info('checking' + str(i) + '/' + str(len(pid_summary.keys())))
	status = pid_summary[k]['Status:'].replace('End of Sale','EndOfSale').replace('End of Support','EndOfSupport').split()[0]
	if status == 'EndOfSupport':
		print(pid_summary[k])
		sys.exit()
print(states)


