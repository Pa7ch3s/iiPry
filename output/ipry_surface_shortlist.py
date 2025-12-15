#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from pathlib import Path


def load_findings(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def prioritize(data, max_items):
    surfaces = data.get("surfaces", [])

    for s in surfaces:
        s["_strength"] = s.get("signal_strength", 0)
        s["_size"] = s.get("cluster_size", 1)
        s["_auth"] = bool(s.get("auth_context"))
        s["_external"] = s.get("source") == "url"

    surfaces.sort(
        key=lambda x: (x["_strength"], x["_size"]),
        reverse=True,
    )

    shortlisted = []
    seen = set()

    def add(item):
        key = item.get("cluster_key")
        if key in seen:
            return
        seen.add(key)
        shortlisted.append(item)

    top_n = max_items // 2
    for s in surfaces[:top_n]:
        add(s)

    for s in surfaces:
        if s["_auth"]:
            add(s)

    median_strength = (
        surfaces[len(surfaces) // 2]["_strength"]
        if surfaces
        else 0
    )

    for s in surfaces:
        if s["_external"] and s["_strength"] >= median_strength:
            add(s)

    for s in surfaces:
        if s["_size"] >= 5:
            add(s)

    return shortlisted[:max_items]


def write_outputs(outdir: Path, shortlist):
    outdir.mkdir(parents=True, exist_ok=True)

    json_path = outdir / "surface_shortlist.json"
    csv_path = outdir / "surface_shortlist.csv"

    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "count": len(shortlist),
                "surfaces": shortlist,
            },
            fh,
            indent=2,
        )

    with csv_path.open("w", encoding="utf-8") as fh:
        fh.write(
            "cluster_key,signal_strength,cluster_size,auth_context,source,value\n"
        )
        for s in shortlist:
            fh.write(
                f"{s.get('cluster_key')},"
                f"{s.get('signal_strength')},"
                f"{s.get('cluster_size')},"
                f"{s.get('auth_context')},"
                f"{s.get('source')},"
                f"\"{s.get('value','')}\"\n"
            )

    return json_path, csv_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("findings", help="path to findings.json")
    ap.add_argument("-o", "--out", default="shortlist")
    ap.add_argument("-n", "--max", type=int, default=50)
    args = ap.parse_args()

    data = load_findings(Path(args.findings))
    shortlist = prioritize(data, args.max)

    json_out, csv_out = write_outputs(Path(args.out), shortlist)

    print(f"[+] Shortlist items: {len(shortlist)}")
    print(f"[+] JSON → {json_out}")
    print(f"[+] CSV  → {csv_out}")


if __name__ == "__main__":
    main()
