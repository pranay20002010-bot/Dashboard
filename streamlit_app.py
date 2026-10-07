"""Vika Wealth Macro Terminal - Streamlit app.   Run:  streamlit run streamlit_app.py"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from vika_macro import config, st_pages, store
from vika_macro.data import fr, yf
from vika_macro.ui import cols, html, inject_css, ticker_strip, topbar

IST = ZoneInfo("Asia/Kolkata")
ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="Vika Macro Terminal", page_icon=str(ROOT / "assets" / "favicon.png")
                   if (ROOT / "assets" / "favicon.png").exists() else "📈", layout="wide",
                   initial_sidebar_state="collapsed")
inject_css()

# ------------------------------------------------------------------ header
status = store.read_status()
n_ok = sum(v.get("status") == "OK" for v in status.values())
n_bad = sum(v.get("status") == "Error" for v in status.values())
led = "err" if n_bad else "ok" if status and n_ok == len(status) else "warn" if status else ""
ran = [v["ran_at"] for v in status.values() if v.get("ran_at")]
upd = pd.Timestamp(max(ran)).tz_convert(IST).strftime("%d-%b %H:%M IST") if ran else "never"
topbar(f"DATA {n_ok}/{len(status) or '–'} OK · updated {upd}", led, datetime.now(IST).strftime("%a %d-%b-%Y  %H:%M IST"))

ticker_strip([("NIFTY 50", yf("NIFTY50"), 0, "pct"), ("SENSEX", yf("SENSEX"), 0, "pct"),
              ("BANK NIFTY", yf("BANKNIFTY"), 0, "pct"), ("INDIA VIX", yf("INDIAVIX"), 2, "pct"),
              ("USD/INR", yf("USDINR"), 2, "pct"), ("GOLD $", yf("GOLD"), 0, "pct"), ("BRENT $", yf("BRENT"), 2, "pct"),
              ("DXY", yf("DXY"), 2, "pct"), ("S&P 500", yf("SPX"), 0, "pct"), ("US 10Y %", fr("US_10Y"), 2, "abs")])

# ------------------------------------------------------------------ navigation + controls
NAMES = list(st_pages.PAGES)
qp = st.query_params.get("page", "INDIA").upper()
if "page" not in st.session_state:
    st.session_state["page"] = qp if qp in NAMES else "INDIA"
page = st.segmented_control("PAGE", NAMES, key="page", label_visibility="collapsed") or "INDIA"
st.query_params["page"] = page

WINDOWS = {"1Y": 1, "3Y": 3, "5Y": 5, "MAX": 0}
ctx = dict(lookback=3, group="Market Cap", countries=["IND", "USA", "CHN"], wb_ind="NY.GDP.MKTP.KD.ZG", months=6)

if page in ("INDIA", "VALUATIONS", "GLOBAL", "SECTORS"):
    widths = {"INDIA": [2, 8], "VALUATIONS": [2, 3, 5], "GLOBAL": [2, 4, 3, 3], "SECTORS": [2, 2, 6]}[page]
    c = cols(widths)
    with c[0]:
        w = st.segmented_control("WINDOW", list(WINDOWS), default="3Y", key="win") or "3Y"
        ctx["lookback"] = WINDOWS[w]
    if page == "VALUATIONS":
        with c[1]:
            ctx["group"] = st.segmented_control("INDEX GROUP", list(config.PE_GROUPS), default="Market Cap", key="grp") or "Market Cap"
    if page == "GLOBAL":
        with c[1]:
            ctx["countries"] = st.multiselect("COUNTRIES (WORLD BANK PANELS)", list(config.WB_COUNTRIES),
                                              default=["IND", "USA", "CHN"], format_func=config.WB_COUNTRIES.get, key="cty")
        with c[2]:
            ctx["wb_ind"] = st.selectbox("WORLD BANK INDICATOR", list(config.WB_INDICATORS),
                                         format_func=lambda k: config.WB_INDICATORS[k][0], key="wbi")
    if page == "SECTORS":
        with c[1]:
            ctx["months"] = st.segmented_control("MONTHS", [3, 6, 9, 12], default=6, key="mon") or 6

# ------------------------------------------------------------------ page
try:
    st_pages.PAGES[page](ctx)
except Exception as e:  # a bad series must never blank the terminal
    st.error(f"Page error: {type(e).__name__}: {e}")

html('<div class="page-foot">Sources: Yahoo Finance · FRED · World Bank · NSE. Free public data, may be delayed; '
     'for research use only.</div>')
