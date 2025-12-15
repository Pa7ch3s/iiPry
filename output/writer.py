# -*- coding: utf-8 -*-

import json
import uuid
from pathlib import Path
from datetime import datetime


class OutputWriter:
    def __init__(self, outdir=None, quiet=False, pretty=False):
        self.quiet = quiet
        self.pretty = pretty

        if outdir:
            self.base = Path(outdir)
            self.base.mkdir(parents=True, exist_ok=True)
        else:
            self.base = Path("/tmp/ipry-test")

        self.workdir = self.base / str(uuid.uuid4())
        self.workdir.mkdir(parents=True, exist_ok=True)

        if not self.quiet:
            print(f"[+] Output → {self.workdir}")

    def write_findings(self, findings):
        dangerous = []
        surfaces = []

        for f in findings:
            ftype = f.get("type")
            cluster_size = f.get("cluster_size", 1)
            strength = f.get("signal_strength", 0)

            if ftype == "dangerous":
                dangerous.append(f)
                continue

            if cluster_size > 1 and strength >= 3:
                surfaces.append(f)

        payload = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "dangerous_count": len(dangerous),
            "surface_count": len(surfaces),
            "dangerous": dangerous,
            "surfaces": surfaces,
        }

        outfile = self.workdir / "findings.json"

        dump_kwargs = {}
        if self.pretty:
            dump_kwargs["indent"] = 2
        else:
            dump_kwargs["separators"] = (",", ":")

        with outfile.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, **dump_kwargs)

        if not self.quiet:
            print(f"[+] Dangerous Findings: {len(dangerous)}")
            print(f"[+] Attack Surfaces: {len(surfaces)}")
            print(f"[+] Saved: {outfile}")
