"""Build the browser-safe local mobility basemap from Overpass JSON exports."""

import argparse
import json
from pathlib import Path


BOUNDS = {"south": 52.329, "west": 10.623, "north": 52.509, "east": 10.913}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    roads = {}
    for source in args.inputs:
        payload = json.loads(Path(source).read_text(encoding="utf-8"))
        for element in payload.get("elements", []):
            geometry = element.get("geometry") or []
            if len(geometry) < 2:
                continue
            roads[element["id"]] = {
                "kind": element.get("tags", {}).get("highway", "road"),
                "points": [
                    [round(point["lon"], 5), round(point["lat"], 5)] for point in geometry
                ],
            }
    output = {
        "bounds": BOUNDS,
        "attribution": "© OpenStreetMap-Mitwirkende, ODbL",
        "roads": list(roads.values()),
    }
    Path(args.output).write_text(
        json.dumps(output, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    print(f"roads={len(roads)}")


if __name__ == "__main__":
    main()
