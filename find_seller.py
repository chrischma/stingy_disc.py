# Note: Please make sure you got the 'chromedriver' file in selenium/webdriver/chrome.
# Download 'chromedriver' here: https://chromedriver.chromium.org/downloads.

import selenium, time, random, re, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

USERNAME = 'USERNAME'             # Your Discogs Username
PASSWORD = 'PASSWORD'             # Your Discogs Password
MAXIMUM_BUDGET = 50.00            # Set your general budget. What are you willing to pay for your order in total?
MAXIMUM_BUDGET_PER_ITEM = 20.00   # Set the maximum cost for one item. Other items will be ignored
NUMBER_OF_ACCOUNTS_TO_CHECK = 25  # Default: 25 - Set how much Accounts the script should check.
ACCOUNT_INDEX_TO_START_AT = 0     # Default: 0  - Only change this, if you want to ignore the first x accounts.

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

  print('pressing login button...')
  driver.find_element_by_css_selector("button[type='submit']").click()

def save_results_to_file():

  with open('page.html', 'w') as f:
    f.write(driver.page_source)
print('Hi! i am searching for the best sellers now! \n this will take around',round(NUMBER_OF_ACCOUNTS_TO_CHECK*0.6),'minutes...')
print("starting webdriver...")
driver = webdriver.Chrome()
#driver.minimize_window()
driver.implicitly_wait(30)
login_to_discogs()

#print("loading results from results page")
#driver.get('https://www.discogs.com/de/sell/mywants?sort=price%2Casc&limit=250&ev=wsim&currency=EUR')
#scroll_whole_page()
#save_results_to_file()

print("reading results from saved html")
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

def get_total_price_from_cart():
  driver.get('https://www.discogs.com/de/sell/cart/')

  with open('cart.html', 'w') as f:
    f.write(driver.page_source)

  cart_html = str(open('cart.html', 'r').read())

  try:
    print('reading total price from cart...')
    total_price = str(cart_html.strip().replace("\n", " "))
    tpr = re.findall(r'(?<=Gesamt)(.*?)(?=span)', total_price)[0].replace(" ", "")
    total_price = str(re.findall(r'(?<=€)(.*?)(?=\<)', tpr))[2:][:-2]
    print('current total price:',total_price)

  except IndexError:
    total_price = 999999999
  return total_price

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
    item_list.append(items[count])
  count -= 1

create_sellers_from_results()

seller_list_sorted = sorted(seller_list, key=lambda x: x.item_count, reverse=True)
seller_list = seller_list_sorted

def check_cart_with_items_of(name):

  print('opening page of',name)
  driver.get(f'https://www.discogs.com/de/seller/{name}/mywants?ev=hxiiw')

  with open('items.html', 'w') as f:
    f.write(driver.page_source)
  print('results stored in items.html!')

  print('opening results html')
  items_for_sale_html = open('items.html','r')
  items_for_sale_html = items_for_sale_html.read()
  item_listed_prices = list()

  item_ids = re.findall('(?<=add=)(.*?)(?=&amp)',items_for_sale_html)
  items_for_sale_html = items_for_sale_html.strip().replace(' ', '').replace('\n', '')
  item_names = re.findall(r'(?<=item_description_title\"data-followable\=\"true\"\>)(.*?)(?=\))',items_for_sale_html)
  item_listed_prices_str = re.findall(r'(?<=p\"\>\<spanclass=\"price\"\>)(.*?)(?=&nbsp)',items_for_sale_html)
  for _ in item_listed_prices_str:
    _ = float(_.replace(",","."))
    item_listed_prices.append(_)

  class listed_item():
    def __init__(self,item_name,item_price,item_id):
      self.item_name = item_name
      self.item_price = item_price
      self.item_id= item_id

  listed_items = list()
  i = 0

  for _ in item_names:
    listed_items.append(listed_item(item_names[i],item_listed_prices[i],item_ids[i]))
    i+=1

  items_by_price = sorted(listed_items, key=lambda x: x.item_price, reverse=False)

  i = 0
  j = 1


  while i <= len(items_by_price):
    try:
      if items_by_price[i].item_name == items_by_price[j].item_name:
        items_by_price.pop(j)
        print("duplicate removed")
      j+=1

    except IndexError:
      i += 1
      j = i+1


  i = 0
  for _ in items_by_price:
    driver.get(f'https://www.discogs.com/de/sell/cart/?add={items_by_price[i].item_id}&amp;ev=atc_br')

    if float(get_total_price_from_cart()) < MAXIMUM_BUDGET:
      i += 1
      print('still budget left, adding another item (',i,'items in cart)')
      time.sleep(2)

    else:
      print("Cart is too expensive. Removing last item...")
      driver.get(str(f'http://discogs.com/de/sell/cart/?remove={items_by_price[i].item_id}'))
      time.sleep(2)

  number_of_items_sold_by_user = i
  final_price = get_total_price_from_cart()
  time.sleep(3)

  print("clearing cart of ",name)
  clearing_link = str(f'https://www.discogs.com/de/sell/cart/?remove_seller={name}')
  driver.get(clearing_link)
  time.sleep(3)

  print("creating",name,"as favorite seller")
  new_favorite_seller = seller(name,number_of_items_sold_by_user,final_price,(round(float(final_price)/float(number_of_items_sold_by_user))),False)
  favorite_sellers.append(new_favorite_seller)
  return

favorite_sellers = list()

def check_offers_for_multiple_sellers():
  i = ACCOUNT_INDEX_TO_START_AT
  accounts_count = NUMBER_OF_ACCOUNTS_TO_CHECK
  for _ in range(accounts_count):
    print("taking a pause")
    time.sleep(5)

    print('checking account number ',i)
    try:
      check_cart_with_items_of(str(seller_list_sorted[i].name)[2:][:-2])

    except IndexError:
      print('items of',seller_list_sorted[i].name,'are not available in your country. user ignored.')
      seller(seller_list_sorted[i].name,item_count=1,total_price=1,price_per_item=1,ignore_seller=True)

    i += 1


def print_result_statistics():

  print("\n\n + + + these sellers give you the HIGHEST NUMBER OF ITEMS within your budget")
  favorite_sellers.sort(key=lambda x: x.item_count, reverse=True)

  for _ in favorite_sellers:
    print(_.item_count,'items for a total price of',_.total_price,'at ',_.name)
  print(f'best seller: {favorite_sellers[0].name} - URL: http://discogs.com/user/{favorite_sellers[0].name}')

  print("\n\n + + + these sellers give you the LOWEST FINAL PRICE within your budget")
  favorite_sellers.sort(key=lambda x: x.total_price, reverse=False)

  for _ in favorite_sellers:
    print(_.total_price,'Euro -',_.item_count,'items at',_.name)
  print(f'best seller: {favorite_sellers[0].name} - URL: http://discogs.com/user/{favorite_sellers[0].name}')

  print("\n\n + + + these sellers give you the LOWEST PRICE PER ITEM within your budget")
  favorite_sellers.sort(key=lambda x: x.price_per_item, reverse=False)

  for _ in favorite_sellers:
    print(_.price_per_item,'Euro per Item. Total price:',_.total_price,'Euro for ',_.item_count, 'items at', _.name)
  print(f'best seller: {favorite_sellers[0].name} - URL: http://discogs.com/user/{favorite_sellers[0].name}')


check_offers_for_multiple_sellers()
print_result_statistics()
driver.close()
exit()
