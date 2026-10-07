"""Streamlit UI building blocks: panels, KPI strip, ticker, styled tables."""
from __future__ import annotations

import base64
import inspect
from pathlib import Path

import pandas as pd
import streamlit as st

from . import theme as T
from .data import spark_text

ROOT = Path(__file__).resolve().parent.parent
CFG = {"displaylogo": False, "displayModeBar": "hover",
       "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]}
STALE_DAYS = {"D": 8, "M": 80, "Q": 200, "A": 500}


def _stretch(fn):
    return {"width": "stretch"} if "width" in inspect.signature(fn).parameters else {"use_container_width": True}


def html(s: str):
    st.markdown(s.replace("\n", ""), unsafe_allow_html=True)


def inject_css():
    css = (ROOT / "assets" / "terminal.css").read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def logo_uri() -> str:
    b = (ROOT / "assets" / "logo.svg").read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(b).decode()


# ------------------------------------------------------------------ panels
def _latest(series):
    ds = [s.index.max() for s in series if s is not None and len(s)]
    return max(ds) if ds else None


def panel(title, fig, unit="", source="", freq="D", series=(), note="", key=None):
    latest = _latest(series)
    if latest is None:
        meta, cls = "no data yet", "ftr-none"
    else:
        age = (pd.Timestamp.now() - latest).days
        stale = age > STALE_DAYS.get(freq, 30)
        meta = f"latest obs {latest:%d-%b-%Y}" + (f" · STALE ({age}d)" if stale else "")
        cls = "ftr-stale" if stale else "ftr-ok"
    with st.container(border=True):
        html(f'<div class="p-hdr"><span class="p-title">{title}</span><span class="p-unit">{unit}</span></div>')
        st.plotly_chart(fig, theme=None, config=CFG, key=key or f"pc:{title}", **_stretch(st.plotly_chart))
        html(f'<div class="p-ftr {cls}"><span class="dot">●</span><span>{source} · {meta}</span>'
             f'<span class="p-note">{note}</span></div>')


def table_panel(title, df: pd.DataFrame | None, meta="", color_cols=(), fmt=None, cond=None, height=None, empty_msg=None):
    with st.container(border=True):
        html(f'<div class="p-hdr"><span class="p-title">{title}</span><span class="p-unit">{meta}</span></div>')
        if df is None or df.empty:
            html(f'<div class="empty">{empty_msg or "NO DATA - run python -m vika_macro.update"}</div>')
            return
        sty = styled(df, color_cols=color_cols, fmt=fmt, cond=cond)
        h = height or min(36 * (len(df) + 1) + 3, 520)
        st.dataframe(sty, hide_index=True, height=h, key=f"df:{title}", **_stretch(st.dataframe))


def styled(df: pd.DataFrame, color_cols=(), fmt=None, cond=None):
    num = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    sty = df.style.format({c: "{:,.2f}" for c in num} | (fmt or {}), na_rep="-")
    mapper = getattr(sty, "map", None) or sty.applymap
    if color_cols:
        sty = mapper(lambda v: f"color:{T.UP}" if isinstance(v, (int, float)) and v > 0
                     else f"color:{T.DOWN}" if isinstance(v, (int, float)) and v < 0 else "", subset=list(color_cols))
    for col, fn in (cond or {}).items():
        sty = (getattr(sty, "map", None) or sty.applymap)(lambda v, fn=fn: fn(v), subset=[col])
    return sty


def notice(title, body):
    with st.container(border=True):
        html(f'<div class="p-hdr"><span class="p-title">{title}</span></div><div class="n-body">{body}</div>')


# ------------------------------------------------------------------ KPI + ticker
def _chg(s, mode):
    last, prev = s.iloc[-1], s.iloc[-2]
    return (last / prev - 1) * 100 if mode == "pct" else last - prev


def kpi_strip(items):
    """items: (label, series, dec, suffix, mode['pct'|'abs'], up_good)"""
    tiles = []
    for label, s, dec, suffix, mode, up_good in items:
        s = s.dropna() if s is not None else pd.Series(dtype=float)
        if len(s) < 2:
            tiles.append(f'<div class="kpi"><div class="k-lab">{label}</div><div class="k-val">—</div>'
                         f'<div class="k-chg muted">no data</div></div>')
            continue
        chg = _chg(s, mode)
        good = (chg >= 0) == up_good
        cls = "up" if (good and chg != 0) else "dn" if chg != 0 else "muted"
        arrow = "▲" if chg > 0 else "▼" if chg < 0 else "■"
        unit = "%" if mode == "pct" else " pp"
        tiles.append(f'<div class="kpi"><div class="k-lab">{label}</div><div class="k-val">{s.iloc[-1]:,.{dec}f}{suffix}</div>'
                     f'<div class="k-chg {cls}">{arrow} {abs(chg):.2f}{unit}</div>'
                     f'<div class="k-spark {cls}">{spark_text(s)}</div></div>')
    html(f'<div class="kpis">{"".join(tiles)}</div>')


def ticker_strip(items):
    """items: (label, series, dec, mode)"""
    tiles = []
    for label, s, dec, mode in items:
        if s is None or len(s.dropna()) < 2:
            tiles.append(f'<div class="tk"><div class="l">{label}</div><div class="v">—</div><div class="c muted">no data</div></div>')
            continue
        s = s.dropna()
        chg = _chg(s, mode)
        cls = "up" if chg > 0 else "dn" if chg < 0 else "muted"
        arrow = "▲" if chg > 0 else "▼" if chg < 0 else "■"
        tiles.append(f'<div class="tk"><div class="l">{label}</div><div class="v">{s.iloc[-1]:,.{dec}f}</div>'
                     f'<div class="c {cls}">{arrow} {abs(chg):.2f}{"%" if mode == "pct" else " pp"}</div></div>')
    html(f'<div class="ticker">{"".join(tiles)}</div>')


def topbar(status_text: str, led: str, clock: str):
    html(f'<div class="topbar"><div class="brand"><img src="{logo_uri()}"/><span class="b1">VIKA WEALTH</span>'
         f'<span class="b2">MACRO TERMINAL</span></div><div class="right"><div class="chip"><span class="led {led}"></span>'
         f'<span>{status_text}</span></div><div class="clock">{clock}</div></div></div>')


def cols(spans, gap="small"):
    return st.columns(spans, gap=gap)
