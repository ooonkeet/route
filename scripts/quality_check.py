"""Quick quality report on the built route data."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

idx = json.loads((DATA / "routes_index.json").read_text(encoding="utf-8"))


total = len(idx)
high_cov  = sum(1 for r in idx if r["coverage"] >= 0.80)
med_cov   = sum(1 for r in idx if 0.60 <= r["coverage"] < 0.80)
low_cov   = sum(1 for r in idx if r["coverage"] < 0.60)
full_cov  = sum(1 for r in idx if r["coverage"] == 1.0)

print("=== Route Quality Report ===")
print("Total routes      :", total)
print("100% coverage     :", full_cov)
print(">= 80% coverage   :", high_cov)
print("60-80% coverage   :", med_cov)
print("< 60% coverage    :", low_cov)
print()

# Kind breakdown
kinds = {}
for r in idx:
    kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
print("By kind:")
for k, v in sorted(kinds.items()):
    print("  {:12s}: {}".format(k, v))
print()

# Scope breakdown
scopes = {}
for r in idx:
    scopes[r["scope"]] = scopes.get(r["scope"], 0) + 1
print("By scope:")
for k, v in sorted(scopes.items()):
    print("  {:12s}: {}".format(k, v))
print()

# Canonical repo sample routes
sample_codes = ["C", "S-12", "AC-1", "12C", "V9", "HB9", "EB1", "M7B", "KB16", "230"]
print("Canonical routes (sample):")
found_sample = {r["code"]: r for r in idx if r["code"] in sample_codes}
for code in sample_codes:
    r = found_sample.get(code)
    if r:
        print("  {:6s} | {} -> {} | cov:{:.0%}".format(
            r["code"], r["origin"], r["destination"], r["coverage"]))

