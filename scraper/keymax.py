from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urlparse

def get_slug_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    slug = path.strip('/').split('/')[-1]
    return slug


def extract_amenities_from_description(description):
    """
    Extract amenities from the description field using the 'Community Features' heading.
    """
    if description:
        soup = BeautifulSoup(description, "html.parser")
        text = soup.get_text("\n", strip=True)
        amenities = []
        match = re.search(r"Community Features[:\n\s]+", text, re.IGNORECASE)
        if match:
            features_section = text[match.end():]
            features_list = re.split(r"\n•\s*", features_section)
            for feature in features_list:
                if feature.strip(): 
                    amenities.append(feature.strip().lower())
            return amenities
    return []

def scrape_house(house_url):
    base_api_url = "https://stg.backend.keymaxrealestate.com/api/v1/properties/"
    slug = get_slug_from_url(house_url)
    api_url = base_api_url+slug

    r = requests.get(api_url, timeout=15)
    r.raise_for_status()
    j = r.json()                 
    p = j["data"]                

    # ---------- helpers ----------
    def to_int(s):
        """strip commas etc. → int, or None"""
        if s is None:
            return None
        s = re.sub(r"[^\d]", "", str(s))
        return int(s) if s else None

    def html_to_text(html):
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text("\n", strip=True) or None

    # ---------- main mapping ----------
    data = {
        "title":              p.get("title"),
        "slug":               p.get("slug"),
        "description":        html_to_text(p.get("description")),
        "price":              to_int(p.get("price")),
        "is_poa":             bool(p.get("price_hidden") == "1" or not p.get("price")),
        "bedrooms":           to_int(p.get("bedrooms_number")),
        "bathrooms":          to_int(p.get("bathrooms_number")),
        "location":           (p.get("location_area") or {}).get("name"),
        "sub_location":       (p.get("location_area") or {}).get("name"),
        "city":               (p.get("city") or {}).get("name"),
        "property_type":      (p.get("property_type") or {}).get("name"),
        "size":               float(p["size"]) if p.get("size") else None,
        "coordinates":        {
                                  "lat": float(p["lat"]),
                                  "lng": float(p["lng"])
                              } if p.get("lat") and p.get("lng") else None,
        "images":             [img["original"] for img in p.get("images", [])
                               if img.get("original")],
        "url":                house_url,          # or build your public URL here
        "rent_or_buy":        p.get("buy_or_sell"),
        "extra_fields":       {}
    }

    description = p.get("description")
    data["amenities"] = extract_amenities_from_description(description)

    # ---------- extras you explicitly wanted ----------
    xf = data["extra_fields"]
    if p.get("parking_number"):
        xf["parking_spaces"] = to_int(p["parking_number"])
    if p.get("furnishing_type"):
        xf["furnishing"] = p["furnishing_type"]
    if p.get("developer_name"):
        xf["developer"] = p["developer_name"]
    if p.get("on_completion"):
        xf["handover_date"] = p["on_completion"]
    if p.get("service_charges"):
        xf["service_charges"] = p["service_charges"]

    xf["address"] = p.get("address")
    xf["agent"] = {
        "first_name": p["agent"].get("first_name"),
        "last_name": p["agent"].get("last_name"),
        "phone": p["agent"].get("phone"),
        "email": p["agent"].get("email"),
        "instagram": p["agent"].get("instagram"),
        "facebook": p["agent"].get("facebook"),
        "linkedin": p["agent"].get("linkedin"),
        "twitter": p["agent"].get("twitter"),
        "youtube": p["agent"].get("youtube"),
        "img_url": p["agent"].get("img_url")
    }

    consumed = {
        # mapped directly
        "title","slug","description","price","price_hidden","bedrooms_number",
        "bathrooms_number","size","lat","lng","buy_or_sell",
        # pulled from nested objects
        "location_area","city","property_type","images","amenities",
        # extras we just copied
        "parking_number","furnishing_type","developer_name",
        "on_completion","service_charges",
        "address","agent"
    }

    for k, v in p.items():
        if k not in consumed and k not in xf:
            xf[k] = v

    return data


if __name__=="__main__":
    details = scrape_house("https://stg.backend.keymaxrealestate.com/api/v1/properties/brand-new-two-bedroom-apartment-genuine-resale")
    for key, value in details.items():
        print(key, value)
        print("---------")

        