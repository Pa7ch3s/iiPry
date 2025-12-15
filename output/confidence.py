def score(finding: dict):
    if not isinstance(finding, dict):
        return finding

    t = (finding.get("type") or "").lower()
    score = 30

    value = finding.get("value")
    if isinstance(value, str) and value:
        if len(value) > 8:
            score += 5

    evidence = finding.get("evidence")
    if not isinstance(evidence, list):
        evidence = []

    tags = set()
    files = set()

    for e in evidence:
        if not isinstance(e, dict):
            continue
        tag = e.get("tag")
        if isinstance(tag, str):
            tags.add(tag)
        fp = e.get("file")
        if isinstance(fp, str) and fp:
            files.add(fp.lower())

    if len(files) >= 2:
        score += 10

    if "auth-context" in tags:
        score += 20

    for fp in files:
        if any(x in fp for x in ("test", "tests", "mock", "example", "sample", "fixture", "__mocks__")):
            score -= 25

    if t == "dangerous":
        score += 10
    if t == "authflow":
        score += 5

    finding["confidence"] = max(0, min(100, score))
    return finding
