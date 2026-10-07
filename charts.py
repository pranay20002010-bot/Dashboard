"""Plotly figure builders.  Every builder takes pandas Series (date-indexed) and returns a Figure."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import theme as T


def window(s: pd.Series, years: float | None) -> pd.Series:
    if s.empty or not years:
        return s
    return s[s.index >= s.index.max() - pd.DateOffset(days=int(365.25 * years))]


def fmt_val(v: float, unit: str = "") -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "-"
    a = abs(v)
    if "crore" in unit.lower() or a >= 10000:
        return f"{v:,.0f}"
    if a >= 1000:
        return f"{v:,.1f}"
    if a >= 100:
        return f"{v:,.2f}"
    return f"{v:,.2f}"


def _tag(fig, y, text, color, yref="y"):
    fig.add_annotation(x=1, xref="paper", y=y, yref=yref, text=f"<b>{text}</b>", showarrow=False,
                       xanchor="left", xshift=4, bgcolor=color, font=dict(color=T.BG, size=10, family=T.MONO),
                       borderpad=2)


def empty(msg="NO DATA - run  python -m vika_macro.update", height=260) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(**T.base_layout(height, legend=False, rangeselector=False))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
                       font=dict(color=T.MUTED, size=12, family=T.MONO))
    return fig


def line(series: dict[str, pd.Series], unit="", height=300, years=3, secondary: tuple[str, ...] = (),
         rebase=False, colors=None, hlines=(), fill_first=False, dec=2, step=False) -> go.Figure:
    series = {k: window(v.dropna(), years) for k, v in series.items() if v is not None and not v.dropna().empty}
    if not series:
        return empty(height=height)
    fig = go.Figure()
    colors = colors or {}
    sec = bool(secondary)
    for i, (name, s) in enumerate(series.items()):
        if rebase:
            s = s / s.iloc[0] * 100
        c = colors.get(name, T.SERIES[i % len(T.SERIES)])
        on2 = name in secondary
        filled = fill_first and i == 0
        if filled:  # invisible baseline just under the data, so the fill never drags the axis down to 0
            lo, hi = float(s.min()), float(s.max())
            base = lo - (hi - lo) * 0.06
            fig.add_trace(go.Scatter(x=s.index, y=[base] * len(s), mode="lines", line=dict(width=0),
                                     hoverinfo="skip", showlegend=False, yaxis="y2" if on2 else "y"))
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values, name=name, mode="lines", yaxis="y2" if on2 else "y",
            line=dict(color=c, width=1.7 if i else 2.0, shape="hv" if step else "linear"),
            fill="tonexty" if filled else None,
            fillcolor="rgba(139,92,246,0.13)" if filled else None,
            hovertemplate=f"%{{y:,.{dec}f}}<extra>{name}</extra>"))
        _tag(fig, s.iloc[-1], f"{s.iloc[-1]:,.{dec}f}", c, "y2" if on2 else "y")
    for y, label, col in hlines:
        fig.add_hline(y=y, line=dict(color=col, width=1, dash="dot"), annotation_text=label,
                      annotation_font=dict(color=col, size=9), annotation_position="left")
    lay = T.base_layout(height, legend=len(series) > 1)
    if sec:
        lay["yaxis2"] = dict(overlaying="y", side="left", showgrid=False, zeroline=False, tickfont=dict(size=10),
                             linecolor="rgba(0,0,0,0)")
        lay["margin"]["l"] = 56
    fig.update_layout(**lay)
    if rebase:
        fig.add_hline(y=100, line=dict(color=T.BORDER, width=1))
    return fig


def bars(series: dict[str, pd.Series], unit="", height=300, years=1.1, mode="group", posneg=False, labels=True,
         dec=0, colors=None, freq="M", max_labels=16, line_overlay: pd.Series | None = None, overlay_name="") -> go.Figure:
    series = {k: window(v.dropna(), years) for k, v in series.items() if v is not None and not v.dropna().empty}
    if not series:
        return empty(height=height)
    fig = go.Figure()
    colors = colors or {}
    n_points = max(len(s) for s in series.values())
    for i, (name, s) in enumerate(series.items()):
        if posneg and len(series) == 1:
            col = [T.UP if v >= 0 else T.DOWN for v in s.values]
        else:
            col = colors.get(name, T.SERIES[(i + 1) % len(T.SERIES)] if len(series) > 1 else T.PURPLE)
        fig.add_trace(go.Bar(
            x=s.index, y=s.values, name=name, marker=dict(color=col, line=dict(width=0)),
            text=[f"{v:,.{dec}f}" for v in s.values] if labels and n_points <= max_labels else None,
            textposition="outside", textfont=dict(size=9, color=T.TEXT, family=T.MONO), cliponaxis=False,
            hovertemplate=f"%{{y:,.{dec}f}}<extra>{name}</extra>"))
    if line_overlay is not None and not line_overlay.empty:
        lo = window(line_overlay, years)
        fig.add_trace(go.Scatter(x=lo.index, y=lo.values, name=overlay_name, mode="lines+markers", yaxis="y2",
                                 line=dict(color=T.GOLD, width=2), marker=dict(size=5, color=T.GOLD)))
    lay = T.base_layout(height, legend=len(series) > 1 or line_overlay is not None, rangeselector=n_points > 18)
    lay["barmode"] = mode
    if freq in ("M", "Q"):
        lay["xaxis"]["tickformat"] = "%b-%y"
        lay["xaxis"]["dtick"] = ("M1" if n_points <= 14 else "M2" if n_points <= 26 else "M6") if freq == "M" else "M6"
    lay["margin"]["r"] = 20
    lay["yaxis"]["side"] = "left"
    lay["yaxis"]["zeroline"] = True
    lay["yaxis"]["zerolinecolor"] = T.BORDER
    lay["xaxis"]["showspikes"] = False
    if line_overlay is not None:
        lay["yaxis2"] = dict(overlaying="y", side="right", showgrid=False, zeroline=False)
        lay["margin"]["r"] = 48
    fig.update_layout(**lay)
    return fig


def pe_panel(s: pd.Series, years=3, height=235) -> go.Figure:
    """Deck-style P/E: line + max / min / average reference lines and latest tag."""
    s = window(s.dropna(), years)
    if s.empty:
        return empty(height=height)
    mx, mn, av, last = s.max(), s.min(), s.mean(), s.iloc[-1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", name="P/E", line=dict(color=T.PURPLE, width=1.6),
                             hovertemplate="%{y:.1f}x<extra>P/E</extra>"))
    for y, lab, col, dash in ((mx, f"Max {mx:.1f}", T.TEXT, "solid"), (av, f"Avg {av:.1f}", T.GOLD, "dash"),
                              (mn, f"Min {mn:.1f}", T.MUTED, "solid")):
        fig.add_hline(y=y, line=dict(color=col, width=1, dash=dash), opacity=0.8)
        fig.add_annotation(x=0, xref="paper", y=y, text=lab, showarrow=False, xanchor="left", yanchor="bottom",
                           font=dict(color=col, size=9, family=T.MONO))
    pct = (s <= last).mean() * 100
    _tag(fig, last, f"{last:.1f}", T.GOLD)
    lay = T.base_layout(height, legend=False, rangeselector=False,
                        margin=dict(l=8, r=54, t=8, b=24))
    lay["hovermode"] = "x"
    lay["xaxis"]["tickformat"] = "%b-%y"
    lay["xaxis"]["nticks"] = 5
    lay["yaxis"]["range"] = [mn - (mx - mn) * 0.12, mx + (mx - mn) * 0.12]
    fig.update_layout(**lay)
    fig.add_annotation(x=1, xref="paper", y=1, yref="paper", text=f"{pct:.0f}th pct", showarrow=False,
                       xanchor="right", yanchor="top", font=dict(color=T.MUTED, size=9, family=T.MONO))
    return fig


def rank_heatmap(rets: pd.DataFrame, height=420) -> go.Figure:
    height = max(height, 44 * len(rets.index) + 50) if len(rets.index) else height
    """Deck-style monthly performance grid: columns = months, cells sorted best->worst."""
    if rets.empty:
        return empty(height=height)
    cols = list(rets.columns)
    n = len(rets.index)
    z, txt = [], []
    for r in range(n):
        zr, tr = [], []
        for c in cols:
            col = rets[c].dropna().sort_values(ascending=False)
            if r < len(col):
                zr.append(col.iloc[r])
                tr.append(f"{col.index[r]}<br><b>{col.iloc[r]:+.2f}%</b>")
            else:
                zr.append(None)
                tr.append("")
        z.append(zr)
        txt.append(tr)
    lim = max(5.0, float(np.nanpercentile(np.abs(np.array(z, dtype=float)), 95)))
    fig = go.Figure(go.Heatmap(
        z=z, x=[c.strftime("%b-%y") if hasattr(c, "strftime") else c for c in cols], y=list(range(1, n + 1)),
        text=txt, texttemplate="%{text}", textfont=dict(size=10, family=T.MONO, color=T.TEXT),
        colorscale=T.DIVERGING, zmin=-lim, zmax=lim, showscale=False, xgap=3, ygap=3,
        hovertemplate="%{text}<extra></extra>"))
    lay = T.base_layout(height, legend=False, rangeselector=False, margin=dict(l=24, r=8, t=8, b=8))
    lay["hovermode"] = "closest"
    fig.update_layout(**lay)
    fig.update_xaxes(side="top", showgrid=False, showspikes=False, tickfont=dict(color=T.GOLD, size=11))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(size=9), side="left")
    return fig


def spark(s: pd.Series, up_good=True) -> go.Figure:
    s = s.dropna().tail(60)
    fig = go.Figure()
    if len(s):
        col = T.UP if (s.iloc[-1] >= s.iloc[0]) == up_good else T.DOWN
        fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", line=dict(color=col, width=1.4),
                                 fill="tozeroy", fillcolor="rgba(139,92,246,0.08)", hoverinfo="skip"))
        fig.update_yaxes(range=[s.min() - (s.max() - s.min()) * 0.1, s.max() + (s.max() - s.min()) * 0.1])
    fig.update_layout(height=34, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def spread(s: pd.Series, years=3, height=280, name="10Y-2Y spread (pp)") -> go.Figure:
    s = window(s.dropna(), years)
    if s.empty:
        return empty(height=height)
    pos, neg = s.clip(lower=0), s.clip(upper=0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=pos, mode="lines", line=dict(color=T.UP, width=0), fill="tozeroy",
                             fillcolor="rgba(45,212,160,0.35)", hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=s.index, y=neg, mode="lines", line=dict(color=T.DOWN, width=0), fill="tozeroy",
                             fillcolor="rgba(244,63,94,0.40)", hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", name=name, line=dict(color=T.TEXT, width=1.3),
                             hovertemplate="%{y:.2f}<extra>" + name + "</extra>"))
    _tag(fig, s.iloc[-1], f"{s.iloc[-1]:.2f}", T.GOLD)
    fig.update_layout(**T.base_layout(height, legend=False))
    return fig


def wb_bars(df: pd.DataFrame, unit: str, height=300, years_back=12) -> go.Figure:
    """df: index=year (int), columns=country names."""
    if df.empty:
        return empty(height=height)
    df = df.tail(years_back)
    fig = go.Figure()
    for i, c in enumerate(df.columns):
        fig.add_trace(go.Bar(x=df.index, y=df[c], name=c, marker=dict(color=T.SERIES[i % len(T.SERIES)]),
                             hovertemplate="%{y:.1f}<extra>" + c + "</extra>"))
    lay = T.base_layout(height, legend=True, rangeselector=False)
    lay["barmode"] = "group"
    lay["hovermode"] = "x unified"
    lay["xaxis"]["dtick"] = 1
    lay["xaxis"]["showspikes"] = False
    lay["yaxis"].update(side="left", zeroline=True, zerolinecolor=T.BORDER)
    lay["margin"]["r"] = 16
    fig.update_layout(**lay)
    return fig


def rolling_table_returns(prices: dict[str, pd.Series]) -> pd.DataFrame:
    """1D, 1W, 1M, 3M, 6M, 1Y, YTD returns (%) per series."""
    rows = []
    for name, s in prices.items():
        s = s.dropna()
        if len(s) < 3:
            continue
        last, d = s.iloc[-1], s.index[-1]

        def ret(days=None, ytd=False):
            ref = s[s.index <= (pd.Timestamp(d.year - 1, 12, 31) if ytd else d - pd.Timedelta(days=days))]
            return (last / ref.iloc[-1] - 1) * 100 if len(ref) else np.nan
        rows.append({"Index": name, "Last": last, "1D": (last / s.iloc[-2] - 1) * 100, "1W": ret(7), "1M": ret(30),
                     "3M": ret(91), "6M": ret(182), "1Y": ret(365), "YTD": ret(ytd=True), "As of": d.strftime("%d-%b-%y")})
    return pd.DataFrame(rows)
