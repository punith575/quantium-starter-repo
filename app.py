from dash import Dash, html
import pandas as pd

app = Dash(__name__)

app.layout = html.Div("Hello Quantium Dash App")

if __name__ == "__main__":
    app.run(debug=True)
