import re

UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.I
)

NUM_RE = re.compile(r"/\d+")
HEX_RE = re.compile(r"\b[0-9a-f]{16,}\b", re.I)
TOKEN_RE = re.compile(r"/[A-Za-z0-9_-]{20,}")

def normalize_endpoint(value: str):
    if not isinstance(value, str):
        return value

    v = value

    v = UUID_RE.sub("{uuid}", v)
    v = HEX_RE.sub("{hex}", v)
    v = TOKEN_RE.sub("/{token}", v)
    v = NUM_RE.sub("/{id}", v)

    return v
