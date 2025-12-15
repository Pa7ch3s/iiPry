import re
from pathlib import Path

AUTH_WORDS = {
    "auth", "oauth", "oidc", "saml", "jwt", "token", "bearer",
    "login", "logout", "signin", "sign-in", "signup", "sign-up",
    "refresh", "session", "csrf", "xsrf", "mfa", "2fa", "password"
}

AUTH_RE = re.compile(r"(?i)\b(" + "|".join(re.escape(w) for w in sorted(AUTH_WORDS, key=len, reverse=True)) + r")\b")

def _safe_text(x):
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    return str(x)

def _read_snippet(path: Path, needle: str, max_len: int = 240):
    try:
        data = path.read_text(errors="ignore")
    except Exception:
        return ""
    if not needle:
        return ""
    i = data.lower().find(needle.lower())
    if i < 0:
        return ""
    start = max(0, i - 80)
    end = min(len(data), i + 80)
    s = data[start:end].replace("\n", " ").replace("\r", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s[:max_len]

def enrich(finding: dict):
    if not isinstance(finding, dict):
        return finding

    t = _safe_text(finding.get("type")).lower()
    v = _safe_text(finding.get("value"))
    fpath = _safe_text(finding.get("file"))

    value_l = v.lower()
    file_l = fpath.lower()

    evidence = finding.get("evidence")
    if not isinstance(evidence, list):
        evidence = []

    auth_hit = False
    m = AUTH_RE.search(value_l) or AUTH_RE.search(file_l)
    if m:
        auth_hit = True

    snippet = ""
    if fpath:
        try:
            p = Path(fpath)
            if p.exists() and p.is_file():
                snippet = _read_snippet(p, v if v else "", max_len=240)
                if snippet and AUTH_RE.search(snippet):
                    auth_hit = True
        except Exception:
            pass

    if auth_hit:
        evidence.append({"tag": "auth-context", "file": fpath, "value": v})

    if snippet:
        evidence.append({"tag": "snippet", "file": fpath, "value": snippet})

    finding["evidence"] = evidence
    return finding
