"""Fetch OSM bus stops in Kolkata & greater West Bengal metropolitan area.

Queries multiple overlapping regions and deduplicates by OSM node ID.
"""
import json
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "osm_bus_stops.json"

# Expanded: covers Kolkata urban + suburban areas including Howrah, Salt Lake,
# New Town, Barrackpore corridor, Barasat, EM Bypass areas, and far south Kolkata
BBOXES = [
    # Core Kolkata + Howrah
    (22.45, 88.25, 22.70, 88.45),
    # North: Barrackpore, Barasat, Dum Dum, Airport
    (22.65, 88.35, 22.85, 88.55),
    # East: Salt Lake, New Town, Rajarhat
    (22.55, 88.40, 22.70, 88.55),
    # South: Garia, Jadavpur, Behala
    (22.42, 88.28, 22.55, 88.42),
    # Far south: Diamond Harbour corridor
    (22.30, 88.18, 22.50, 88.38),
    # West Howrah: Uluberia, Domjur, Sankrail
    (22.47, 88.10, 22.68, 88.30),
    # Far north: Kalyani, Barrackpore, Bhatpara
    (22.75, 88.32, 23.00, 88.52),
]

QUERY_TEMPLATE = """\
[out:json][timeout:180];
(
  node["highway"="bus_stop"]({minlat},{minlon},{maxlat},{maxlon});
  node["public_transport"="platform"]["bus"="yes"]({minlat},{minlon},{maxlat},{maxlon});
  node["public_transport"="stop_position"]["bus"="yes"]({minlat},{minlon},{maxlat},{maxlon});
  node["amenity"="bus_station"]({minlat},{minlon},{maxlat},{maxlon});
  node["highway"="bus_stop"]["name"]({minlat},{minlon},{maxlat},{maxlon});
);
out body;
"""


def fetch_bbox(minlat, minlon, maxlat, maxlon):
    query = QUERY_TEMPLATE.format(
        minlat=minlat, minlon=minlon, maxlat=maxlat, maxlon=maxlon
    )
    req = urllib.request.Request(
        "https://overpass-api.de/api/interpreter",
        data=query.encode(),
        method="POST",
        headers={"User-Agent": "kolkata-bus-map/1.0 (education)", "Accept": "*/*"},
    )
    with urllib.request.urlopen(req, timeout=200) as resp:
        return json.loads(resp.read())


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    seen_ids = set()
    all_stops = []

    for i, bbox in enumerate(BBOXES):
        minlat, minlon, maxlat, maxlon = bbox
        print(f"Fetching bbox {i+1}/{len(BBOXES)}: ({minlat},{minlon}) -> ({maxlat},{maxlon})")
        try:
            raw = fetch_bbox(minlat, minlon, maxlat, maxlon)
        except Exception as e:
            print(f"  Error: {e}")
            continue

        count = 0
        for el in raw.get("elements", []):
            if el.get("type") != "node":
                continue
            node_id = el["id"]
            if node_id in seen_ids:
                continue
            seen_ids.add(node_id)
            tags = el.get("tags", {})
            name = (
                tags.get("name")
                or tags.get("name:en")
                or tags.get("local_name")
                or tags.get("ref")
                or ""
            )
            if not name:
                continue
            all_stops.append({
                "name": name,
                "lat": el["lat"],
                "lon": el["lon"],
                "id": node_id,
            })
            count += 1
        print(f"  Got {count} new stops (total: {len(all_stops)})")

    OUT.write_text(json.dumps(all_stops, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_stops)} OSM bus stops to {OUT}")


if __name__ == "__main__":
    main()
