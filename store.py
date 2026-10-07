"""Tiny flat-file store.  Each connector owns one long-format CSV in data/: series_id,date,value.

Set VIKA_DATA_DIR to relocate, or VIKA_DATA_URL to read the CSVs straight from a raw GitHub URL
(e.g. https://raw.githubusercontent.com/<you>/<repo>/main/data) so the hosted app picks up the
daily Action commits without redeploying.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("VIKA_DATA_DIR", ROOT / "data"))
URL = os.environ.get("VIKA_DATA_URL", "").rstrip("/")
TTL = 900  # seconds a remote/local read is reused

_cache: dict[str, tuple[float, object]] = {}


def _cached(key, loader):
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < TTL:
        return hit[1]
    val = loader()
    _cache[key] = (now, val)
    return val


def clear_cache():
    _cache.clear()


def _read_csv(name: str) -> pd.DataFrame:
    src = f"{URL}/{name}.csv" if URL else DATA / f"{name}.csv"
    try:
        df = pd.read_csv(src, parse_dates=["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.dropna(subset=["value"])
    except Exception:
        return pd.DataFrame(columns=["series_id", "date", "value"])


def load(name: str) -> pd.DataFrame:
    return _cached(f"csv:{name}", lambda: _read_csv(name))


def series(name: str, series_id: str) -> pd.Series:
    """One series as a date-indexed float Series (empty if missing)."""
    df = load(name)
    s = df[df["series_id"] == series_id].drop_duplicates("date", keep="last").set_index("date")["value"].sort_index()
    return s.astype(float)


def save(name: str, df: pd.DataFrame):
    """Merge into data/<name>.csv; new rows win; history is kept."""
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / f"{name}.csv"
    if path.exists():
        old = pd.read_csv(path, parse_dates=["date"])
        df = pd.concat([old, df], ignore_index=True)
    df = df.drop_duplicates(["series_id", "date"], keep="last").sort_values(["series_id", "date"])
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df.to_csv(path, index=False)
    clear_cache()


# ---------------------------------------------------------------- status log
def status_path() -> Path:
    return DATA / "status.json"


def read_status() -> dict:
    def _l():
        try:
            if URL:
                import requests
                return requests.get(f"{URL}/status.json", timeout=10).json()
            return json.loads(status_path().read_text())
        except Exception:
            return {}
    return _cached("status", _l)


def write_status(name: str, **kw):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        st = json.loads(status_path().read_text())
    except Exception:
        st = {}
    st[name] = {**kw, "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    status_path().write_text(json.dumps(st, indent=2))
    clear_cache()
