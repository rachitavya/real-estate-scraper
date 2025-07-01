from bs4 import BeautifulSoup
import json
import re
import requests
from urllib.parse import urlparse

def get_slug_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    slug = path.strip('/').split('/')[-1]
    return slug

def extract_property_id(url):
    match = re.search(r'(\d+)(?=/)', url)
    
    if match:
        return int(match.group(1))
    else:
        return None

def parse_property_json_v2(api_data):
    property_data = api_data["result"]["data"]["glstrapi"]["property"]["data"]["attributes"]
    property_address = property_data["address"]

    data = {
        'title': property_data.get("title"),
        'slug': property_data.get("crm_id"),
        'description': property_data.get("long_description"),
        'price': property_data.get("price"),
        'is_poa': False if property_data.get("price") else True,
        'bedrooms': property_data.get("bedroom"),
        'bathrooms': property_data.get("bathroom"),
        'location': property_data.get("display_address"),
        'sub_location': property_address.get("area"),
        'city': property_address.get("address2"),
        'property_type': property_data.get("building"),
        'size': property_data.get("size"),
        'amenities': property_data.get("accommodation_summary"),
        'coordinates': {
            "latitude": property_data.get("latitude"),
            "longitude": property_data.get("longitude")
        },
        'images': [image.get("url") for image in property_data.get("images", [])],
        'url': None, 
        'rent_or_buy': property_data.get("search_type"),
        'extra_fields': {
            "negotiator_details": {
                "name": property_data.get("negotiator_details", {}).get("name"),
                "email": property_data.get("negotiator_details", {}).get("email"),
                "phone": property_data.get("negotiator_details", {}).get("phone")
            },
            "furnished": property_data.get("furnished"),
            "propertyID": property_data.get("propertyID"),
            "crm_id": property_data.get("crm_id")
        }
    }
    
    return data


def scrape_house(house_url):
    id = extract_property_id(house_url)
    slug = get_slug_from_url(house_url)
    
    api_url = "https://www.thepearlgatesdubai.com/page-data/properties-for-sale/{slug}/page-data.json".format(slug=slug)

    r = requests.get(api_url, timeout=15)
    r.raise_for_status()
    j = r.json()
    data = parse_property_json_v2(j)
    data["url"] = house_url
    data["slug"]= slug
    return data


if __name__=="__main__":
    details = scrape_house("https://www.thepearlgatesdubai.com/properties-for-sale/3-bedroom-apartment-for-sale-in-one-business-bay-business-bay-dubai-3029/")
    for key, value in details.items():
        print(key, value)

        