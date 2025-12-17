from pathlib import Path
import json


def run(target: Path):
    for p in target.rglob("*.json"):
        try:
            data = json.loads(p.read_text())
            p.write_text(json.dumps(data, indent=2))
        except Exception:
            pass
