import urllib.request
import urllib.parse
import json
import math

lat = 40.812328
lon = -74.076899
radius = 500

query = f"""
[out:json];
(
  way["building"](around:{radius},{lat},{lon});
);
out center;
"""

url = "http://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={'User-Agent': 'Test'})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        buildings = len(data.get('elements', []))
        print(f"Buildings within {radius}m: {buildings}")
except Exception as e:
    print(e)
