#!/usr/bin/python3
import pickle
import re
all_eos = pickle.load(open("eos.p",'rb'))

pattern = re.compile('7600')

for eos in all_eos:
	if pattern.search(eos):
		print(eos)

	#framework-column-center



content = requests.get("http://www.cisco.com/c/dam/en/us/support/home/json/overlays/routers.json",timeout=10)
soup = BeautifulSoup(content.text)