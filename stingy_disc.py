import re
import requests
from bs4 import BeautifulSoup
from simple_term_menu import TerminalMenu
from colorama import init, Fore, Back, Style


init() #initializing colorama

def read_fav_file():
	try: 
		fav_file = open('favorites.txt','r')

	except IOError:
		print("You have no favorites so far. Use a new search-term to add some...")

	finally: 
		fav_file.close()


def import_favs_from_file():

	try: 
		global fav_file
		fav_file = open('favorites.txt','r')

	except FileNotFoundError:
		open('favorites.txt','w')

	global favs

	favs = list(fav_file.read().split(","))


def save_request_to_favorites():

	if search_term in favs:
		print(f'"{search_term}" ist bereits in deinen Favoriten.')

	else: 
		
		fav_file = open('favorites.txt','a')
		fav_file.write(f',{search_term}')

		print(f'Okay. I added >> {search_term} << to your favorites!')
	
	main_menu()


def set_value_color(value):

		global color

		if value < 10:
			color=Fore.GREEN

		elif value > 10 and value<20:
			color=Fore.YELLOW

		elif value > 20:
			color=Fore.RED


def get_results(search_term):

	read_fav_file()

	URL = f'https://www.discogs.com/sell/list?&limit=250&q={search_term}&format=Vinyl&format_desc=LP'
	page = requests.get(URL)

	soup = BeautifulSoup(page.content, 'html.parser')
	results = soup.find(id="pjax_container")

	try:	
		prices = results.find_all(class_='item_description_title')
		items = results.find_all(class_="item_price hide_mobile")

	except AttributeError:

		pass 


	items_list_clean = re.findall("(?<=- )(.*)(?=\()",results.text)

	try:
		price_list_clean=re.findall("(?<=€)(.*)(?= total)",results.text)
	except ValueError:
		price = 0	


	global results_dict

	results_dict = dict(zip(price_list_clean,items_list_clean))

	# Create two lists from dictionary

	prices = []
	items = []

	for key in sorted(results_dict,reverse=True):
	
	 	try:
	 		if float(key) <= 99:

		 		prices.append(float(key))
		 		items.append(results_dict[key][:40])

	 	except ValueError:
	 		pass					
	


	if mm_result == 0:

		print(f'\n \n Results for "{search_term}":')
		i = 0
		for _ in prices:

			set_value_color(prices[i])

			result_string = str(color+str(prices[i]).ljust(5,"0")+" € "+Style.RESET_ALL+str(items[i]))		

			print(result_string)

			i+=1

		print("Add last search_term to favorites?")

		m = TerminalMenu(["Maybe later...","Yes!"])
		r = m.show()

		if r == 1:
			save_request_to_favorites()
			print("added!")
		
		main_menu()


	if mm_result == 2: # This only shows the lowest price (for the case that user checks multiple items at once)

		set_value_color(float(prices[len(prices)-1]))
		print(color,str(prices[len(prices)-1]).ljust(5," "),Style.RESET_ALL,str(items[len(items)-1])[:40]) 


def print_favs():

	print("\n\n These are your saved search_term requests: \n")
	print(*favs,sep="\n")

	main_menu()

	
def get_prices_of_all_favorites():

	print(f'Now checking {len(favs)} favorites...')

	i = len(favs)-1
	for _ in favs:
		try:
			get_results(favs[i])
			i-=1
		except UnboundLocalError:
			pass


def new_search_term():
	global search_term
	search_term = input("Enter any artist, album... : ")

	get_results(search_term)


def main_menu():
    m = TerminalMenu(["Search for a new item","Show my saved search-terms","Check all prices","Quit"],"\n")
    global mm_result
    mm_result = m.show()

    if mm_result == 0:
    	new_search_term()

    elif mm_result == 1:
    	print_favs()

    elif mm_result == 2:
    	get_prices_of_all_favorites()

    else:
    	exit()


import_favs_from_file()
main_menu()

