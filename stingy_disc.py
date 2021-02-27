import re, time, pync, requests
from bs4 import BeautifulSoup
from simple_term_menu import TerminalMenu
from colorama import init, Fore, Back, Style

YOUR_USERNAME = ""

# Todo: 
 	# setup file erstellen
 	# f-strings in parameterstrings umwandeln


init() #initializing colorama

def import_favs_from_discogs():

	global favs
	favs = favs_from_discogs

def set_value_color(value):

		global color
	
		if value < 15:
			color=Back.LIGHTGREEN_EX

		if value >= 15 and value < 20:
			color=Back.YELLOW

		if value >= 20:
			color=Back.LIGHTRED_EX

all_best_prices = []
item_counter = 1

def get_results(search_term):
	global item_counter

	if item_counter % 25 == 0:
		pync.notify(f'{item_counter}/{len(favs_from_discogs)} items done.')
	#print(f'now searching item nr {item_counter}/{len(favs_from_discogs)}: {search_term}')
	time.sleep(1)
	item_counter += 1

	URL = f'https://www.discogs.com/sell/list?&limit=250&currency=EUR&q={search_term}&format=Vinyl&format_desc=LP'
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, 'html.parser')

	try:

		results = soup.find("table", attrs={"class": "table_block mpitems push_down table_responsive"})
		results = list(results.tbody.find_all("tr"))  

	except AttributeError:
		return

	quantity_of_results = len(results)
                         
	if len(results) < 3:
		return                        

	i = quantity_of_results-1

	while i>0:
		if "Unavailable" in str(results[i]):
			results.pop(i)
		i-=1

	obj_list = []

	class Item():

		def __init__(self, item_name, item_price, item_url):

			self.item_name = item_name 
			self.item_price = item_price
			self.item_url = item_url

	i = 0

	

	for _ in results:

		try:

			regex_for_price = re.findall("(?<=€)(.*)(?=total)",str(results[i]))[0][:-6]
			regex_for_name = re.findall("(?<=>)(.*)(?=LP)",str(results[i]))[0][:-6]
			regex_for_url = re.findall("(?<=title)(.*)(?=\")",str(results[i]))[0][31:]

		except IndexError:
			pass

		try: regex_for_name=regex_for_name[:40]

		except IndexError:
			pass

		try: regex_for_price = float(regex_for_price)

		except ValueError:
			regex_for_price = 99999
			pass

		complete_url = "discogs.com"+regex_for_url
	
		obj = Item(regex_for_name,regex_for_price,complete_url)
		obj_list.append(obj)
		
		i+=1

	
	obj_list.sort(key=lambda x: x.item_price, reverse=False)

	if mm_result == 0:
		for _ in obj_list:
			set_value_color(_.item_price)
			print(color,str(_.item_price).ljust(6),_.item_name,Style.RESET_ALL)

	all_best_prices.append(obj_list[0])

	set_value_color(obj_list[0].item_price)

	# Print best result
	print(f'{color}{str(obj_list[0].item_price).ljust(6)} {obj_list[0].item_name} {obj_list[0].item_url}{Style.RESET_ALL}')
	time.sleep(3)
	

def read_favs_from_discogs():
	URL = f'https://www.discogs.com/de/wantlist?page=1&limit=250&user={YOUR_USERNAME}'
	page = requests.get(URL)

	soup = BeautifulSoup(page.content, 'html.parser')
	release_data = soup.find_all('span',attrs={'class':'release_title set_height'})

	global favs_from_discogs

	favs_from_discogs = []

	class Item():

			def __init__(self, artist_name, album_name, label_name):

				self.artist_name = artist_name
				self.album_name = album_name
				self.label_name = label_name

	item_list = []

	for _ in release_data:
	
		item_data_string = str(_.text.replace("\n","").replace("  ",""))

		obj = Item(re.findall(".+?(?=-)",item_data_string)[0],re.findall("(?<=-).+?(?=\()",item_data_string)[0],re.findall("(?<=\().+?(?=-)",item_data_string)[0])

		if obj.album_name not in item_list:
			item_list.append(obj)
		

	print("Hi!",len(item_list)," items sucessfully imported from your discogs profile!")
	favs_from_discogs = item_list

def print_favs():

	for number, item in enumerate(favs_from_discogs):
		print(number, item.artist_name, item.album_name)


def get_prices_of_all_favorites():

	print(f'\n Finding best offers for {len(favs)} favorites...')
	print(f' Estimated time: {round(len((favs)*4)/60)} minutes.')

	i = len(favs)-1
	for _ in favs:
		try:
			get_results(favs[i].album_name+favs[i].label_name+favs[i].artist_name)
			i-=1
		except UnboundLocalError:
			pass


def new_search_term():
	global search_term
	search_term = input("Enter any artist, album... : ")

	get_results(search_term)

def print_all_best_prices():
	all_best_prices.sort(key=lambda x: x.item_price, reverse=True)

	print("\n \n /// Summary: ///")

	for item in all_best_prices:
		set_value_color(item.item_price)
		print(color,str(item.item_price).ljust(6), item.item_name, item.item_url,Style.RESET_ALL)

	
def main_menu():
    m = TerminalMenu(["NEW CUSTOM SEARCH (Beta)","SHOW FAVORITES","CHECK ALL PRICES","QUIT"],"\n")
    global mm_result
    mm_result = m.show()

    if mm_result == 0:
    	new_search_term()


    elif mm_result == 1:
    	print_favs()

    elif mm_result == 2:
    	item_counter = 1
    	get_prices_of_all_favorites()
    	print_all_best_prices()
    	pync.notify("done!")

    else:
    	exit()


read_favs_from_discogs()
import_favs_from_discogs()
main_menu()

