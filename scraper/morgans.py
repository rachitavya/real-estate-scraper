import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse

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

    section = soup.find('section', class_='space blog-detail-page')
    photos_div = soup.find('section', class_='property-gallery-sec space pb-0')

    # From that section, find the div with class "content-wrapper"
    if section:
        content_div = section.find('div', class_='content-wrapper')
        if not content_div:
            print("No <div class='content-wrapper'> found inside the section.")
    else:
        print("No <section class='space blog-detail page'> found.")


    # Extracting data based on HTML structure
    data['title'] = content_div.find('h2', class_='mt-0').get_text(strip=True) if content_div.find('h2', class_='mt-0') else None
    data['slug'] = get_slug_from_url(house_url) 
    data['description'] = content_div.find('div', class_='show_more_content').get_text(strip=True) if content_div.find('div', class_='show_more_content') else None
    data['price'] = content_div.find('div', class_='price-amenitity').find('h3').get_text(strip=True) if content_div.find('div', class_='price-amenitity') else None
    data['is_poa'] = 'POA' in data['price'] if data['price'] else False

    rooms = content_div.find_all('div', class_='amenity-box')
    for room in rooms:
        if 'Beds' in room.find('p').get_text():
            data['bedrooms'] = int(room.find('p').get_text(strip=True).split()[0]) 

        if 'Bathrooms' in room.find('p').get_text():
            data['bathrooms'] = int(room.find('p').get_text(strip=True).split()[0])

    # Location
    location = content_div.find('div', class_='property-location').text.strip()
    data['location'] = location.replace('Property Location', '').strip()

    data["sub_location"]=content_div.find("p").get_text().strip()
    data["city"] = data["location"]

    property_type = photos_div.find('p', class_='category-label').get_text(strip=True) if photos_div.find('p', class_='category-label') else None
    data['property_type'] = property_type 

    size = content_div.find('div', class_='amenity-box')
    if size:
        data['size'] = size.find('p').get_text(strip=True)

    amenities = []
    amenities_section = content_div.find('div', class_='ameneties-items')
    if amenities_section:
        amenities = [item.get_text(strip=True) for item in amenities_section.find_all('p')]
    data['amenities'] = amenities

    coordinates = content_div.find('iframe')['src'] if content_div.find('iframe') else None
    data['coordinates'] = coordinates.split('q=')[1].split('&')[0] if coordinates else None

    photos = [img['src'] for img in photos_div.find("div", class_ = "gallery-grid").find_all('img') if img.has_attr('src')]
    data['images'] = photos

    data['url'] = house_url 

    rent_section = soup.find("section", class_="breadcrumb-sec").find_all('a', href=True)
    rent_or_buy = None
    for link in rent_section:
        if "for=rent" in link['href'].lower() or "for=sales" in link["href"].lower():
            rent_or_buy = link.get_text(strip=True).lower()
            break
    data["rent_or_buy"] = rent_or_buy if rent_or_buy in ["rent", "buy"] else None
            
    data['extra_fields'] = {}

    return data


if __name__=="__main__":
    details = scrape_house("https://www.morgansrealty.com/properties/view/4-br-penthouse-premium-features-prime-location-2")
    for key, value in details.items():
        print(key, value)

        