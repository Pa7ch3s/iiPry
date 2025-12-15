from pathlib import Path
import re

AUTH_PATTERNS = [
    r"login",
    r"signin",
    r"signup",
    r"logout",
    r"refresh",
    r"oauth",
    r"token",
    r"auth",
    r"session"
]

def hunt(path: Path):
    findings = []
    for p in path.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in (".js", ".ts", ".json"):
            continue

        try:
            data = p.read_text(errors="ignore")
        except Exception:
            continue

        for pat in AUTH_PATTERNS:
            if re.search(pat, data, re.IGNORECASE):
                findings.append({
                    "type": "authflow",
                    "pattern": pat,
                    "file": str(p)
                })

    return findings
