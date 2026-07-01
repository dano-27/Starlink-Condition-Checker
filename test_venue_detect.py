import urllib.request
import urllib.parse
import json

lat = 40.7827725 # Central Park
lon = -73.9653627
radius = 250

query = f"""
[out:json];
(
  way["building"](around:{radius},{lat},{lon});
  way["natural"](around:{radius},{lat},{lon});
  way["landuse"](around:{radius},{lat},{lon});
  way["leisure"](around:{radius},{lat},{lon});
  way["waterway"](around:{radius},{lat},{lon});
);
out tags;
"""

url = "http://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={'User-Agent': 'Test'})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        buildings = 0
        water = 0
        forest = 0
        for el in data.get('elements', []):
            tags = el.get('tags', {})
            if 'building' in tags: buildings += 1
            if tags.get('natural') == 'water' or tags.get('natural') == 'coastline' or 'waterway' in tags: water += 1
            if tags.get('natural') == 'wood' or tags.get('landuse') == 'forest' or tags.get('leisure') == 'nature_reserve': forest += 1
            
        print(f"Buildings: {buildings}, Water: {water}, Forest: {forest}")
except Exception as e:
    print(e)
