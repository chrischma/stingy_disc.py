import requests
from bs4 import BeautifulSoup
from simple_term_menu import TerminalMenu

def check_fav_file():
	try: 
		fav_file = open('favorites.txt','r')

	except IOError:
		print("You have no favorites so far. Use a new search to add some...")

	finally: 
		fav_file.close()


def read_favs():
	try: 
		global fav_file
		fav_file = open('favorites.txt','r')

	except FileNotFoundError:
		open('favorites.txt','w')

	global favs
	favs = list(fav_file.read().split(","))


def add_fav():
	if search in favs:
		print(f'"{search}" ist bereits in deinen Favoriten.')
	else: 
		
		fav_file = open('favorites.txt','a')
		fav_file.write(f',{search}')

		print(f'Okay. I added >> {search} << to your favorites!')
		exit()


def get_results(search):
	check_fav_file()

	URL = f'https://www.discogs.com/sell/list?&limit=100&q={search}&format=Vinyl&format_desc=LP'
	page = requests.get(URL)

	soup = BeautifulSoup(page.content, 'html.parser')
	results = soup.find(id="pjax_container")

	try:	
		items = results.find_all(class_='item_description_title')
		prices = results.find_all(class_="item_price hide_mobile")

	except AttributeError:
		print(f'Sorry, no results found for {search}')
		exit()

	# Clean up the price list
	price_list = []
	for prices in prices:
		price_list.append(prices.text.strip())

	price_list = [x.strip(' ') for x in price_list]

	# Clean up the item names
	item_list = []
	for items in items:
		item_list.append(items.text.strip())

	global price_list_final
	price_list_final=[]

	for i in price_list:
	    
	    j = i.split('shipping')
	    j.pop(0)
	    j = j[0]
	    j = j.replace(' ','').replace('\n','').replace('total','').replace('about','').replace('€','')

	    try:
	    	j = float(j)
	    except ValueError:
	    	j = 0			

	    price_list_final.append(j)


	global results_dict
	results_dict = dict(zip(price_list_final,item_list))

	# if the price is 0, there might be something wrong. i delete these results.
	for key in list(results_dict):
		if key == 0:
			del results_dict[key]

	items = []
	prices = []

	# Create two lists from dictionary
	
	for key in sorted(results_dict,reverse=True):
	 
	    items.append(key)					
	    prices.append(results_dict[key])


	if mm_result == 0:

		print(f'\n \n Results for "{search}":')
		i = 0
		for _ in items:
			print(f' {items[i]}€ {prices[i]}')
			i+=1
		print("\n")

	print(f'*** Best Deal: {items[len(items)-1]} - {prices[len(prices)-1]} **') 


	if mm_result == 0: # Ask user, if he / she wants to add the result to favs
		print("Add last search to favorites?")
		m = TerminalMenu(["Maybe later...","Yes!"])
		result = m.show()

		if result == 0:
			main_menu()

		if result == 1:
			add_fav()
			print("added!")
			main_menu()

def print_favs():
	print("\n\n These are your saved search requests: \n")
	print(*favs,sep="\n")

	main_menu()

	
def check_fav_list():

	i = len(favs)-1
	while i != -1:
		get_results(favs[i])
		i-=1

def new_search():
	global search
	search = input("Enter any artist, album... : ")
	#search = search.replace(" ","+")
	options = "y"
	get_results(search)

def main_menu():
    m = TerminalMenu(["Create new search","Show Favorites","Check prices for favorites","Quit"],"\n")
    global mm_result
    mm_result = m.show()

    if mm_result == 0:
    	new_search()

    if mm_result == 1:
    	print_favs()

    if mm_result == 2:
    	check_fav_list()

    if mm_result == 3:
    	exit()

read_favs()
main_menu()
