#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from pathlib import Path


ELECTRON_MAIN_HINTS = [
    "app.on(",
    "BrowserWindow",
    "ipcMain",
    "protocol.register",
    "session.defaultSession",
    "require('electron').app",
    "require(\"electron\").app",
]

ELECTRON_RENDERER_HINTS = [
    "ipcRenderer",
    "window.",
    "document.",
    "fetch(",
    "XMLHttpRequest",
]

CODE_LOADING_HINTS = [
    "require(",
    "import(",
    "loadURL(",
    "loadFile(",
    "eval(",
    "new Function",
]


def infer_execution_context(surface):
    file = surface.get("file", "") or ""
    value = surface.get("value", "") or ""

    if surface.get("source") == "url":
        return "remote"

    for hint in ELECTRON_MAIN_HINTS:
        if hint in value or hint in file:
            return "main"

    for hint in ELECTRON_RENDERER_HINTS:
        if hint in value or hint in file:
            return "renderer"

    if "ipc" in value.lower():
        return "ipc"

    return "unknown"


def infer_boundary(surface, context):
    if context == "ipc":
        return "renderer->main"

    if context == "remote":
        return "client->server"

    if context == "renderer":
        return "renderer-only"

    if context == "main":
        return "local-only"

    return "unknown"


def infer_execution_risk(surface):
    value = surface.get("value", "") or ""

    for hint in CODE_LOADING_HINTS:
        if hint in value:
            return "code-loading"

    if surface.get("type") == "dangerous":
        return "privileged"

    if surface.get("auth_context"):
        return "state-change"

    return "read-only"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="surface_reachability.json")
    ap.add_argument("-o", "--out", default="execution_context")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    surfaces = data.get("surfaces", [])

    for s in surfaces:
        context = infer_execution_context(s)
        boundary = infer_boundary(s, context)
        risk = infer_execution_risk(s)

        s["execution_context"] = context
        s["boundary"] = boundary
        s["execution_risk"] = risk

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    outfile = outdir / "surface_execution_context.json"
    with open(outfile, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "count": len(surfaces),
                "surfaces": surfaces,
            },
            fh,
            indent=2,
        )

    print(f"[+] Surfaces analyzed: {len(surfaces)}")
    print(f"[+] Output → {outfile}")


if __name__ == "__main__":
    main()
