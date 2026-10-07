"""Read-side helpers shared by the pages (no UI imports)."""
from __future__ import annotations

import pandas as pd

from . import config, store


def yf(sid): return store.series("yahoo", sid)
def fr(sid): return store.series("fred", sid)
def wbs(ind, iso): return store.series("worldbank", f"{ind}|{iso}")
def fl(sid): return store.series("flows", sid)
def pe(idx, kind="pe"): return store.series("valuations", f"{kind}|{idx}")
def lab(sid): return config.yahoo_label(sid)


def years_for(lookback, bars=False):
    """lookback in years (0/None = all history)."""
    if not lookback:
        return None
    return min(lookback, 2) if bars else lookback


def wb_frame(ind, countries) -> pd.DataFrame:
    """Years x country-name frame of a World Bank indicator (empty frame if nothing fetched yet)."""
    d = {config.WB_COUNTRIES[c]: wbs(ind, c) for c in countries}
    d = {k: v for k, v in d.items() if len(v)}
    if not d:
        return pd.DataFrame()
    df = pd.DataFrame(d).sort_index()
    df.index = df.index.year
    return df


def month_returns(ids, n=6) -> pd.DataFrame:
    """Rows = series label, columns = last n month labels ('*' marks the month to date)."""
    d = {}
    for sid in ids:
        s = yf(sid)
        if len(s) < 40:
            continue
        d[lab(sid)] = s.resample("ME").last().pct_change() * 100
    if not d:
        return pd.DataFrame()
    df = pd.DataFrame(d).T.dropna(axis=1, how="all").iloc[:, -n:]
    last_obs = max(yf(i).index.max() for i in ids if len(yf(i)))
    cols = []
    for c in df.columns:
        partial = (c.year, c.month) == (last_obs.year, last_obs.month) and last_obs < c
        cols.append(c.strftime("%b-%y") + ("*" if partial else ""))
    df.columns = cols
    return df


SPARK = "▁▂▃▄▅▆▇█"


def spark_text(s: pd.Series, n=28) -> str:
    s = s.dropna().tail(n)
    if len(s) < 2 or s.max() == s.min():
        return ""
    z = (s - s.min()) / (s.max() - s.min())
    return "".join(SPARK[min(7, int(v * 8))] for v in z)
