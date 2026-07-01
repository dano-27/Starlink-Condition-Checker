import urllib.request
import json
import math

lat = 37.8023569652861
lon = -122.45699432525547

R = 6371
D = 1.5
pts = [{'lat': lat, 'lon': lon}]
for i in range(16):
    b = (i * 22.5) * math.pi / 180
    pts.append({
        'lat': lat + (D / R) * math.cos(b) * (180 / math.pi),
        'lon': lon + (D / R) * math.sin(b) / math.cos(lat * math.pi / 180) * (180 / math.pi)
    })

lats = ",".join(f"{p['lat']:.6f}" for p in pts)
lons = ",".join(f"{p['lon']:.6f}" for p in pts)

url = f"https://api.open-meteo.com/v1/elevation?latitude={lats}&longitude={lons}"

# Bypass SSL verify for test script
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(url, context=ctx) as response:
        data = json.loads(response.read().decode())
        elev = data['elevation']
        cElev = elev[0]
        angles = []
        dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
        print(f"Center Elev: {cElev}m")
        for i in range(16):
            sElev = elev[i+1]
            diff = sElev - cElev
            ang = math.atan2(diff, D * 1000) * 180 / math.pi
            angles.append(max(0, ang))
            print(f"Dir {dirs[i]}: {diff:.1f}m -> {max(0, ang):.1f} deg")
        
        avg_ang = sum(angles)/len(angles)
        max_ang = max(angles)
        print(f"Avg Angle: {avg_ang:.1f}")
        print(f"Max Angle: {max_ang:.1f}")
        
        score = 100 - avg_ang * 3.2 - max_ang * 1.4
        print(f"Base Math Score: {score:.1f}")
except Exception as e:
    print(e)
