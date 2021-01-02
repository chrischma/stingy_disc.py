import requests
from bs4 import BeautifulSoup


search = input("Enter any artist, album... : ")
search = search.replace(" ","+")
print("Searching...")


# requesting data from discogs
URL = f'https://www.discogs.com/sell/list?&limit=250&q={search}&format=Vinyl'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find(id="pjax_container")
	
item_name_elems = results.find_all(class_='item_description_title')
price_elems = results.find_all(class_="item_price hide_mobile")


# Clean up the lists
price_list= []
for price_elems in price_elems:
	price_list.append(price_elems.text.strip())

price_list = [x.strip(' ') for x in price_list]


item_list = []
for item_name_elems in item_name_elems:
	item_list.append(item_name_elems.text.strip())

price_list_final=[]

for i in price_list:
    
    j = i.split('shipping')
    j.pop(0)
    j = j[0]
    j = j.replace(' ','').replace('\n','').replace('total','').replace('about','').replace('€','')


# Some results may have no price. I mark them to filtre them later.
    try:
    	j = float(j)
    except ValueError:
    	j = 999999			

    price_list_final.append(j)

results_dict = dict(zip(price_list_final,item_list))


# Filtering the results that have no price.
for key in list(results_dict):
	if key == 999999:
		del results_dict[key]


# Printing the sorted dictionary
for key in sorted(results_dict,reverse=True):
    print(key, results_dict[key])