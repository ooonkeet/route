"""Build GeoJSON route geometries using OSRM road routing between stops."""
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BUSDATA = DATA / "busdata.json"
STOPS = DATA / "stops_geocoded.json"
ROUTES_OUT = DATA / "routes.geojson"
ROUTE_INDEX = DATA / "routes_index.json"
OSRM = "https://router.project-osrm.org/route/v1/driving"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(min(1, h ** 0.5))


def osrm_route(coords: list[tuple[float, float]]) -> list[list[float]] | None:
    if len(coords) < 2:
        return None
    # OSRM supports up to ~100 coordinates; chunk long routes
    all_points: list[list[float]] = []
    chunk_size = 25
    for start in range(0, len(coords) - 1, chunk_size - 1):
        chunk = coords[start : start + chunk_size]
        if len(chunk) < 2:
            continue
        path = ";".join(f"{lon},{lat}" for lat, lon in chunk)
        url = f"{OSRM}/{path}?overview=full&geometries=geojson"
        req = urllib.request.Request(url, headers={"User-Agent": "kolkata-bus-map/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            if data.get("code") != "Ok":
                return None
            geom = data["routes"][0]["geometry"]["coordinates"]
            if all_points and geom:
                geom = geom[1:]
            all_points.extend(geom)
        except Exception:
            return None
    return all_points or None


def straight_line(coords: list[tuple[float, float]]) -> list[list[float]]:
    return [[lon, lat] for lat, lon in coords]


def filter_outliers(points: list[tuple[float, float]], stop_features: list[dict]) -> tuple[list[tuple[float, float]], list[dict]]:
    if len(points) <= 3:
        return points, stop_features

    filtered_pts = [points[0]]
    filtered_stops = [stop_features[0]]

    for i in range(1, len(points) - 1):
        prev = filtered_pts[-1]
        curr = points[i]
        nxt = points[i + 1]

        d_prev_curr = haversine(prev, curr)
        d_curr_nxt = haversine(curr, nxt)
        d_prev_nxt = haversine(prev, nxt)

        # Detect sharp spike out of the linear corridor
        is_spike = (d_prev_curr > 5.0 and d_curr_nxt > 5.0 and (d_prev_curr + d_curr_nxt) > 2.5 * max(0.5, d_prev_nxt))
        if is_spike:
            continue

        filtered_pts.append(curr)
        filtered_stops.append(stop_features[i])

    filtered_pts.append(points[-1])
    filtered_stops.append(stop_features[-1])

    return filtered_pts, filtered_stops


def route_coords(route: dict, geocoded: dict) -> tuple[list[tuple[float, float]], list[dict]]:
    points = []
    stop_features = []
    for i, name in enumerate(route["stops"]):
        g = geocoded.get(name)
        if not g:
            continue
        lat, lon = g["lat"], g["lng"]
        points.append((lat, lon))
        stop_features.append({
            "name": name,
            "sequence": i + 1,
            "lat": lat,
            "lng": lon,
        })

    return filter_outliers(points, stop_features)


def main(use_osrm: bool = True, min_coverage: float = 0.5):
    busdata = load_json(BUSDATA)
    geocoded = load_json(STOPS)

    features = []
    index = []

    for route in busdata["routes"]:
        coords, stops = route_coords(route, geocoded)
        if len(coords) < 2:
            continue
        coverage = len(stops) / max(1, len(route["stops"]))
        if coverage < min_coverage:
            continue

        geometry = None
        geom_source = "straight"
        # Use OSRM only for routes with good geocoding coverage and manageable size
        if use_osrm and len(coords) <= 80 and coverage >= 0.70:
            geometry = osrm_route(coords)
            if geometry:
                geom_source = "osrm"

        if not geometry:
            geometry = straight_line(coords)
            geom_source = "straight"

        rid = f"{route['code']}|{route.get('towards','')}|{route['kind']}"
        props = {
            "id": rid,
            "code": route["code"],
            "kind": route.get("kind", "private"),
            "scope": route.get("scope", "local"),
            "towards": route.get("towards", ""),
            "directional": route.get("directional", False),
            "stop_count": len(route["stops"]),
            "geocoded_stops": len(stops),
            "coverage": round(coverage, 3),
            "geom_source": geom_source,
            "stops": stops,
            "origin": route["stops"][0] if route["stops"] else "",
            "destination": route["stops"][-1] if route["stops"] else "",
        }

        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": geometry},
            "properties": props,
        })
        index.append({
            "id": rid,
            "code": route["code"],
            "kind": route.get("kind", "private"),
            "scope": route.get("scope", "local"),
            "towards": route.get("towards", ""),
            "origin": props["origin"],
            "destination": props["destination"],
            "stop_count": len(route["stops"]),
            "geocoded_stops": len(stops),
            "coverage": round(coverage, 3),
        })

    geojson = {"type": "FeatureCollection", "features": features}
    ROUTES_OUT.write_text(json.dumps(geojson, ensure_ascii=False), encoding="utf-8")
    ROUTE_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {len(features)} routes -> {ROUTES_OUT}")


if __name__ == "__main__":
    main(use_osrm=False, min_coverage=0.0)

