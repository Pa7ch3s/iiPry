from pathlib import Path
import re

from ipry.output.normalize import normalize_endpoint

URL_RE = re.compile(r"https?://[A-Za-z0-9\.\-_:]+(?:/[^\s\"\'\)]*)?")
PATH_RE = re.compile(r"(?:fetch|axios\.|XMLHttpRequest|\$\.ajax)\s*\(\s*[\"'](/[^\"']+)[\"']")
ROUTE_RE = re.compile(r"(?:app|router)\.(?:get|post|put|delete|patch)\s*\(\s*[\"'](/[^\"']+)[\"']")

JS_EXT = {".js", ".mjs", ".cjs"}
JSON_EXT = {".json"}

AUTH_HINTS = ("auth", "oauth", "oidc", "saml", "jwt", "token", "login", "signin", "signup", "refresh", "session", "csrf")

def _scan_file(path: Path):
    findings = []
    try:
        data = path.read_text(errors="ignore")
    except Exception:
        return findings

    file_s = str(path)
    file_l = file_s.lower()

    def emit(source: str, value: str):
        if value is None:
            return
        v = value if isinstance(value, str) else str(value)
        n = normalize_endpoint(v) if v.startswith("/") else v

        ev = [{"file": file_s}]
        auth_ctx = False
        if any(x in (v.lower() if isinstance(v, str) else "").lower() for x in AUTH_HINTS) or any(x in file_l for x in AUTH_HINTS):
            auth_ctx = True
            ev.append({"tag": "auth-context", "file": file_s, "value": v})

        finding = {
            "type": "endpoint",
            "source": source,
            "value": v,
            "normalized": n,
            "file": file_s,
            "evidence": ev,
            "auth_context": auth_ctx,
        }
        findings.append(finding)

    for m in URL_RE.findall(data):
        emit("url", m)

    for m in PATH_RE.findall(data):
        emit("http-client", m)

    for m in ROUTE_RE.findall(data):
        emit("server-route", m)

    return findings

def hunt(target: Path):
    target = Path(target)
    results = []

    if target.is_file():
        return _scan_file(target)

    for path in target.rglob("*"):
        suf = path.suffix.lower()
        if suf in JS_EXT or suf in JSON_EXT:
            results.extend(_scan_file(path))

    return results
