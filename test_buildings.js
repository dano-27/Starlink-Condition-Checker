const fetch = require('node-fetch');

async function getBuildingObstructions(lat, lon, horizonAngles) {
  const radius = 250; // meters
  const query = `[out:json];(way["building"](around:${radius},${lat},${lon});relation["building"](around:${radius},${lat},${lon}););out center tags;`;
  const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;
  
  try {
    const res = await fetch(url);
    const data = await res.json();
    if (!data.elements) return horizonAngles;

    const mergedAngles = JSON.parse(JSON.stringify(horizonAngles));
    let applied = 0;
    
    data.elements.forEach(el => {
      if (!el.center) return;
      const blat = el.center.lat, blon = el.center.lon;
      
      const R = 6371e3;
      const φ1 = lat * Math.PI/180, φ2 = blat * Math.PI/180;
      const Δφ = (blat-lat) * Math.PI/180, Δλ = (blon-lon) * Math.PI/180;
      const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ/2) * Math.sin(Δλ/2);
      const dist = R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)));

      if (dist < 5) return;

      const y = Math.sin(Δλ) * Math.cos(φ2);
      const x = Math.cos(φ1)*Math.sin(φ2) - Math.sin(φ1)*Math.cos(φ2)*Math.cos(Δλ);
      const bearing = (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;

      let height = 12;
      const tags = el.tags || {};
      if (tags.height) height = parseFloat(tags.height);
      else if (tags['building:levels']) height = parseFloat(tags['building:levels']) * 3.5;
      if (isNaN(height) || height <= 0) height = 12;

      const elevAngle = Math.atan2(height, dist) * 180 / Math.PI;
      const binIndex = Math.round(bearing / 22.5) % 16;
      
      if (elevAngle > mergedAngles[binIndex].angle) {
        mergedAngles[binIndex].angle = Math.round(elevAngle * 10) / 10;
        applied++;
      }
    });
    
    console.log(`Applied ${applied} buildings`);
    return mergedAngles;
  } catch(e) {
    console.error(e);
    return horizonAngles;
  }
}

const baseAngles = Array.from({ length: 16 }, (_, i) => ({ 
  dir: ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'][i], 
  bearing: i * 22.5, 
  angle: 0 
}));

// WTC area
getBuildingObstructions(40.7127, -74.0134, baseAngles).then(res => {
  console.log(res);
});
