#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from pathlib import Path


def classify(surface):
    value = surface.get("value", "") or ""
    if "auth" in value.lower():
        return "auth"
    if value.startswith("http"):
        return "endpoint"
    return "internal"


def hypotheses(surface):
    h = []

    if surface.get("auth_context"):
        h.append("Test privilege boundary handling")
        h.append("Check token reuse / escalation")

    if surface.get("source") == "url":
        h.append("Test parameter manipulation")
        h.append("Test unauthenticated access")

    if surface.get("cluster_size", 1) >= 5:
        h.append("High reuse surface — test deeper logic")

    if surface.get("signal_strength", 0) >= 4:
        h.append("Multi-signal convergence — prioritize")

    if not h:
        h.append("Baseline reachability + error handling")

    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shortlist", help="surface_shortlist.json")
    ap.add_argument("-o", "--out", default="annotated")
    args = ap.parse_args()

    data = json.load(open(args.shortlist, "r"))
    surfaces = data.get("surfaces", [])

    for s in surfaces:
        s["surface_type"] = classify(s)
        s["dynamic_hypotheses"] = hypotheses(s)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    out = outdir / "surface_test_plan.json"
    json.dump(
        {
            "count": len(surfaces),
            "surfaces": surfaces,
        },
        open(out, "w"),
        indent=2,
    )

    print(f"[+] Annotated surfaces: {len(surfaces)}")
    print(f"[+] Test plan → {out}")


if __name__ == "__main__":
    main()
