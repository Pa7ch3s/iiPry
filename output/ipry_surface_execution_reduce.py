#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="surface_execution_context.json")
    ap.add_argument("-o", "--out", default="execution_reduced")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    surfaces = data.get("surfaces", [])

    reduced = [
        s for s in surfaces
        if s.get("execution_risk") == "state-change"
    ]

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    outfile = outdir / "surface_execution_reduced.json"
    with open(outfile, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "count": len(reduced),
                "surfaces": reduced,
            },
            fh,
            indent=2,
        )

    print(f"[+] Surfaces input: {len(surfaces)}")
    print(f"[+] Surfaces kept (state-change): {len(reduced)}")
    print(f"[+] Output → {outfile}")


if __name__ == "__main__":
    main()
