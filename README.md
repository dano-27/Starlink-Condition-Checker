# Fello Site Checker

**Instantly assess if your event venue is ready for Starlink satellite internet and cellular connectivity — no site visit needed.**

A single-page web application that evaluates any US location for Starlink readiness and cellular coverage quality using real terrain, weather, satellite, and carrier signal data. Built for [Fello](https://www.fello.com), a company that rents Starlink terminals to customers who need reliable internet at remote event venues.

---

## Features

### 🛰️ Starlink Site Assessment
Enter an event address and date to get a scored readiness report (0–100) based on:
- **Satellite Coverage** — Latitude-based Starlink orbital coverage model
- **Terrain Analysis** — 16-point horizon elevation profile using NASA ASTER data to detect hills, mountains, and obstructions
- **Weather Forecast** — Cloud cover, precipitation, and wind speed for the event date
- **Venue Detection** — Automatic identification of venue type (open field, urban, forest, waterfront, etc.) using OpenStreetMap land use data
- **Actionable Recommendations** — Step-by-step guidance based on site conditions

### 📶 Cellular Coverage Analysis
Standalone or paired with the Starlink assessment:
- **Carrier Comparison** — Side-by-side cards for Verizon, AT&T, and T-Mobile with tower counts and signal strength
- **Real Signal Strength** — dBm values from CoverageMap's enterprise API (FCC Broadband Data Collection + crowdsourced)
- **5G Status** — Definitive 5G Available / No 5G badges per carrier
- **Signal Range Chart** — Visualizes how signal degrades from the venue outward (¼ mi → ½ mi → 1 mi)
- **Coverage Reliability Score** — Weighted composite of signal strength (55%), consistency (25%), and coverage area (20%)
- **Interactive Tower Map** — Leaflet map with color-coded cell tower markers and coverage radius circles
- **Carrier Recommendation** — Plain-English advice on which carrier to use

---

## APIs Used

| API | Purpose | Cost |
|-----|---------|------|
| [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org) | Geocoding — address to lat/lon | Free |
| [OpenTopoData (NASA ASTER)](https://www.opentopodata.org) | Elevation & terrain profiling | Free |
| [Overpass API](https://overpass-api.de) | Building, land use, and venue detection | Free |
| [Open-Meteo](https://open-meteo.com) | Weather forecasting | Free |
| [OpenCelliD](https://opencellid.org) | Cell tower locations and radio types | Free (API key required) |
| [CoverageMap Enterprise](https://enterprise.coveragemap.com) | Signal strength (dBm), 5G confirmation, coverage % | Paid (14-day free trial) |
| [CartoDB + Leaflet](https://carto.com) | Interactive dark-themed maps | Free |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Browser (index.html)              │
│  Single-page app — all logic runs client-side       │
├─────────────────────────────────────────────────────┤
│  Direct API calls:                                  │
│   → Nominatim (geocoding)                           │
│   → OpenTopoData (elevation)                        │
│   → Overpass API (venue detection)                   │
│   → Open-Meteo (weather)                            │
│   → OpenCelliD (cell towers)                        │
│                                                     │
│  Via Cloudflare Worker proxy:                       │
│   → CoverageMap Enterprise (signal strength)        │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────▼──────────────┐
    │  Cloudflare Worker          │
    │  coveragemap-proxy          │
    │  (adds Authorization header │
    │   to bypass CORS)           │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │  CoverageMap Enterprise API │
    └─────────────────────────────┘
```

The CoverageMap API requires an `Authorization` header, which triggers CORS preflight requests that their server rejects. The Cloudflare Worker acts as a thin proxy that adds the auth header server-side.

---

## Setup

### Prerequisites
- A [CoverageMap Enterprise](https://enterprise.coveragemap.com) API key (14-day free trial, no credit card)
- An [OpenCelliD](https://opencellid.org) API key (free)
- Python 3 (for local development only)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/dano-27/Starlink-Condition-Checker.git
   cd Starlink-Condition-Checker
   ```

2. **Start the local server** (includes CoverageMap proxy)
   ```bash
   python3 server.py
   ```

3. **Open** `http://localhost:8000`

> **Note:** The local `server.py` proxies CoverageMap API requests to avoid CORS issues. For production, use the Cloudflare Worker instead.

### Production Deployment (GitHub Pages + Cloudflare Worker)

1. **Deploy the Cloudflare Worker**
   - Create a free account at [dash.cloudflare.com](https://dash.cloudflare.com)
   - Go to **Workers & Pages → Create → Create Worker**
   - Name it `coveragemap-proxy`
   - Replace the code with the contents of [`cloudflare-worker.js`](cloudflare-worker.js)
   - Click **Save and Deploy**

2. **Update the Worker URL** in `index.html`
   - Find the `getCoverageMapData` function
   - Replace the fetch URL with your worker URL:
     ```javascript
     const res = await fetch(`https://coveragemap-proxy.YOUR-SUBDOMAIN.workers.dev?latitude=${lat}&longitude=${lon}`);
     ```

3. **Enable GitHub Pages**
   - Go to your repo → Settings → Pages
   - Set source to `main` branch
   - Your site will be live at `https://your-username.github.io/Starlink-Condition-Checker/`

---

## Project Structure

```
├── index.html              # Complete single-page application (HTML + CSS + JS)
├── server.py               # Local development server with CoverageMap proxy
├── cloudflare-worker.js    # Cloudflare Worker for production CoverageMap proxy
└── README.md               # This file
```

---

## Configuration

API keys are stored directly in the source files:

| Key | Location | Variable |
|-----|----------|----------|
| OpenCelliD | `index.html` | `OPENCELLID_KEY` |
| CoverageMap | `server.py` / `cloudflare-worker.js` | `COVERAGEMAP_KEY` |

> ⚠️ **Security Note:** For production use, move API keys to environment variables. The Cloudflare Worker supports [secrets](https://developers.cloudflare.com/workers/configuration/secrets/) for this purpose.

---

## Coverage Reliability Scoring

The Coverage Reliability score uses a weighted formula based on real signal data from the CoverageMap API:

| Component | Weight | Calculation |
|-----------|--------|-------------|
| **Signal Strength** | 55% | Average dBm across venue + ¼/½/1 mile. -60 dBm = 100, -110 dBm = 0 |
| **Signal Consistency** | 25% | Drop from venue to worst point. < 5 dBm drop = 100, > 20 dBm = 0 |
| **Coverage Presence** | 20% | Carrier-reported coverage in the ¼ mile area |

**Score thresholds:**
- 🟢 80–100 = Reliable
- 🔵 60–79 = Good
- 🟡 40–59 = Fair
- 🟠 20–39 = Weak
- 🔴 0–19 = Poor

---

## License

MIT

---

Built by [Fello](https://www.fello.com) · Powered by open data and CoverageMap
