# stingy_disc.py 

![Screenshot](https://github.com/chrischma/stingy_disc.py/blob/main/stingy_screenshot.png)

## About
<code> stingy_disc.py</code> is a commandline tool for MacOS that adds a new search option to the discogs search.

it helps you to find the cheapest price for the record you are searching for. the regular search engine of discogs only allows you to sort the results by price, while this price does not include shipping. as shipping prices can be ridiculously high some time, it is very helpful to have a list sorted by the **total price**. and this is what stingy_disc.py does. 

## Features
* colorful, minimalist interface
* find the lowest total price for a record on discogs
* import your search list from discogs
* find lowest total price for every item in your search list
* get links to all recommended items

## Beta-Features (find_seller.py-Module)
* find the best seller for the items of your personal wantlist
* find sellers with best prices per item
* set a budget: skript can fill your cart until certain budget is reached 
* script will return the url of the user where you get most items for your money



## Setup
1. make sure all dependencies are installed.
2. Enter your Username in line 7 of <code> stingy_disc.py </code> (for example: <code> YOUR_USERNAME = "otto9876543" </code>

## Usage
run <code> python3 stingy_disc.py </code>. 

Enter any artist, album, single, ep and so on. 
stingy_disc.py will respond with a list of up to 250 offers.

## To-Do
* add headless mode
* standalone-app
