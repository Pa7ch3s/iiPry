from collections import defaultdict
from urllib.parse import urlparse
import re
import uuid


def _normalize_surface(f):
    ftype = f.get("type", "")
    raw = f.get("normalized") or f.get("value") or f.get("endpoint") or ""

    if not raw:
        return None

    surface = raw.strip()

    surface = re.sub(r"\$\{[^}]+\}", "", surface)
    surface = surface.rstrip("`,;'\"")

    if surface.startswith("http://") or surface.startswith("https://"):
        parsed = urlparse(surface)
        path = parsed.path.rstrip("/")
        surface = f"{parsed.scheme}://{parsed.netloc}{path}"

    surface = re.sub(r"/\d+", "/{id}", surface)

    return f"{ftype}:{surface}"


def correlate(findings):
    if not isinstance(findings, list):
        return findings

    index = defaultdict(list)

    for f in findings:
        key = _normalize_surface(f)
        if not key:
            continue
        index[key].append(f)

    for key, group in index.items():
        if len(group) < 1:
            continue

        ids = []
        types = set()

        for f in group:
            if "id" not in f:
                f["id"] = str(uuid.uuid4())
            ids.append(f["id"])
            types.add(f.get("type"))

        strength = 0

        if "endpoint" in types:
            strength += 1
        if "authflow" in types:
            strength += 2
        if "dangerous" in types:
            strength += 3

        if len(group) >= 2:
            strength += 2

        for f in group:
            f["correlation_key"] = key
            f["related"] = [i for i in ids if i != f["id"]]
            f["signal_strength"] = strength

    return findings
