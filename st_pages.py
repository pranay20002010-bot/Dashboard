"""Terminal pages (Streamlit).  Each function renders one page from ctx."""
from __future__ import annotations

import pandas as pd

from . import charts as C
from . import config, store
from . import theme as T
from .data import fl, fr, lab, month_returns, pe, wb_frame, wbs, yf, years_for
from .ui import cols, kpi_strip, notice, panel, table_panel

RET_COLS = ("1D", "1W", "1M", "3M", "6M", "1Y", "YTD")


# ------------------------------------------------------------------ INDIA
def india(ctx):
    L = ctx["lookback"]
    y = years_for(L)
    eq = {lab(i): yf(i) for i in ("NIFTY50", "NIFTYNEXT50", "NIFTYMID150", "NIFTYSML250")}
    cpi, gdp, gsec, vix, usd = fr("IN_CPI"), fr("IN_GDP"), fr("IN_10Y"), yf("INDIAVIX"), yf("USDINR")
    kpi_strip([("NIFTY 50", yf("NIFTY50"), 2, "", "pct", True), ("NIFTY BANK", yf("BANKNIFTY"), 2, "", "pct", True),
               ("INDIA VIX", vix, 2, "", "pct", False), ("USD/INR", usd, 2, "", "pct", False),
               ("INDIA 10Y", gsec, 2, "%", "abs", False), ("INDIA CPI", cpi, 2, "%", "abs", False),
               ("REAL GDP", gdp, 1, "%", "abs", True)])
    ret = C.rolling_table_returns({lab(i): yf(i) for i in ("NIFTY50", "SENSEX", "BANKNIFTY", "NIFTYNEXT50",
                                                            "NIFTYMID150", "NIFTYSML250", "NIFTY500")})
    a, b = cols([8, 4])
    with a:
        panel("Indian equities - rebased to 100", C.line(eq, years=y, rebase=True, height=330, dec=1),
              "Index, rebased", "Yahoo Finance", "D", eq.values())
    with b:
        table_panel("Index returns", ret, "% change", color_cols=RET_COLS, height=330 - 20)
    a, b, c = cols([4, 4, 4])
    with a:
        panel("Real GDP growth", C.bars({"Real GDP": gdp}, years=min(L, 6) if L else 8, posneg=True, dec=1, freq="Q",
                                        max_labels=24, height=290), "% YoY", "FRED (IMF)", "Q", [gdp])
    with b:
        panel("CPI inflation (RBI band 2-6%)", C.line({"India CPI": cpi}, years=max(y or 5, 2), height=290, fill_first=True,
                                                      hlines=[(4, "4% target", T.GOLD), (6, "6% upper", T.DOWN),
                                                              (2, "2% lower", T.MUTED)]), "% YoY", "FRED (OECD)", "M", [cpi])
    with c:
        panel("India 10Y G-sec yield", C.line({"India 10Y": gsec}, years=max(y or 5, 2), height=290, fill_first=True),
              "%", "FRED (OECD)", "M", [gsec])
    a, b, c = cols([4, 4, 4])
    with a:
        panel("India VIX", C.line({"India VIX": vix}, years=y, height=270, fill_first=True), "Index", "Yahoo Finance", "D", [vix])
    with b:
        panel("USD/INR", C.line({"USD/INR": usd}, years=y, height=270), "INR per USD", "Yahoo Finance", "D", [usd])
    with c:
        rel = (yf("BANKNIFTY") / yf("NIFTY50")).dropna()
        panel("Nifty Bank vs Nifty 50 (relative)", C.line({"Bank / Nifty 50": rel}, years=y, height=270, dec=3),
              "Ratio", "Yahoo Finance", "D", [yf("BANKNIFTY"), yf("NIFTY50")])


# ------------------------------------------------------------------ VALUATIONS
def valuations(ctx):
    L = ctx["lookback"] or 3
    group = ctx["group"] if ctx["group"] in config.PE_GROUPS else "Market Cap"
    items = config.PE_GROUPS[group]
    rows = []
    for disp, idx in items:
        sw = C.window(pe(idx), L)
        if len(sw):
            last = sw.iloc[-1]
            rows.append({"Index": disp, "P/E": last, f"{L}Y Avg": sw.mean(), "Max": sw.max(), "Min": sw.min(),
                         "Percentile": (sw <= last).mean() * 100, "vs Avg %": (last / sw.mean() - 1) * 100})
    df = pd.DataFrame(rows)
    cond = {"Percentile": lambda v: f"color:{T.DOWN}" if v > 80 else f"color:{T.UP}" if v < 20 else "",
            "vs Avg %": lambda v: f"color:{T.ORANGE}" if v > 15 else f"color:{T.UP}" if v < -15 else ""}
    table_panel(f"Valuation summary - {group}", df, f"lookback {L}Y · percentile = share of days at or below today's P/E",
                cond=cond, fmt={"Percentile": "{:.0f}", "vs Avg %": "{:+.1f}"},
                empty_msg="NO DATA - NSE Indices has not been fetched yet (see STATUS tab)")
    per_row = 4 if group == "Sectors" else 2
    for i in range(0, len(items), per_row):
        for col, (disp, idx) in zip(cols([1] * per_row), items[i:i + per_row]):
            with col:
                s = pe(idx)
                panel(disp, C.pe_panel(s, years=L), "Trailing P/E (x)", "NSE Indices", "D", [s])
    a, b = cols([1, 1])
    with a:
        s = pe("NIFTY 50", "pb")
        panel("Nifty 50 - P/B", C.line({"P/B": s}, years=L, height=250, fill_first=True), "x", "NSE Indices", "D", [s])
    with b:
        s = pe("NIFTY 50", "dy")
        panel("Nifty 50 - dividend yield", C.line({"Div yield": s}, years=L, height=250, fill_first=True), "%",
              "NSE Indices", "D", [s])


# ------------------------------------------------------------------ FLOWS
def flows(ctx):
    fii, dii = fl("fii_net"), fl("dii_net")
    if fii.empty and dii.empty:
        notice("FII / DII flows - waiting for first NSE fetch",
               "NSE publishes only the latest session, so history builds up from the first successful run of the daily "
               "update job. Check the STATUS tab if this stays empty.")
    else:
        first = min(fii.index.min(), dii.index.min())
        monthly = pd.DataFrame({"FII": fii.resample("ME").sum(), "DII": dii.resample("ME").sum()})
        daily = pd.DataFrame({"FII": fii, "DII": dii}).dropna(how="all").tail(60)
        cum = pd.DataFrame({"FII": fii.cumsum(), "DII": dii.cumsum()}).ffill()
        recent = daily.tail(10).iloc[::-1].copy()
        recent.insert(0, "Date", recent.index.strftime("%d-%b-%y"))
        recent["Net (FII+DII)"] = recent["FII"] + recent["DII"]
        kpi_strip([("FII NET (LAST SESSION)", fii.tail(2), 0, " cr", "abs", True),
                   ("DII NET (LAST SESSION)", dii.tail(2), 0, " cr", "abs", True)])
        colors = {"FII": T.MUTED, "DII": T.PURPLE}
        a, b = cols([8, 4])
        with a:
            panel("FII & DII net activity - monthly", C.bars({"FII": monthly["FII"], "DII": monthly["DII"]}, years=2,
                                                              colors=colors, height=320), "Rs crore",
                  "NSE (cash, provisional)", "D", [fii, dii], note=f"history since {first:%d-%b-%Y}")
        with b:
            table_panel("Last 10 sessions", recent, "Rs crore", color_cols=("FII", "DII", "Net (FII+DII)"),
                        fmt={c: "{:,.0f}" for c in ("FII", "DII", "Net (FII+DII)")}, height=330)
        a, b = cols([8, 4])
        with a:
            panel("Daily net flows - last 60 sessions", C.bars({"FII": daily["FII"], "DII": daily["DII"]}, years=None,
                                                               colors=colors, height=290, labels=False, freq="D"),
                  "Rs crore", "NSE (cash, provisional)", "D", [fii, dii])
        with b:
            panel("Cumulative net flows", C.line({"FII": cum["FII"], "DII": cum["DII"]}, years=None, height=290,
                                                 colors=colors, dec=0), "Rs crore", "NSE", "D", [fii, dii])
    notice("Mutual fund flows & SIP data (AMFI) - not automated yet",
           "AMFI publishes monthly industry data as Excel/PDF without a stable API. A scraper connector is the next build "
           "item; it will land here with no manual upload.")


# ------------------------------------------------------------------ GLOBAL
def global_macro(ctx):
    y = years_for(ctx["lookback"])
    countries = ctx["countries"] or ["IND", "USA", "CHN"]
    ind = ctx["wb_ind"] if ctx["wb_ind"] in config.WB_INDICATORS else "NY.GDP.MKTP.KD.ZG"
    name, unit = config.WB_INDICATORS[ind]
    gl_idx = {lab(i): yf(i) for i in ("NIFTY50", "SPX", "NDX", "DAX", "NIKKEI", "HSI", "FTSE")}
    heat = month_returns(["NIFTY50", "NIFTYNEXT50", "NIFTYMID150", "NIFTYSML250", "NIFTY500", "SPX", "DJI", "NDX",
                          "FTSE", "DAX", "CAC", "NIKKEI", "HSI"])
    idx_ret = C.rolling_table_returns({lab(i): yf(i) for i in ("NIFTY50", "NIFTYNEXT50", "NIFTYMID150", "NIFTYSML250",
                                                                "SPX", "DJI", "NDX", "FTSE", "DAX", "CAC", "NIKKEI", "HSI")})
    gold, silver, usd = yf("GOLD"), yf("SILVER"), yf("USDINR")
    gold_inr = (gold * usd.reindex(gold.index).ffill() / 31.1035 * 10).dropna()
    us10, us2, ff, curve = fr("US_10Y"), fr("US_2Y"), fr("FED_FUNDS"), fr("US_CURVE")
    ym = max(y or 5, 2)
    kpi_strip([("S&P 500", yf("SPX"), 2, "", "pct", True), ("NASDAQ", yf("NDX"), 2, "", "pct", True),
               ("US 10Y", us10, 2, "%", "abs", False), ("DXY", yf("DXY"), 2, "", "pct", False),
               ("GOLD $", gold, 1, "", "pct", True), ("BRENT $", yf("BRENT"), 2, "", "pct", False),
               ("VIX", yf("VIX"), 2, "", "pct", False)])
    a, b = cols([8, 4])
    with a:
        panel("Global indices - rebased to 100", C.line(gl_idx, years=y, rebase=True, height=330, dec=1),
              "Index, rebased", "Yahoo Finance", "D", gl_idx.values())
    with b:
        table_panel("Index returns", idx_ret, "% change", color_cols=RET_COLS, height=310)
    panel("Monthly returns - ranked best to worst", C.rank_heatmap(heat, height=420), "% MoM (* = month to date)",
          "Yahoo Finance", "D", [yf("NIFTY50"), yf("SPX")])
    a, b, c = cols([4, 4, 4])
    with a:
        panel("Gold & Silver", C.line({"Gold (USD/oz)": gold, "Silver (USD/oz)": silver}, years=y, height=290,
                                      secondary=("Silver (USD/oz)",),
                                      colors={"Gold (USD/oz)": T.GOLD, "Silver (USD/oz)": T.CYAN}),
              "USD per troy oz", "Yahoo Finance (futures)", "D", [gold, silver])
    with b:
        panel("Gold in INR / 10g (ex duty & GST)", C.line({"Gold INR/10g": gold_inr}, years=y, height=290, dec=0,
                                                          fill_first=True), "INR", "Computed: Gold x USD/INR", "D", [gold, usd])
    with c:
        panel("Currency rates", C.line({"EUR/INR": yf("EURINR"), "GBP/INR": yf("GBPINR"), "USD/INR": usd,
                                        "JPY/INR": yf("JPYINR")}, years=y, height=290,
                                       colors={"EUR/INR": T.PURPLE, "GBP/INR": T.PINK, "USD/INR": T.GOLD, "JPY/INR": T.ORANGE}),
              "INR per unit", "Yahoo Finance", "D", [usd])
    a, b, c = cols([4, 4, 4])
    with a:
        panel("US interest rates", C.line({"US 10Y": us10, "US 2Y": us2, "Fed Funds": ff}, years=y, height=290,
                                          colors={"US 10Y": T.GOLD, "US 2Y": T.PURPLE, "Fed Funds": T.CYAN}),
              "%", "FRED", "D", [us10, us2, ff])
    with b:
        panel("US yield curve (10Y - 2Y)", C.spread(curve, years=y or 10, height=290), "pp", "FRED", "D", [curve])
    with c:
        panel("US dollar index", C.line({"DXY": yf("DXY")}, years=y, height=290, fill_first=True), "Index",
              "Yahoo Finance", "D", [yf("DXY")])
    a, b, c = cols([4, 4, 4])
    with a:
        panel("Inflation - US, India, China", C.line({"US": fr("US_CPI"), "India": fr("IN_CPI"), "China": fr("CN_CPI")},
                                                     years=ym, height=290,
                                                     colors={"US": T.PURPLE, "India": T.GOLD, "China": T.CYAN}),
              "% YoY", "FRED / OECD", "M", [fr("US_CPI"), fr("IN_CPI"), fr("CN_CPI")])
    with b:
        panel("US unemployment rate", C.line({"US": fr("US_UNEMP")}, years=ym, height=290, fill_first=True), "%",
              "FRED", "M", [fr("US_UNEMP")])
    with c:
        panel("Crude oil & copper", C.line({"Brent": yf("BRENT"), "WTI": yf("WTI"), "Copper (USD/lb)": yf("COPPER")},
                                           years=y, height=290, secondary=("Copper (USD/lb)",),
                                           colors={"Brent": T.GOLD, "WTI": T.PURPLE, "Copper (USD/lb)": T.ORANGE}),
              "USD", "Yahoo Finance (futures)", "D", [yf("BRENT"), yf("WTI")])
    a, b = cols([1, 1])
    with a:
        panel(f"{name} - country comparison", C.wb_bars(wb_frame(ind, countries), unit, height=320), unit,
              "World Bank", "A", [wbs(ind, c) for c in countries])
    with b:
        fdi = "BX.KLT.DINV.WD.GD.ZS"
        panel("FDI net inflows - country comparison", C.wb_bars(wb_frame(fdi, countries), "% of GDP", height=320),
              "% of GDP", "World Bank", "A", [wbs(fdi, c) for c in countries])


# ------------------------------------------------------------------ SECTORS
SECTOR_IDS = ["S_IT", "S_AUTO", "S_PHARMA", "S_FMCG", "S_METAL", "S_ENERGY", "S_REALTY", "S_MEDIA", "S_INFRA", "S_FIN",
              "S_PSUBANK", "BANKNIFTY"]


def sectors(ctx):
    y = years_for(ctx["lookback"])
    heat = month_returns(SECTOR_IDS, n=int(ctx.get("months") or 6))
    rets = C.rolling_table_returns({lab(i): yf(i) for i in SECTOR_IDS})
    sec = {lab(i): yf(i) for i in SECTOR_IDS}
    a, b = cols([8, 4])
    with a:
        panel("Sector monthly performance - ranked best to worst", C.rank_heatmap(heat, height=440),
              "% MoM (* = month to date)", "Yahoo Finance (NSE sector indices)", "D", sec.values())
    with b:
        table_panel("Sector returns", rets, "% change", color_cols=RET_COLS, height=470)
    panel("Sector performance - rebased to 100", C.line(sec, years=y or 5, rebase=True, height=420, dec=1),
          "Index, rebased", "Yahoo Finance", "D", sec.values())


# ------------------------------------------------------------------ STATUS
NOT_AUTOMATED = [
    ("India PMI (Mfg & Services)", "HSBC / S&P Global", "Proprietary; headline only in press releases"),
    ("GST collections", "GST Council / PIB", "Monthly press release - scrape candidate"),
    ("Merchandise & services trade balance", "Ministry of Commerce / RBI", "Press release / RBI DBIE - scrape candidate"),
    ("Auto sales", "FADA", "Monthly press release - scrape candidate"),
    ("Mutual fund flows, SIP data", "AMFI", "Monthly Excel/PDF - scrape candidate"),
    ("WPI inflation, IIP", "DPIIT / MoSPI", "MoSPI eSankhyiki API to be evaluated"),
    ("Market cap to GDP", "NSE/BSE + MoSPI", "Compute once GDP and market-cap feeds are wired"),
    ("China unemployment, China 1Y LPR, PMIs (US/China)", "NBS / PBoC / S&P Global", "No free stable API"),
]


def status(ctx):
    st_ = store.read_status()
    rows = [{"Source": v.get("label", k), "Status": v.get("status", "?"), "Last obs": v.get("last_obs") or "-",
             "Series": v.get("series", 0), "Records": v.get("records", 0),
             "Ran at (UTC)": v.get("ran_at", "-")[:16].replace("T", " "), "Issues": "; ".join(v.get("errors", []))[:300] or "-"}
            for k, v in st_.items()]
    stat_col = {"Status": lambda v: f"color:{T.UP}" if v == "OK" else f"color:{T.GOLD}" if v == "Warning"
                else f"color:{T.DOWN}" if v == "Error" else ""}
    table_panel("Data connectors", pd.DataFrame(rows), "one row per source - a failure never stops the dashboard",
                cond=stat_col, fmt={"Series": "{:,.0f}", "Records": "{:,.0f}"},
                empty_msg="No update has run yet. Run  python -m vika_macro.update  (or the GitHub Action).")
    expect = ([("yahoo", i, l) for i, l, *_ in config.YAHOO] + [("fred", k, v["label"]) for k, v in config.FRED.items()]
              + [("flows", "fii_net", "FII net"), ("flows", "dii_net", "DII net")]
              + [("valuations", f"pe|{idx}", f"P/E {d}") for g in config.PE_GROUPS.values() for d, idx in g])
    cov = []
    for src, sid, label in expect:
        s = store.series(src, sid)
        age = (pd.Timestamp.now() - s.index.max()).days if len(s) else None
        cov.append({"Series": label, "Feed": src, "Last obs": s.index.max().strftime("%Y-%m-%d") if len(s) else "-",
                    "Age (d)": age if age is not None else None, "Rows": len(s),
                    "State": "MISSING" if age is None else "STALE" if age > 10 else "FRESH"})
    cov_col = {"State": lambda v: f"color:{T.UP}" if v == "FRESH" else f"color:{T.GOLD}" if v == "STALE"
               else f"color:{T.DOWN}" if v == "MISSING" else ""}
    a, b = cols([7, 5])
    with a:
        table_panel("Series coverage", pd.DataFrame(cov), "STALE = older than 10 days (monthly series are expected to be older)",
                    cond=cov_col, fmt={"Age (d)": "{:,.0f}", "Rows": "{:,.0f}"}, height=520)
    with b:
        table_panel("From the deck, not yet automated",
                    pd.DataFrame(NOT_AUTOMATED, columns=["Deck item", "Source", "Status / path to automation"]),
                    "next connectors", height=330)


PAGES = {"INDIA": india, "VALUATIONS": valuations, "FLOWS": flows, "GLOBAL": global_macro, "SECTORS": sectors,
         "STATUS": status}
