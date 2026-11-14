"""Chargement des données BDG2 (réutilisé dans tous les notebooks)."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def load_metadata() -> pd.DataFrame:
    return pd.read_csv(RAW / "metadata.csv", index_col="building_id")


def load_weather(site_id: str | None = None) -> pd.DataFrame:
    w = pd.read_csv(RAW / "weather.csv", parse_dates=["timestamp"])
    if site_id is not None:
        w = w[w["site_id"] == site_id].drop(columns="site_id")
    return w.set_index("timestamp").sort_index()


def load_building(building_id: str) -> pd.DataFrame:
    """Électricité horaire (kWh) d'un bâtiment + météo de son site, sur un index horaire complet."""
    elec = pd.read_csv(
        RAW / "electricity_cleaned.csv",
        usecols=["timestamp", building_id],
        parse_dates=["timestamp"],
        index_col="timestamp",
    ).rename(columns={building_id: "kwh"})
    site = building_id.split("_")[0]
    weather = load_weather(site)
    full_index = pd.date_range(elec.index.min(), elec.index.max(), freq="h")
    df = elec.reindex(full_index).join(weather, how="left")
    df.index.name = "timestamp"
    return df
