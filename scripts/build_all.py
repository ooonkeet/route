"""Run full data pipeline: geocode stops then build route GeoJSON."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(script: str, *args):
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    print(">>", " ".join(cmd))
    subprocess.check_call(cmd)


if __name__ == "__main__":
    run("geocode_stops.py")
    run("build_routes.py")
