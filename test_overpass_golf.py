import urllib.request
import urllib.parse
import json

lat = 40.83326316559694
lon = -74.69128592521571

query = f"""
[out:json];
(
  way["leisure"](around:500,{lat},{lon});
  way["landuse"](around:500,{lat},{lon});
  way["natural"](around:500,{lat},{lon});
);
out tags;
"""

url = "http://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={'User-Agent': 'Test'})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"Elements found: {len(data.get('elements', []))}")
        for el in data.get('elements', [])[:10]:
            print(el.get('tags', {}))
except Exception as e:
    print(e)
