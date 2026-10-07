# Vika Macro Terminal

A Bloomberg-style macro & markets dashboard (Streamlit + Plotly) for Vika Wealth research. Dark terminal look with Vika
purple/gold branding. Fully automated from free, keyless public sources: a scheduled GitHub Action refreshes the data
files in `data/`, and the app just reads them. No manual uploads.

Pages: **INDIA** · **VALUATIONS** (deck-style P/E bands for 24 Nifty indices) · **FLOWS** (FII/DII) · **GLOBAL**
(indices, FX, gold, oil, US rates, curve, inflation, country comparison) · **SECTORS** (ranked monthly heatmap) · **STATUS**.

## Try it on your Mac

```bash
cd vika-macro-terminal
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m vika_macro.update      # first data fetch, ~3-6 min (NSE P/E history is the slow part)
streamlit run streamlit_app.py   # opens http://localhost:8501
```

Open the **STATUS** page after the update: it shows what worked and exactly what failed.

## Put it online so anyone can open it

1. **GitHub**: create a repo and push this folder. In the repo go to Settings → Actions → General → Workflow
   permissions → *Read and write*. Then Actions → "Update data" → *Run workflow*. This fills `data/` and, from then on,
   refreshes it automatically on weekdays at 07:00 and 19:00 IST.
2. **Streamlit Community Cloud** (free): go to share.streamlit.io, sign in with GitHub, *Create app*, pick the repo,
   branch `main`, main file `streamlit_app.py`, *Deploy*. You get a link anyone can open. Each data commit from the
   Action updates the app automatically.
   (Private repos work too, but the Streamlit link is then restricted to people you invite unless you make the app public.)

## Data sources (all free, no API keys)

| Feed | Connector | Covers | Frequency |
|---|---|---|---|
| Yahoo Finance | `connectors/yahoo.py` | Nifty indices & sectors, India VIX, global indices, USD/EUR/GBP/JPY-INR, DXY, gold, silver, Brent, WTI, copper, VIX | daily |
| FRED (`fredgraph.csv`) | `connectors/fred.py` | US CPI/core CPI, unemployment, 10Y/2Y, curve, Fed funds; India 10Y, CPI, real GDP; China CPI | daily/monthly/quarterly |
| World Bank API | `connectors/worldbank.py` | GDP growth, inflation, FDI, current account, debt, unemployment for 11 countries | annual |
| NSE Indices | `connectors/nse.py` | Trailing P/E, P/B, dividend yield history | daily |
| NSE | `connectors/nse.py` | FII/DII net flows (history builds from the first run) | daily |

Every connector implements `fetch() → clean() → validate() → save()`, never raises, and records its result in
`data/status.json`. One failing source never blanks the dashboard: charts keep the last good data, and a panel footer turns
amber with `STALE (n days)` when data is old.

## Honest caveats

- The NSE endpoints and some Yahoo/FRED identifiers could **not be live-tested while building** (the build sandbox had no
  internet), and the pages were verified by automated rendering tests rather than by eye. The first real run shows what works.
  Likely first fixes: a few Nifty index tickers on Yahoo, the OECD-sourced FRED series for India/China CPI (may be stale),
  and the NSE endpoints if NSE blocks GitHub's servers.
- FII/DII: NSE exposes only the latest session, so history starts when the Action first runs.
- Not yet automated (no free stable API): India PMI, GST, trade balance, auto sales (FADA), MF/SIP flows (AMFI), WPI,
  market-cap/GDP. They are listed on the STATUS page. Adding one means dropping a connector class into
  `vika_macro/connectors/` and registering it in `connectors/__init__.py`.

## Layout

```
streamlit_app.py        app shell: header, ticker strip, navigation, controls
vika_macro/config.py    tickers, FRED ids, World Bank indicators, NSE index list   <- edit to add series
vika_macro/connectors/  one file per source
vika_macro/charts.py    Plotly figure builders (institutional styling)
vika_macro/st_pages.py  page layouts
vika_macro/ui.py        panels, KPI tiles, ticker, tables
vika_macro/theme.py     colours / fonts / Plotly template
assets/terminal.css     terminal styling   ·   .streamlit/config.toml  dark theme
data/                   refreshed CSVs + status.json (committed by the Action)
tests/                  offline tests (synthetic data exists only in tests/make_demo_data.py)
```

`VIKA_DATA_DIR` relocates the data folder; `VIKA_DATA_URL` reads the CSVs from a URL instead.
Free public data, may be delayed. For research use only.
