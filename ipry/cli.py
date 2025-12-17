#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path
import shutil

from ipry import __version__
from ipry.update import run_update

from ipry.output.dedupe import dedupe
from ipry.output.context import enrich
from ipry.output.confidence import score
from ipry.output.correlate import correlate
from ipry.output.writer import OutputWriter

from ipry.extract import zip as extract_zip
from ipry.extract import asar as extract_asar
from ipry.extract import nupkg as extract_nupkg

from ipry.beautify import js as beautify_js
from ipry.beautify import json as beautify_json

from ipry.hunt import endpoint, dangerous, authflow


# -------------------------------------------------
# ANSI Colors
# -------------------------------------------------

C_RESET = "\033[0m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_CYAN = "\033[36m"
C_BOLD = "\033[1m"


# -------------------------------------------------
# Banner + Centered Header
# -------------------------------------------------

def print_banner():
    banner_path = Path(__file__).parent / "iiPry_Banner.txt"
    indent = "    "  # fixed left offset (2 tabs)

    raw_lines = []
    max_len = 0

    if banner_path.exists():
        raw_lines = banner_path.read_text().rstrip().splitlines()
        max_len = max(len(line) for line in raw_lines)

        for line in raw_lines:
            print(C_CYAN + indent + indent + line + C_RESET)
        print()

    title = "iiPry — Thick Client Surface Intelligence (static)"

    if max_len > len(title):
        pad = (max_len - len(title)) // 2
        title_line = indent + title
    else:
        title_line = indent + title

    print(C_BOLD + C_CYAN + title_line + C_RESET)
    print()


# -------------------------------------------------
# Help
# -------------------------------------------------

def print_help():
    print(f"""{C_GREEN}USAGE:{C_RESET}
  iiPry <file>
  iiPry hunt <file>
  iiPry update

{C_GREEN}OPTIONS:{C_RESET}
  -e            Extract only (no beautify)
  -b            Beautify only (no extract)
  -o <dir>      Output directory
  -H <list>     Hunters (endpoint,dangerous,authflow)
  --hunt        Enable all hunters
  -q            Quiet mode
  -v            Version
  -?, ?, help   Show this help

{C_GREEN}EXAMPLES:{C_RESET}
  iiPry app.asar
  iiPry hunt ./extracted_app
  iiPry hunt app.asar -o /tmp/ipry
  iiPry update

{C_YELLOW}DESCRIPTION:{C_RESET}
  iiPry performs static analysis on thick-client artifacts
  to identify reachable, state-changing attack surfaces.

  It does NOT exploit.
  It does NOT guess.
  It tells you what matters — and why.

{C_BLUE}Version:{C_RESET} {__version__}
""")


# -------------------------------------------------
# Archive detection / extraction
# -------------------------------------------------

def detect_archive(path: Path):
    name = path.name.lower()
    if name.endswith(".asar"):
        return "asar"
    if name.endswith(".nupkg"):
        return "nupkg"
    if name.endswith(".zip"):
        return "zip"
    return None


def run_extract(path: Path, outdir: Path):
    kind = detect_archive(path)

    if kind == "asar":
        return extract_asar.extract(path, outdir)
    if kind == "nupkg":
        return extract_nupkg.extract(path, outdir)
    if kind == "zip":
        return extract_zip.extract(path, outdir)

    return path


# -------------------------------------------------
# Beautification
# -------------------------------------------------

def run_beautify(target: Path):
    beautify_js.run(target)
    beautify_json.run(target)


# -------------------------------------------------
# Hunters
# -------------------------------------------------

def run_hunters(target: Path, enabled):
    findings = []

    if not enabled or "endpoint" in enabled:
        findings.extend(endpoint.hunt(target))

    if not enabled or "dangerous" in enabled:
        findings.extend(dangerous.hunt(target))

    if not enabled or "authflow" in enabled:
        findings.extend(authflow.hunt(target))

    return findings


# -------------------------------------------------
# Confidence + Signal filter
# -------------------------------------------------

def confidence_filter(findings):
    kept = []

    for f in findings:
        ftype = f.get("type", "")
        confidence = f.get("confidence", 0)
        strength = f.get("signal_strength", 0)

        if ftype == "endpoint" and (confidence >= 40 or strength >= 3):
            kept.append(f)
        elif ftype == "dangerous" and (confidence >= 20 or strength >= 3):
            kept.append(f)
        elif ftype == "authflow" and (confidence >= 10 or strength >= 3):
            kept.append(f)

    return kept


# -------------------------------------------------
# Core processing pipeline
# -------------------------------------------------

def process_target(target: Path, args):
    writer = OutputWriter(outdir=args.o, quiet=args.q)
    workdir = target

    if args.e or not args.b:
        workdir = run_extract(target, writer.workdir)

    if args.b or not args.e:
        run_beautify(workdir)

    enabled = args.H.split(",") if args.H else []

    findings = run_hunters(workdir, enabled)
    findings = dedupe(findings)
    findings = [score(f) for f in findings]
    findings = [enrich(f) for f in findings]
    findings = correlate(findings)
    findings = confidence_filter(findings)

    writer.write_findings(findings)
    return 0


# -------------------------------------------------
# CLI
# -------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(add_help=False)

    p.add_argument("command", nargs="?", help="hunt | update | <file>")
    p.add_argument("target", nargs="?", help="Target file")

    p.add_argument("-e", action="store_true")
    p.add_argument("-b", action="store_true")
    p.add_argument("-o", metavar="DIR")
    p.add_argument("-H", metavar="LIST")
    p.add_argument("--hunt", action="store_true")
    p.add_argument("-q", action="store_true")
    p.add_argument("-v", action="store_true")
    p.add_argument("-?", action="store_true", dest="help")

    return p


def main():
    print_banner()

    if len(sys.argv) == 1:
        print_help()
        return 0

    if sys.argv[1] in ("?", "help", "--help"):
        print_help()
        return 0

    parser = build_parser()
    args, _ = parser.parse_known_args()

    if args.help:
        print_help()
        return 0

    if args.v:
        print(__version__)
        return 0

    if args.command == "update":
        return run_update(quiet=args.q)

    if args.hunt:
        args.H = "endpoint,dangerous,authflow"

    if args.command == "hunt":
        if not args.target:
            print(f"{C_RED}iiPry hunt <file>{C_RESET}")
            return 1
        return process_target(Path(args.target).resolve(), args)

    if not args.command:
        print_help()
        return 1

    return process_target(Path(args.command).resolve(), args)


if __name__ == "__main__":
    sys.exit(main())
