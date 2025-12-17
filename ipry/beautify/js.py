from pathlib import Path
import shutil
import subprocess


def run(target: Path):
    jsb = shutil.which("js-beautify")
    if not jsb:
        return

    for p in target.rglob("*.js"):
        subprocess.run(
            [jsb, "-r", str(p)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
