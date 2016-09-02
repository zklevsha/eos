#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
from mylibs.utils import *
import pickle
import sys
import subprocess
log = get_logger('test.py')
start_date = datetime.datetime.now()

arr = []
# with open('routes','r') as fr:
# 	for line in fr.readlines():
# 		line = line.split(' ')
# 		#print(line)
# 		if (line[4],line[2]) not in arr and line[4] != 'proto':
# 			arr.append((line[4],line[2]))

# for i in arr:
# 	print(i[0],i[1])

res = subprocess.check_output(['ping','8.8.8.8'])

print (str(res).encode('utf-8') )