# Kolkata Bus Routes Map

Interactive map of **all Kolkata bus routes** with geographically accurate paths and stop locations.

## What's included

- **1,919 bus/metro route records** from the [Kolkata Travel Router](https://github.com/Akash190104/kolkata-travel-router) Bus Repository dataset
- **2,233 unique stops** geocoded via:
  - Known hub coordinates (major junctions)
  - OpenStreetMap `highway=bus_stop` nodes in the Kolkata metro area
  - Nominatim geocoding fallback for remaining stops
- **Route geometries** drawn along roads (OSRM) or straight-line fallback between mapped stops
- **Web UI** with search, filters, route detail panel, and toggle to show all routes

## Quick start

### 1. Build the data

```bash
python scripts/build_all.py
```

Or step by step:

```bash
python scripts/fetch_osm_stops.py   # fetch OSM bus stop coordinates
python scripts/geocode_stops.py     # match + geocode all stop names (~7 min for Nominatim)
python scripts/build_routes.py      # generate routes.geojson
```

### 2. Serve the map

```bash
python -m http.server 8080
```

Open http://localhost:8080

## Data files

| File | Description |
|------|-------------|
| `data/busdata.json` | Raw route + stop names |
| `data/osm_bus_stops.json` | OSM bus stop coordinates |
| `data/stops_geocoded.json` | Final geocoded stop index |
| `data/routes.geojson` | Route line geometries + stop lists |
| `data/routes_index.json` | Lightweight route list for the UI |

## Notes

- There is no single official GTFS feed for all Kolkata buses. This map combines the best available community route lists with OSM/Nominatim coordinates.
- Routes with low stop coverage (<50% geocoded) are excluded from the map layer.
- "Show all routes" renders every mapped route at low opacity; select a route for full detail and stop markers.
- Geocoding results are cached in `data/geocode_cache.json` so rebuilds are faster.

## Sources

- Route data: [Akash190104/kolkata-travel-router](https://github.com/Akash190104/kolkata-travel-router) (Bus Repository)
- Stop coordinates: [OpenStreetMap](https://www.openstreetmap.org) via Overpass API & Nominatim
- Road routing: [OSRM](https://project-osrm.org/) (optional)
- Map tiles: CARTO dark basemap
