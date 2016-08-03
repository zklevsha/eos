#!/usr/bin/python3
import pickle
import re
all_eos = pickle.load(open("eos.p",'rb'))

pattern = re.compile('7200')

for eos in all_eos:
	if pattern.search(eos):
		print(eos)

	#framework-column-center