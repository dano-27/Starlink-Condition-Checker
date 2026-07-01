import urllib.request
import urllib.parse
import json

lat, lon = 40.7127, -74.0134  # Near WTC
radius = 200 # meters

query = f"""
[out:json];
(
  way["building"](around:{radius},{lat},{lon});
  relation["building"](around:{radius},{lat},{lon});
);
out center tags;
"""

url = "http://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={'User-Agent': 'FelloSiteChecker/1.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        buildings_with_height = 0
        buildings_with_levels = 0
        total = len(data.get('elements', []))
        for el in data.get('elements', []):
            tags = el.get('tags', {})
            if 'height' in tags: buildings_with_height += 1
            elif 'building:levels' in tags: buildings_with_levels += 1
            
        print(f"Total buildings found: {total}")
        print(f"With exact height: {buildings_with_height}")
        print(f"With levels: {buildings_with_levels}")
        
        # print first 3 with levels or height
        printed = 0
        for el in data.get('elements', []):
            tags = el.get('tags', {})
            if 'height' in tags or 'building:levels' in tags:
                print(f"ID: {el['id']}, Name: {tags.get('name', 'Unknown')}, Height: {tags.get('height')}, Levels: {tags.get('building:levels')}")
                printed += 1
                if printed >= 3: break
except Exception as e:
    print("Error:", e)
