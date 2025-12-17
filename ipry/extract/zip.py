from pathlib import Path
import zipfile
import shutil


def extract(path: Path, outdir: Path):
    path = Path(path)
    target_dir = outdir / path.stem
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(path, "r") as z:
            z.extractall(target_dir)
    except zipfile.BadZipFile:
        raise RuntimeError(f"Invalid zip archive: {path}")

    return target_dir
