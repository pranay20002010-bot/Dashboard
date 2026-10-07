"""Design tokens: Bloomberg-style dark terminal tinted with Vika Wealth purple + gold."""

BG = "#0A0712"
PANEL = "#110C1F"
PANEL_HDR = "#1B1040"
BORDER = "#2B2150"
GRID = "#1E1738"
TEXT = "#E9E5F7"
MUTED = "#8F86B0"
GOLD = "#F2B825"       # Vika gold (deck titles)
PURPLE = "#8B5CF6"     # brightened Vika purple for dark bg
DEEP = "#3B1A8C"       # deck header purple
UP = "#2DD4A0"
DOWN = "#F43F5E"
CYAN = "#38BDF8"
PINK = "#F472B6"
ORANGE = "#FB923C"

SERIES = [GOLD, PURPLE, CYAN, PINK, UP, ORANGE, "#A3E635", "#E879F9"]
MONO = "IBM Plex Mono, SFMono-Regular, Menlo, monospace"
SANS = "IBM Plex Sans, Inter, system-ui, sans-serif"

# diverging scale for heatmaps / returns:  red -> near-black purple -> green
DIVERGING = [[0, "#B4233F"], [0.35, "#5A1A33"], [0.5, "#1B1433"], [0.65, "#124A44"], [1, "#1FBF8F"]]

RANGE_BUTTONS = [
    dict(count=1, label="1M", step="month", stepmode="backward"),
    dict(count=3, label="3M", step="month", stepmode="backward"),
    dict(count=6, label="6M", step="month", stepmode="backward"),
    dict(count=1, label="1Y", step="year", stepmode="backward"),
    dict(count=3, label="3Y", step="year", stepmode="backward"),
    dict(step="all", label="ALL"),
]


def base_layout(height=300, legend=True, margin=None, rangeselector=True) -> dict:
    lay = dict(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=MONO, size=10.5, color=MUTED),
        margin=margin or dict(l=48, r=62, t=26, b=30),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=PANEL_HDR, bordercolor=BORDER, font=dict(family=MONO, size=11, color=TEXT)),
        legend=dict(orientation="h", x=1, y=1.0, yanchor="bottom", xanchor="right", font=dict(size=10, color=TEXT),
                    bgcolor="rgba(0,0,0,0)", itemsizing="constant"),
        showlegend=legend,
        xaxis=dict(gridcolor=GRID, linecolor=BORDER, zeroline=False, showspikes=True, spikecolor=MUTED,
                   spikethickness=1, spikedash="dot", spikemode="across", tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID, linecolor="rgba(0,0,0,0)", zeroline=False, side="right",
                   tickfont=dict(size=10), automargin=True),
        bargap=0.28, bargroupgap=0.06,
    )
    if rangeselector:
        lay["xaxis"]["rangeselector"] = dict(buttons=RANGE_BUTTONS, x=0, y=1.0, yanchor="bottom",
                                             bgcolor="rgba(0,0,0,0)", activecolor=DEEP, bordercolor=BORDER,
                                             borderwidth=1, font=dict(size=9, color=TEXT))
    return lay
