from pathlib import Path
import re

DANGEROUS_PATTERNS = {
    "eval": re.compile(r"\beval\s*\("),
    "exec": re.compile(r"\bexec\s*\("),
    "new_function": re.compile(r"\bnew\s+Function\s*\("),
    "child_process": re.compile(r"\bchild_process\.(exec|spawn|fork)\s*\("),
    "deserialize": re.compile(r"\b(JSON\.parse|pickle\.loads|yaml\.load)\s*\("),
    "settimeout_string": re.compile(r"\bsetTimeout\s*\(\s*[\"']"),
}

JS_EXT = {".js", ".mjs", ".cjs"}

def _scan_file(path: Path):
    findings = []
    try:
        data = path.read_text(errors="ignore")
    except Exception:
        return findings

    for name, rx in DANGEROUS_PATTERNS.items():
        if rx.search(data):
            findings.append({
                "type": "dangerous",
                "sink": name,
                "file": str(path)
            })

    return findings

def hunt(target: Path):
    target = Path(target)
    results = []

    if target.is_file():
        return _scan_file(target)

    for path in target.rglob("*"):
        if path.suffix.lower() in JS_EXT:
            results.extend(_scan_file(path))

    return results
