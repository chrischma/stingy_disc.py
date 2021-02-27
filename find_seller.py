import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, random, re, os

# Note: Please make sure you got the 'chromedriver' file in selenium/webdriver/chrome.
# Download 'chromedriver' here: https://chromedriver.chromium.org/downloads.

USERNAME = 'USERNAME'             # Your Discogs Username
PASSWORD = 'PASSWORD'             # Your Discogs Password
MAXIMUM_BUDGET = 100.00           # Set your general budget. What are you willing to pay for your order in total?
MAXIMUM_BUDGET_PER_ITEM = 20.00   # Set the maximum cost for one item. Other items will be ignored
NUMBER_OF_ACCOUNTS_TO_CHECK = 10  # Set how much Accounts the script should check. One account takes around 30 seconds.

seller_list=list()

def clprint(text):
  os.system('clear')
  print(text)

def hide_cookies():
  print('hiding cookies')
  driver.find_element_by_id("onetrust-accept-btn-handler").click()

def scroll_whole_page():
  html = driver.find_element_by_tag_name('html')

  for _ in range(100):
    print('Scrolling down the results page', _, '% ...')
    html.send_keys(Keys.PAGE_DOWN)
    time.sleep((random.randint(10,25)/10))

def login_to_discogs():
  clprint('opening login page...')
  driver.get("https://www.discogs.com/")
  hide_cookies()

  driver.find_element_by_id("log_in_link").click()
  hide_cookies()

  print('passing username')
  username_field = driver.find_element_by_id('username')
  username_field.clear()
  username_field.send_keys(USERNAME)
  time.sleep(1)

  print('passing password')
  password_field = driver.find_element_by_id('password')
  password_field.clear()
  password_field.send_keys(PASSWORD)
  time.sleep(1)

  print('confirming login...')
  driver.find_element_by_css_selector("button[type='submit']").click()

def save_results_to_file():

  with open('page.html', 'w') as f:
    f.write(driver.page_source)

print("starting webdriver...")
driver = webdriver.Chrome()
#driver.minimize_window()
driver.implicitly_wait(30)
login_to_discogs()

#print("loading results from results page")
#driver.get('https://www.discogs.com/de/sell/mywants?sort=price%2Casc&limit=250&ev=wsim&currency=EUR')
#scroll_whole_page()
#save_results_to_file()

clprint("reading results from saved html")
results_html = open('page.html','r')
results_html = results_html.read().replace('\n','')
items = re.findall(r"(?<=seller\/)(.*?)(?=\<\/a\>)",results_html)
item_list = list()
count = len(items)-1

class seller():
  def __init__(self, name, item_count,total_price,price_per_item,ignore_seller):
    self.name = name
    self.item_count = item_count
    self.total_price = total_price
    self.price_per_item = price_per_item
    self.ignore_seller = ignore_seller

def create_sellers_from_results():

  global names
  names = list()

  for _ in item_list:
    item_count = _.split()[1]
    try:
      item_count = int(item_count)+1
    except ValueError:
      item_count = 1

    name = re.findall(r'.+?(?=\/)', _)

    if name not in names:
      names.append(name)
      seller_list.append(seller(name, item_count, 'no total price','no price per item', False))

while count >= 0:

  if "?ev=hxiiw" in items[count]:
    print(items[count])
    item_list.append(items[count])
  count -= 1

create_sellers_from_results()

seller_list_sorted = sorted(seller_list, key=lambda x: x.item_count, reverse=True)
seller_list = seller_list_sorted

for _ in seller_list:
  print(_.item_count,_.name)

def check_cart_with_items_of(name):

  print('opening page of',name)
  driver.get(f'https://www.discogs.com/de/seller/{name}/mywants?ev=hxiiw')

  with open('items.html', 'w') as f:
    f.write(driver.page_source)
  print('results stored in items.html!')

  print('opening results html')
  items_for_sale_html = open('items.html','r')
  items_for_sale_html = items_for_sale_html.read()

  print('search for item ids')
  item_ids = re.findall('(?<=add=)(.*?)(?=&amp)',items_for_sale_html)

  for _ in item_ids:
    print('adding item to chart...')
    driver.get(f'https://www.discogs.com/de/sell/cart/?add={_}&amp;ev=atc_br')
    time.sleep(2)

  with open('cart.html', 'w') as f:
    f.write(driver.page_source)

  print("loading cart from saved file...")
  cart_html = str(open('cart.html','r').read())
  cart_table = cart_html.strip().replace(' ','').replace('\n','')
  item_names_dirty = re.findall(r'(?<=aclass\=\"item_link\")(.*?)(?=\))',cart_table)
  item_prices = re.findall(r'(?<=pricenumericnowrap)(.*?)(?=&nbsp)',cart_table)

  item_prices_clean = list()

  for _ in item_prices:
    _ = _.replace(",",".")
    try:
      _ = _.split(sep=':')[1]
    except IndexError:
      _ = float(_.split(sep='>')[1])

    item_prices_clean.append(_)

  item_prices = item_prices_clean

  item_names = list()
  item_delete_links_dirty = list()
  item_delete_links = list()

  print("finding item names")
  for _ in item_names_dirty:
    item_names.append(_.split(sep="\">")[1])
    item_delete_links_dirty.append((_.split(sep="\">")[0]))

  print("cleaning item links...")
  for _ in item_delete_links_dirty:
    id = _.split(sep="item")[1][1:]
    clean_item_link = str(f'http://discogs.com/de/sell/cart/?remove={id}')
    item_delete_links.append(clean_item_link)

  print(len(item_names),len(item_delete_links),len(item_prices))

  class item_in_cart():
    def __init__(self,item_name,item_price,item_delete_link):
      self.item_name = item_name
      self.item_price = item_price
      self.item_delete_link = item_delete_link

  items_in_cart = list()
  global duplicate_counter
  duplicate_counter = 0

  # Too expensive Vinyls will be ignored here
  i = 0
  for _ in range (len(item_names)):
    if float(item_prices[i]) <= MAXIMUM_BUDGET_PER_ITEM:
      items_in_cart.append(item_in_cart(item_names[i],item_prices[i],item_delete_links[i]))
    else:
      driver.get(item_delete_links[i])
      duplicate_counter+=1
      print("Deleted item because too expensive.")
    i+=1

  print(len(items_in_cart))
  time.sleep(5)

  i = 0
  j = 1


  print('items in car',len(items_in_cart))

  try:
    while j<=len(items_in_cart):

        if items_in_cart[i].item_name == items_in_cart[j].item_name:
          driver.get(items_in_cart[j].item_delete_link)
          duplicate_counter +=1
          print("duplicate removed")
        else:
          print("no duplicate")

        time.sleep(1)
        i+=1
        j+=1

  except IndexError:
    print('Done.')

  for _ in items_in_cart:
    print(_.item_name,_.item_price,_.item_delete_link)

  driver.get('https://www.discogs.com/de/sell/cart/')
  with open('cart.html', 'w') as f:
    f.write(driver.page_source)
  cart_html = str(open('cart.html', 'r').read())

  try:
    print('reading total price from cart...')
    total_price = str(cart_html.strip().replace("\n"," "))
    tpr = re.findall(r'(?<=Gesamt)(.*?)(?=span)',total_price)[0].replace(" ","")
    total_price = str(re.findall(r'(?<=€)(.*?)(?=\<)',tpr))[2:][:-2]
    print(total_price)
  except IndexError:
    total_price = 999999999
    return total_price


  list_of_items_in_cart = list()

  clprint('clearing cart')
  clearing_link = str(f'https://www.discogs.com/de/sell/cart/?remove_seller={name}')
  driver.get(clearing_link)

  print(total_price)
  return total_price

favorite_sellers = list()

i = 0                                           
accounts_count = NUMBER_OF_ACCOUNTS_TO_CHECK
for _ in range(accounts_count):

  print('taking a pause')
  time.sleep(7)
  print('Scanning offers of user nr.',_,'of',accounts_count)
  name = ''.join(seller_list[i].name)

  try:
    price_total = str(check_cart_with_items_of(name))
    new_item_count = seller_list[i].item_count
    seller_list[i].item_count = new_item_count

  except selenium.common.exceptions.NoSuchElementException:
    price_total = 9999999999

  try:
    try:
      final_price_total = float(price_total)
    except ValueError:
      final_price_total = 9999999999

    final_item_count = float(seller_list[i].item_count-duplicate_counter)
    price_per_item = round(final_price_total/final_item_count)
  except ZeroDivisionError:
    price_per_item = 9999999999

  new_seller = seller(seller_list[i].name,int(int(seller_list[i].item_count)-int(duplicate_counter)),price_total,price_per_item,False)
  try:
    if float(new_seller.total_price) <= 10000:
      favorite_sellers.append(new_seller)
      print("seller added to favlist")
    else:
      print("seller ignored")
  except ValueError:
    print('seller ignored')
  i+=1


sellers_in_budget = list ()

for _ in favorite_sellers:
  if float(_.total_price) <= MAXIMUM_BUDGET:
    sellers_in_budget.append(_)

print("\n\n MOST ITEMS AT ONCE")
favorite_sellers.sort(key=lambda x: x.item_count, reverse=True)
for _ in favorite_sellers:
  print(f'{_.item_count} items for {_.total_price} are sold by {_.name}. thats {_.price_per_item} Euro per Item.')

print("\n\n BEST PRICE PER ITEM")
favorite_sellers.sort(key=lambda x: x.price_per_item, reverse=False)
for _ in favorite_sellers:
  print(f'{_.price_per_item} Euro per Item: {_.name} sells {_.item_count} items for {_.total_price} total. ')

print("\n\n MOST ITEMS AT ONCE")
favorite_sellers.sort(key=lambda x: x.total_price, reverse=True)
for _ in favorite_sellers:
  print(f'For {_.total_price} you get {_.item_count} items from {_.name}. thats {_.price_per_item} Euro per Item.')

print("\n\n SELLERS WITHIN YOUR BUDGET OF",MAXIMUM_BUDGET)
sellers_in_budget.sort(key=lambda x: x.item_count, reverse=True)
for _ in sellers_in_budget:
  print(f'For {_.total_price} you get {_.item_count} items from {_.name}. thats {_.price_per_item} Euro per Item.')

driver.close()
