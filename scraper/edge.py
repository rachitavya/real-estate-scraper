import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

def get_slug_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    slug = path.strip('/').split('/')[-1]
    return slug

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

    title_tag = soup.find("h1")
    if title_tag:
        data["title"] = title_tag.get_text(strip=True)
        data["slug"] = get_slug_from_url(house_url)

    loc_tag = soup.find("p", string=re.compile(r"\w"))
    if loc_tag:
        loc_text = loc_tag.get_text(strip=True)
        data["location"] = loc_text
        data["sub_location"] = loc_text
        data["city"] = "Dubai"

    aed_tag = soup.select_one("div.AED span")
    if aed_tag:
        price_text = aed_tag.get_text(strip=True)          # "AED 1,050,000"
        price_num = re.sub(r"[^\d.]", "", price_text)      # "1050000"
        data["price"] = int(float(price_num)) if price_num else None
        data["is_poa"] = False
    else:
        data["is_poa"] = True

    bc_sale = soup.select_one('a[href*="/sale/"]')
    bc_rent = soup.select_one('a[href*="/rent/"]')
    data["rent_or_buy"] = "buy" if bc_sale else "rent" if bc_rent else None

    details_tag = soup.find("h3")
    if details_tag:
        details = details_tag.get_text(" ", strip=True)

        num = lambda pattern: int(re.search(pattern, details).group(1)) if re.search(pattern, details) else None
        txt = lambda pattern: re.search(pattern, details).group(1) if re.search(pattern, details) else None

        data["property_type"] = txt(r"^\s*(\w+)")
        data["bedrooms"]       = num(r"(\d+)\s+Bedrooms?")
        data["bathrooms"]      = num(r"(\d+)\s+Bathrooms?")
        data["size"]           = float(re.sub(r",", "", txt(r"([\d,.]+)\s+Sq\.ft"))) if txt(r"([\d,.]+)\s+Sq\.ft") else None

        parking                = num(r"(\d+)\s+Parking")
        permit_no              = txt(r"Permit No\s+(\d+)")
        if parking is not None:
            data["extra_fields"]["parking_spaces"] = parking
        if permit_no:
            data["extra_fields"]["permit_no"] = permit_no

    data["images"] = []
    seen = set()
    for a in soup.select('a[data-fslightbox="property-carousel"]'):
        href = a.get("href")
        if href and href not in seen:
            seen.add(href)
            data["images"].append(href)

    for img in soup.select('img.slider-property'):
        src = img.get("src")
        if src and src not in seen:
            seen.add(src)
            data["images"].append(src)

    about = soup.select_one("#about_mobile")

    if about:
        desc_parts = []
        for elem in about.children:
            if getattr(elem, "name", None) == "ul":
                break
            if getattr(elem, "name", None) == "p":
                text = elem.get_text(" ", strip=True)
                if text:
                    desc_parts.append(text)
        data["description"] = "\n\n".join(desc_parts) if desc_parts else None

        heading = about.find(lambda tag:  "property features" in tag.get_text(strip=True).lower())
        amenities_list = []
        if heading:
            ul = heading.find_next("ul")
            if ul:
                for li in ul.find_all("li"):
                    item = li.get_text(" ", strip=True)
                    if item:
                        amenities_list.append(item.lower())
        seen = set()
        data["amenities"] = [a for a in amenities_list if not (a in seen or seen.add(a))] or None

    return data

if __name__=="__main__":
    details = scrape_house("https://www.edgerealty.ae/en/dubai-property/1-bedroom-apartment-in-jumeirah-village-circle")
    for key, value in details.items():
        print(key, value)

        