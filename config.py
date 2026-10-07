"""What the terminal tracks. Everything here comes from a free, keyless public source."""
from __future__ import annotations

# --------------------------------------------------------------------------- Yahoo Finance
# (series id, label, ticker, group)
YAHOO = [
    # India broad market
    ("NIFTY50", "Nifty 50", "^NSEI", "india"),
    ("SENSEX", "Sensex", "^BSESN", "india"),
    ("BANKNIFTY", "Nifty Bank", "^NSEBANK", "india"),
    ("NIFTYNEXT50", "Nifty Next 50", "^NSMIDCP", "india"),
    ("NIFTYMID150", "Nifty Midcap 150", "NIFTYMIDCAP150.NS", "india"),
    ("NIFTYSML250", "Nifty Smallcap 250", "NIFTYSMLCAP250.NS", "india"),
    ("NIFTY500", "Nifty 500", "^CRSLDX", "india"),
    ("INDIAVIX", "India VIX", "^INDIAVIX", "india"),
    # India sectors
    ("S_IT", "Nifty IT", "^CNXIT", "sector"),
    ("S_AUTO", "Nifty Auto", "^CNXAUTO", "sector"),
    ("S_PHARMA", "Nifty Pharma", "^CNXPHARMA", "sector"),
    ("S_FMCG", "Nifty FMCG", "^CNXFMCG", "sector"),
    ("S_METAL", "Nifty Metal", "^CNXMETAL", "sector"),
    ("S_ENERGY", "Nifty Energy", "^CNXENERGY", "sector"),
    ("S_REALTY", "Nifty Realty", "^CNXREALTY", "sector"),
    ("S_MEDIA", "Nifty Media", "^CNXMEDIA", "sector"),
    ("S_INFRA", "Nifty Infra", "^CNXINFRA", "sector"),
    ("S_FIN", "Nifty Financials", "^CNXFIN", "sector"),
    ("S_PSUBANK", "Nifty PSU Bank", "^CNXPSUBANK", "sector"),
    # global equity
    ("SPX", "S&P 500", "^GSPC", "global"),
    ("NDX", "Nasdaq", "^IXIC", "global"),
    ("DJI", "Dow Jones", "^DJI", "global"),
    ("FTSE", "FTSE 100", "^FTSE", "global"),
    ("DAX", "DAX", "^GDAXI", "global"),
    ("CAC", "CAC 40", "^FCHI", "global"),
    ("NIKKEI", "Nikkei 225", "^N225", "global"),
    ("HSI", "Hang Seng", "^HSI", "global"),
    ("SHCOMP", "Shanghai Comp", "000001.SS", "global"),
    ("KOSPI", "KOSPI", "^KS11", "global"),
    ("VIX", "VIX", "^VIX", "global"),
    # FX
    ("USDINR", "USD/INR", "USDINR=X", "fx"),
    ("EURINR", "EUR/INR", "EURINR=X", "fx"),
    ("GBPINR", "GBP/INR", "GBPINR=X", "fx"),
    ("JPYINR", "JPY/INR", "JPYINR=X", "fx"),
    ("DXY", "US Dollar Index", "DX-Y.NYB", "fx"),
    # commodities
    ("GOLD", "Gold (USD/oz)", "GC=F", "commodity"),
    ("SILVER", "Silver (USD/oz)", "SI=F", "commodity"),
    ("BRENT", "Brent (USD/bbl)", "BZ=F", "commodity"),
    ("WTI", "WTI (USD/bbl)", "CL=F", "commodity"),
    ("COPPER", "Copper (USD/lb)", "HG=F", "commodity"),
]
YAHOO_START = "2018-01-01"

# --------------------------------------------------------------------------- FRED (fredgraph.csv, no key)
# id -> dict(label, unit, freq, chain=[(fred_id, transform), ...], max_age_days)
# The connector tries each candidate in order and keeps the first one that is fresh.
FRED = {
    "US_CPI": dict(label="US CPI", unit="% YoY", freq="M", chain=[("CPIAUCSL", "yoy12")], max_age=75),
    "US_CORE_CPI": dict(label="US Core CPI", unit="% YoY", freq="M", chain=[("CPILFESL", "yoy12")], max_age=75),
    "US_UNEMP": dict(label="US Unemployment", unit="%", freq="M", chain=[("UNRATE", "level")], max_age=75),
    "US_10Y": dict(label="US 10Y Treasury", unit="%", freq="D", chain=[("DGS10", "level")], max_age=10),
    "US_2Y": dict(label="US 2Y Treasury", unit="%", freq="D", chain=[("DGS2", "level")], max_age=10),
    "US_CURVE": dict(label="US 10Y-2Y spread", unit="pp", freq="D", chain=[("T10Y2Y", "level")], max_age=10),
    "FED_FUNDS": dict(label="Fed Funds (effective)", unit="%", freq="D", chain=[("DFF", "level")], max_age=10),
    "IN_10Y": dict(label="India 10Y G-sec", unit="%", freq="M", chain=[("INDIRLTLT01STM", "level")], max_age=150),
    "IN_CPI": dict(label="India CPI", unit="% YoY", freq="M",
                   chain=[("CPALTT01INM659N", "level"), ("INDCPIALLMINMEI", "yoy12")], max_age=150),
    "IN_GDP": dict(label="India Real GDP", unit="% YoY", freq="Q", chain=[("NGDPRSAXDCINQ", "yoy4")], max_age=300),
    "CN_CPI": dict(label="China CPI", unit="% YoY", freq="M",
                   chain=[("CPALTT01CNM659N", "level"), ("CHNCPIALLMINMEI", "yoy12")], max_age=150),
}

# --------------------------------------------------------------------------- World Bank (annual, cross-country)
WB_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": ("Real GDP growth", "% YoY"),
    "FP.CPI.TOTL.ZG": ("CPI inflation", "% YoY"),
    "BX.KLT.DINV.WD.GD.ZS": ("FDI net inflows", "% of GDP"),
    "BN.CAB.XOKA.GD.ZS": ("Current account balance", "% of GDP"),
    "SL.UEM.TOTL.ZS": ("Unemployment", "% of labour force"),
    "GC.DOD.TOTL.GD.ZS": ("Central govt debt", "% of GDP"),
}
WB_COUNTRIES = {
    "IND": "India", "USA": "United States", "CHN": "China", "JPN": "Japan", "GBR": "United Kingdom",
    "DEU": "Germany", "BRA": "Brazil", "KOR": "Korea", "IDN": "Indonesia", "MEX": "Mexico", "TUR": "Turkey",
}
WB_START = 2000

# --------------------------------------------------------------------------- NSE Indices (P/E history)
PE_GROUPS = {
    "Market Cap": [("Nifty 50", "NIFTY 50"), ("Nifty Next 50", "NIFTY NEXT 50"),
                   ("Nifty Midcap 150", "NIFTY MIDCAP 150"), ("Nifty Smallcap 250", "NIFTY SMALLCAP 250")],
    "Themes": [("Nifty 500", "NIFTY 500"), ("Nifty 100 Low Vol 30", "NIFTY100 LOW VOLATILITY 30"),
               ("Nifty 100 Quality 30", "NIFTY100 QUALITY 30"), ("Nifty 200 Momentum 30", "NIFTY200 MOMENTUM 30")],
    "Sectors": [("Nifty Auto", "NIFTY AUTO"), ("Nifty Bank", "NIFTY BANK"),
                ("Nifty Consumer Durables", "NIFTY CONSUMER DURABLES"), ("Nifty Defence", "NIFTY INDIA DEFENCE"),
                ("Nifty Energy", "NIFTY ENERGY"), ("Nifty FMCG", "NIFTY FMCG"),
                ("Nifty Healthcare", "NIFTY HEALTHCARE INDEX"), ("Nifty IT", "NIFTY IT"),
                ("Nifty Infra", "NIFTY INFRASTRUCTURE"), ("Nifty Manufacturing", "NIFTY INDIA MANUFACTURING"),
                ("Nifty Metals", "NIFTY METAL"), ("Nifty MNC", "NIFTY MNC"),
                ("Nifty Oil and Gas", "NIFTY OIL & GAS"), ("Nifty Pharma", "NIFTY PHARMA"),
                ("Nifty PSU Banks", "NIFTY PSU BANK"), ("Nifty Realty", "NIFTY REALTY")],
}
PE_START = "2020-01-01"


def yahoo_label(sid: str) -> str:
    return next((l for i, l, *_ in YAHOO if i == sid), sid)
