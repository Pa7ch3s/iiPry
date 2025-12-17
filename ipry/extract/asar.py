from pathlib import Path
import shutil
import subprocess


def _find_asar():
    return shutil.which("asar")


def extract(path: Path, outdir: Path):
    path = Path(path).resolve()
    target_dir = (outdir / path.stem).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    asar_bin = _find_asar()
    if not asar_bin:
        raise RuntimeError("asar tool not found (npm install -g asar)")

    proc = subprocess.run(
        [
            asar_bin,
            "extract",
            str(path),
            str(target_dir),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode(errors="ignore").strip())

    return target_dir
