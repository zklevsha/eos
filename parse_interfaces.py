from  mylibs.utils import  get_page
from bs4 import BeautifulSoup

page = get_page('https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-3750-metro-series-switches/prod_end-of-life_notice0900aecd804c7228.html')

s = BeautifulSoup(page.text)


print(len(page.text))