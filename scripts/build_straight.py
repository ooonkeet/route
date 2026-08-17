"""Build routes.geojson and routes_index.json using straight-line geometry (fast, no OSRM)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

busdata = json.loads((DATA / "busdata.json").read_text(encoding="utf-8"))
geocoded = json.loads((DATA / "stops_geocoded.json").read_text(encoding="utf-8"))

features = []
index = []

for route in busdata["routes"]:
    stops_out = []
    coords = []
    for i, name in enumerate(route["stops"]):
        g = geocoded.get(name)
        if not g:
            continue
        coords.append([g["lng"], g["lat"]])
        stops_out.append({"name": name, "sequence": i + 1, "lat": g["lat"], "lng": g["lng"]})

    if len(coords) < 2:
        continue
    coverage = len(stops_out) / max(1, len(route["stops"]))
    if coverage < 0.45:
        continue

    rid = "{}|{}|{}".format(route["code"], route.get("towards", ""), route.get("kind", "private"))
    props = {
        "id": rid,
        "code": route["code"],
        "kind": route.get("kind", "private"),
        "scope": route.get("scope", "local"),
        "towards": route.get("towards", ""),
        "directional": route.get("directional", False),
        "stop_count": len(route["stops"]),
        "geocoded_stops": len(stops_out),
        "coverage": round(coverage, 3),
        "geom_source": "straight",
        "stops": stops_out,
        "origin": route["stops"][0] if route["stops"] else "",
        "destination": route["stops"][-1] if route["stops"] else "",
    }
    features.append({
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coords},
        "properties": props,
    })
    index.append({
        "id": rid,
        "code": route["code"],
        "kind": props["kind"],
        "scope": props["scope"],
        "towards": props["towards"],
        "origin": props["origin"],
        "destination": props["destination"],
        "stop_count": props["stop_count"],
        "geocoded_stops": props["geocoded_stops"],
        "coverage": props["coverage"],
    })

geojson = {"type": "FeatureCollection", "features": features}
(DATA / "routes.geojson").write_text(json.dumps(geojson, ensure_ascii=False), encoding="utf-8")
(DATA / "routes_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
print("Built {} routes ({} index entries)".format(len(features), len(index)))
