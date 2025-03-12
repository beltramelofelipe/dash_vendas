import dash
import plotly.express as px
from dash import html, dcc
import pandas as pd

app = dash.Dash(__name__)

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Banas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF",'SF',"SF","Montreal","Montreal","Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City")

app.layout = html.Div(
    children=[
        html.H1("Hello Dash", id="h1"),
        
        html.Div("Dash: Um framework web para Python"),

        dcc.Graph(figure=fig, id="graph")
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)