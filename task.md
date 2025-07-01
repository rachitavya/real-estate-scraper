Websites:

Here are the 5 websites

1. https://www.morgansrealty.com/
2. https://www.edgerealty.ae/
3. https://www.axcapital.ae/
4. https://site.keymaxrealestate.com
5. https://www.thepearlgatesdubai.com/

```
import requests
import json
from bs4 import BeautifulSoup


def scrape_house(house_url):
    
    response = requests.get(
        house_url
    )
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = {}

    data['title'] = None
    data['slug'] = None
    data['description'] = None
    data['price'] = None
    data['is_poa'] = None
    data['bedrooms'] = None
    data['bathrooms'] = None
    data['location'] = None
    data['sub_location'] = None
    data['city'] = None
    data['property_type'] = None
    data['size'] = None
    data['amenities'] = None
    data['coordinates'] = None
    data['images'] = []
    data['url'] = house_url
    data['rent_or_buy'] = None
    data['extra_fields'] = {}
    
    # ...... scraper's logic

    return data

```