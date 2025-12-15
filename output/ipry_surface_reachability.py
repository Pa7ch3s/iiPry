#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from pathlib import Path
import re


def classify_reachability(surface):
    value = surface.get("value", "") or ""
    auth = surface.get("auth_context", False)

    if value.startswith("http"):
        if auth:
            return "authenticated"
        return "unauthenticated"

    return "internal"


def classify_input_control(surface):
    value = surface.get("value", "") or ""

    if "?" in value:
        return "parameter-controlled"

    if re.search(r"/\{.*?\}", value):
        return "path-controlled"

    if surface.get("auth_context"):
        return "config-controlled"

    if value.startswith("http"):
        return "environment-controlled"

    return "hardcoded"


def control_confidence(surface, reachability, control):
    score = 0

    if reachability in ("unauthenticated", "authenticated"):
        score += 1

    if control in ("parameter-controlled", "path-controlled"):
        score += 1

    if control == "config-controlled" or surface.get("auth_context"):
        score += 1

    if surface.get("signal_strength", 0) >= 3:
        score += 1

    return score


def dynamic_ready(confidence, reachability):
    return confidence >= 2 and reachability != "internal"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="surface_reachability.json")
    ap.add_argument("-o", "--out", default="reachability")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    surfaces = data.get("surfaces", [])
    ready = 0

    for s in surfaces:
        reach = classify_reachability(s)
        control = classify_input_control(s)
        confidence = control_confidence(s, reach, control)

        s["reachability"] = reach
        s["input_control"] = control
        s["control_confidence"] = confidence
        s["dynamic_ready"] = dynamic_ready(confidence, reach)

        if s["dynamic_ready"]:
            ready += 1

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    outfile = outdir / "surface_reachability.json"
    with open(outfile, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "count": len(surfaces),
                "dynamic_ready": ready,
                "surfaces": surfaces,
            },
            fh,
            indent=2,
        )

    print(f"[+] Surfaces analyzed: {len(surfaces)}")
    print(f"[+] Dynamic-ready (final): {ready}")
    print(f"[+] Output → {outfile}")


if __name__ == "__main__":
    main()
