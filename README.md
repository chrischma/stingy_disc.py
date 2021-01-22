# stingy_disc.py

![Screenshot](https://github.com/chrischma/stingy_disc.py/blob/main/sceenshot.png)

## About
<code> stingy_disc.py</code> is a commandline tool that adds a new search option to the discogs search.

it helps you to find the cheapest price for the record you are searching for. the regular search engine of discogs only allows you to sort the results by price, while this price does not include shipping. as shipping prices can be ridiculously high some time, it is very helpful to have a list sorted by the **total price**. and this is what stingy_disc.py does. 

## Features
* find the lowest total price for a record on discogs
* colorful, minimalist interface
* save favorite search terms for later
* check lowest price for all your favorite items with one click


## Usage
make sure the following modules are installed: <code>requests</code>, <code>BeautifulSoup</code> and <code>simple_term_menu </code>.

run <code> python3 stingy_disc.py </code>. 

Enter any artist, album, single, ep and so on. 
stingy_disc.py will respond with a list of up to 250 offers.
