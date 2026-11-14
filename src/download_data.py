"""Télécharge les fichiers BDG2 nécessaires dans data/raw/.

Source : Building Data Genome Project 2 (Miller et al., 2020)
https://github.com/buds-lab/building-data-genome-project-2

Usage : python -m src.download_data
"""
from pathlib import Path
import urllib.request

BASE = "https://media.githubusercontent.com/media/buds-lab/building-data-genome-project-2/master/data"
FILES = {
    "electricity_cleaned.csv": f"{BASE}/meters/cleaned/electricity_cleaned.csv",
    "metadata.csv": f"{BASE}/metadata/metadata.csv",
    "weather.csv": f"{BASE}/weather/weather.csv",
}
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        dest = RAW_DIR / name
        if dest.exists() and dest.stat().st_size > 1_000:
            print(f"✓ {name} déjà présent ({dest.stat().st_size / 1e6:.1f} Mo)")
            continue
        print(f"↓ {name} ...")
        urllib.request.urlretrieve(url, dest)
        print(f"  {dest.stat().st_size / 1e6:.1f} Mo")


if __name__ == "__main__":
    main()
