import json, os
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

idx = json.loads((DATA / "routes_index.json").read_text(encoding="utf-8"))
print("routes_index.json entries:", len(idx))

kinds = {}
for r in idx:
    kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
print("By kind:", kinds)

found = {r["code"] for r in idx}
canonical_sample = ["C", "S-12", "AC-1", "12C", "V9", "HB9", "EB1", "M7B", "KB16", "230"]
present_sample = [c for c in canonical_sample if c in found]
print("Canonical repo routes sample present: {}/{}".format(len(present_sample), len(canonical_sample)))


geojson_files = list(DATA.glob("routes_*.geojson")) + ([DATA / "routes.geojson"] if (DATA / "routes.geojson").exists() else [])
total_features = 0
for f in DATA.glob("routes_*.geojson"):
    geo = json.loads(f.read_text(encoding="utf-8"))
    count = len(geo.get("features", []))
    total_features += count
    print(f"  {f.name}: {count} features ({f.stat().st_size / 1024:.1f} KB)")

print(f"Total GeoJSON features across files: {total_features}")

for f in ["routes_index.json", "busdata.json", "stops_geocoded.json"]:
    if (DATA / f).exists():
        size = os.path.getsize(DATA / f)
        print("  {}: {:.1f} KB".format(f, size / 1024))

