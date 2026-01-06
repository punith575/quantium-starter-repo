from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# ---------- Load data ----------
REPO_ROOT = Path(__file__).resolve().parent
DATA_FILE = REPO_ROOT / "output_sales.csv"

df = pd.read_csv(DATA_FILE)

# Ensure expected columns exist (Sales, Date, Region)
df.columns = [c.strip() for c in df.columns]

# Parse Date and clean Region
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Region"] = df["Region"].astype(str).str.strip().str.lower()

# Drop rows with bad dates (just in case)
df = df.dropna(subset=["Date"])


# ---------- Dash app ----------
app = Dash(__name__)
app.title = "Pink Morsels Sales Visualizer"

regions = sorted(df["Region"].dropna().unique().tolist())
region_options = [{"label": "All", "value": "ALL"}] + [{"label": r.title(), "value": r} for r in regions]

app.layout = html.Div(
    style={"maxWidth": "1000px", "margin": "40px auto", "fontFamily": "Arial"},
    children=[
        html.H1("Pink Morsels Sales Over Time"),
        html.P("Use the dropdown to filter by region. The chart shows total sales per day."),

        html.Label("Region"),
        dcc.Dropdown(
            id="region",
            options=region_options,
            value="ALL",
            clearable=False,
            style={"width": "300px"},
        ),

        dcc.Graph(id="sales-line"),
    ],
)


@app.callback(
    Output("sales-line", "figure"),
    Input("region", "value"),
)
def update_chart(selected_region: str):
    dff = df.copy()

    if selected_region != "ALL":
        dff = dff[dff["Region"] == selected_region]

    # Total sales per day
    daily = (
        dff.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
    )

    fig = px.line(
        daily,
        x="Date",
        y="Sales",
        markers=True,
        title="Total Sales per Day",
        labels={"Date": "Date", "Sales": "Sales ($)"},
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
