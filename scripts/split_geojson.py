"""Split routes.geojson into smaller files by kind, and minify routes_index.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

geo = json.loads((DATA / "routes.geojson").read_text(encoding="utf-8"))
features = geo["features"]

# Split by kind
by_kind = {}
for f in features:
    k = f["properties"].get("kind", "private")
    by_kind.setdefault(k, []).append(f)

for kind, feats in by_kind.items():
    out = {"type": "FeatureCollection", "features": feats}
    path = DATA / f"routes_{kind}.geojson"
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size = path.stat().st_size / 1024 / 1024
    print(f"  routes_{kind}.geojson  {len(feats)} routes  {size:.1f} MB")

# Remove the big combined file
(DATA / "routes.geojson").unlink(missing_ok=True)
print("Deleted routes.geojson")

# Also minify routes_index.json (remove pretty-print indent)
idx = json.loads((DATA / "routes_index.json").read_text(encoding="utf-8"))
(DATA / "routes_index.json").write_text(
    json.dumps(idx, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8"
)
size = (DATA / "routes_index.json").stat().st_size / 1024
print(f"routes_index.json minified to {size:.1f} KB")

# Minify stops_geocoded.json
stops = json.loads((DATA / "stops_geocoded.json").read_text(encoding="utf-8"))
(DATA / "stops_geocoded.json").write_text(
    json.dumps(stops, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8"
)
size = (DATA / "stops_geocoded.json").stat().st_size / 1024
print(f"stops_geocoded.json minified to {size:.1f} KB")
