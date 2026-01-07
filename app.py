from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# --- Config ---
DATA_FILE = "output_sales.csv"
CUTOFF_DATE = pd.Timestamp("2021-01-15")  # Price increase date


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)

    # Normalize column names (Sales -> sales, Date -> date, Region -> region, etc.)
    df.columns = [c.strip().lower() for c in df.columns]

    # Basic validation
    required = {"date", "region", "sales"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {DATA_FILE}: {missing}")

    # Clean types
    df["region"] = df["region"].astype(str).str.strip().str.lower()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")

    # Drop bad rows
    df = df.dropna(subset=["date", "sales", "region"]).copy()

    return df


df_all = load_data()

# Fixed order (as required by the task)
REGION_OPTIONS = ["all", "north", "east", "south", "west"]


app = Dash(__name__)
app.title = "Pink Morsel Sales Visualiser"

app.layout = html.Div(
    className="page",
    children=[
        html.H1("Pink Morsel Sales Visualiser", className="title"),
        html.P(
            "Use the radio buttons to filter by region. The chart shows total sales per day.",
            style={"marginBottom": "12px"},
        ),

        html.Div(
            className="controls",
            children=[
                html.Div("Region", className="label"),
                dcc.RadioItems(
                  id="region_radio",
                  options=[{"label": r.capitalize(), "value": r} for r in REGION_OPTIONS],
                  value="all",
                  inline=True,
                  labelStyle={"marginRight": "14px"},
                ),

            ],
        ),

        dcc.Graph(id="sales_line_chart"),

        html.Div(id="summary_text", style={"marginTop": "12px", "fontWeight": "600"}),
    ],
)


@app.callback(
    Output("sales_line_chart", "figure"),
    Output("summary_text", "children"),
    Input("region_radio", "value"),
)
def update_chart(region_value: str):
    # Filter by region
    if region_value and region_value != "all":
        dff = df_all[df_all["region"] == region_value].copy()
        region_label = region_value.capitalize()
    else:
        dff = df_all.copy()
        region_label = "All Regions"

    # Group by date (sum sales), sort by date
    daily = (
        dff.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
        .copy()
    )

    # Make sure x-axis is real datetime (prevents Plotly int+str error)
    daily["date"] = pd.to_datetime(daily["date"])

    # Build figure
    fig = px.line(
        daily,
        x="date",
        y="sales",
        title=f"Total Sales per Day ({region_label})",
        labels={"date": "Date", "sales": "Sales ($)"},
    )
    fig.update_xaxes(type="date")

    # Add cutoff line + annotation (safe way)
    fig.add_vline(x=CUTOFF_DATE, line_width=2, line_dash="dash")
    fig.add_annotation(
        x=CUTOFF_DATE,
        y=1,
        yref="paper",
        text="Price increase (Jan 15, 2021)",
        showarrow=False,
        xanchor="left",
        yanchor="top",
    )

    # Simple summary (before vs after)
    before = daily[daily["date"] < CUTOFF_DATE]["sales"]
    after = daily[daily["date"] >= CUTOFF_DATE]["sales"]

    if len(before) == 0 or len(after) == 0:
        summary = "Not enough data on both sides of Jan 15, 2021 to compare."
    else:
        before_avg = before.mean()
        after_avg = after.mean()
        verdict = "after" if after_avg > before_avg else "before"
        summary = (
            f"Average daily sales {verdict} the price increase. "
            f"Before: {before_avg:,.0f} | After: {after_avg:,.0f}"
        )

    return fig, summary


if __name__ == "__main__":
    app.run(debug=True)
