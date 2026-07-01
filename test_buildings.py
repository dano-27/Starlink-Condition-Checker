import urllib.request
import urllib.parse
import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def bearing(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlam)
    theta = math.atan2(y, x)
    return (math.degrees(theta) + 360) % 360

lat = 40.7127
lon = -74.0134
radius = 250

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

angles = [{"dir": d, "angle": 0} for d in ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']]

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        applied = 0
        for el in data.get('elements', []):
            center = el.get('center')
            if not center: continue
            
            blat, blon = center['lat'], center['lon']
            dist = haversine(lat, lon, blat, blon)
            if dist < 5: continue
            
            b = bearing(lat, lon, blat, blon)
            
            h = 12
            tags = el.get('tags', {})
            if 'height' in tags:
                try: h = float(tags['height'])
                except: pass
            elif 'building:levels' in tags:
                try: h = float(tags['building:levels']) * 3.5
                except: pass
            
            elev_angle = math.degrees(math.atan2(h, dist))
            bin_index = round(b / 22.5) % 16
            
            if elev_angle > angles[bin_index]['angle']:
                angles[bin_index]['angle'] = round(elev_angle, 1)
                applied += 1
                
        print(f"Applied {applied} buildings")
        for a in angles:
            print(f"{a['dir']}: {a['angle']} degrees")
except Exception as e:
    print(e)
