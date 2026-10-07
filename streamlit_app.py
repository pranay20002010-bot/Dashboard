"""Vika Wealth Macro Terminal - single-file Streamlit app (live free data: Yahoo, FRED, World Bank, NSE).
The code of the whole terminal is bundled below (compressed). Do not edit the blob; see GitHub source to change things."""
from __future__ import annotations

import base64, importlib.abc, importlib.util, json, linecache, sys, zlib

_BLOB = (
    "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"
)


class _Loader(importlib.abc.Loader):
    def __init__(self, data):
        self.d = data

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        m = self.d["mods"][module.__spec__.name]
        if module.__spec__.name == "vika_macro.ui":
            module.EMBEDDED_ASSETS = self.d["assets"]
        fn = "<vika:" + module.__spec__.name + ">"
        module.__file__ = __import__("os").path.join(__import__("os").getcwd(), "vika_macro", module.__spec__.name.split(".")[-1] + ".py")
        linecache.cache[fn] = (len(m["src"]), None, m["src"].splitlines(True), fn)
        exec(compile(m["src"], fn, "exec"), module.__dict__)


class _Finder(importlib.abc.MetaPathFinder):
    def __init__(self, data):
        self.d = data

    def find_spec(self, name, path=None, target=None):
        m = self.d["mods"].get(name)
        if m is None:
            return None
        return importlib.util.spec_from_loader(name, _Loader(self.d), is_package=m["pkg"])


if not any(isinstance(f, _Finder) for f in sys.meta_path):
    sys.meta_path.insert(0, _Finder(json.loads(zlib.decompress(base64.b64decode(_BLOB)))))

# ------------------------------------------------------------------ app
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from vika_macro import config, st_pages, store
from vika_macro.data import fr, yf
from vika_macro.ui import cols, html, inject_css, ticker_strip, topbar

IST = ZoneInfo("Asia/Kolkata")

st.set_page_config(page_title="Vika Macro Terminal", page_icon="📈", layout="wide",
                   initial_sidebar_state="collapsed")
inject_css()

# ------------------------------------------------------------------ live data (cached for hours, shared by all visitors)
NAMES = list(st_pages.PAGES)
_qp = st.query_params.get("page", "INDIA").upper()
_page_now = st.session_state.get("page") or (_qp if _qp in NAMES else "INDIA")
_WARM = {"FLOWS": ["flows"], "GLOBAL": ["worldbank"], "STATUS": ["flows", "worldbank"]}
with st.spinner("Loading live market data (first visit takes up to a minute, then it is cached)..."):
    store.prefetch(["yahoo", "fred"] + _WARM.get(_page_now, []))

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
