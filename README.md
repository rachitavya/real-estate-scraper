# real-estate-scraper

I've put initial scraping files in the scraper directory.

Each file has a `scrape_house` function which takes `house_url` as a param and returns the object in the format:

```json
{
  "title": null,
  "slug": null,
  "description": null,
  "price": null,
  "is_poa": null,
  "bedrooms": null,
  "bathrooms": null,
  "location": null,
  "sub_location": null,
  "city": null,
  "property_type": null,
  "size": null,
  "amenities": null,
  "coordinates": null,
  "images": [],
  "url": "house_url",
  "rent_or_buy": null,
  "extra_fields": {}
}
```