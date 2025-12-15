def _key(f: dict):
    if not isinstance(f, dict):
        return None

    t = f.get("type") or ""
    v = f.get("value")
    n = f.get("normalized")

    if isinstance(n, str) and n:
        return (t, n)

    if isinstance(v, str):
        return (t, v)

    return (t, str(v))

def dedupe(findings):
    if not isinstance(findings, list):
        return []

    seen = set()
    out = []

    for f in findings:
        k = _key(f)
        if k is None:
            continue
        if k in seen:
            continue
        seen.add(k)
        out.append(f)

    return out
