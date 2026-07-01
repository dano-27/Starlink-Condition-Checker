import urllib.request
import urllib.parse
import json

lat = 37.8023569652861
lon = -122.45699432525547

query = f"""
[out:json];
(
  way["building"](around:250,{lat},{lon});
  way["natural"](around:500,{lat},{lon});
);
out center tags;
"""

url = "http://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={'User-Agent': 'Test'})

import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        buildings = [el for el in data.get('elements', []) if 'building' in el.get('tags', {})]
        print(f"Buildings: {len(buildings)}")
        trees = [el for el in data.get('elements', []) if 'wood' in el.get('tags', {}).get('natural','')]
        print(f"Trees: {len(trees)}")
except Exception as e:
    print(e)
