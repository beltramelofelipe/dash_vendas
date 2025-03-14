import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import random
import datetime
from dash import html, dcc, Input, Output

# Inicializar a aplicação Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"])

# Gerar dados fictícios para o gráfico de vendas
num_dias = 30  # Últimos 30 dias
hoje = datetime.date.today()
datas = [hoje - datetime.timedelta(days=i) for i in range(num_dias)]
vendas = [random.randint(10000, 50000) for _ in range(num_dias)]

# Criar DataFrame com as datas e vendas
df_vendas = pd.DataFrame({"Data": datas, "Vendas": vendas})
df_vendas = df_vendas.sort_values(by="Data")  # Ordenar por data

# Função para criar um Card KPI bem alinhado
def create_kpi_card(title, value1, value2, label1, label2, icon):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(className=f"fa {icon} fa-2x", style={"color": "#32CD32"}),  # Verde claro
                        html.H5(title, className="card-title", style={"margin": "0", "font-size": "16px"}),
                    ],
                    style={"display": "flex", "align-items": "center", "gap": "8px", "justify-content": "center"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(value1, style={"color": "#D90718", "font-size": "20px", "margin": "0"}),  # Verde claro
                                html.P(label1, className="card-text", style={"font-size": "12px", "color": "gray", "margin": "0"}),
                            ],
                            style={"text-align": "center"},
                        ),
                        html.Div(
                            [
                                html.H2(value2, style={"color": "#0D0D0D", "font-size": "18px", "margin": "0"}),  # Verde claro
                                html.P(label2, className="card-text", style={"font-size": "12px", "color": "gray", "margin": "0"}),
                            ],
                            style={"text-align": "center"},
                        ),
                    ],
                    style={"display": "flex", "justify-content": "space-between", "margin-top": "10px"},
                ),
            ]
        ),
        style={
            "width": "100%",
            "textAlign": "center",
            "boxShadow": "2px 2px 10px rgba(0,0,0,0.1)",
            "height": "120px",
            "padding": "10px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center"
        },
    )

# Layout do aplicativo
app.layout = dbc.Container(
    [
        html.H1("Vendas SN", style={"textAlign": "center"}),
        html.Hr(),

        # Linha de KPIs
        dbc.Row(
            [
                dbc.Col(create_kpi_card("Faturamento", "R$ 1.250.000", "12.5%", "Total", "Crescimento", "fa-dollar-sign"), width=2),
                dbc.Col(create_kpi_card("Qtd Vendas", "7.200", "R$ 350", "Total", "Ticket Médio", "fa-shopping-cart"), width=2),
                dbc.Col(create_kpi_card("Produtos Vendidos", "15.000", "10%", "Total", "Aumento", "fa-box"), width=2),
                dbc.Col(create_kpi_card("Clientes Novos", "1.500", "7 dias", "Total", "Média de Retenção", "fa-user-plus"), width=2),
                dbc.Col(create_kpi_card("Reembolso", "R$ 150.000", "8.2%", "Valor Total", "Porcentagem", "fa-hand-holding-usd"), width=2),
            ],
            className="mb-4 justify-content-center",
        ),

        # Seletor de intervalo de datas
        dbc.Row(
            dbc.Col(
                dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed=min(datas),
                    max_date_allowed=max(datas),
                    start_date=min(datas),
                    end_date=max(datas),
                    display_format="DD/MM/YYYY",
                    style={"margin-bottom": "20px"}
                ),
                width={"size": 6, "offset": 3},
            ),
            className="mb-4",
        ),

        # Gráfico de vendas (de colunas)
        dbc.Row(
            dbc.Col(dcc.Graph(id="bar-chart"), width=12),
        ),
    ],
    className="mt-4",
)

# Callback para atualizar o gráfico com base no intervalo de datas selecionado
@app.callback(
    Output("bar-chart", "figure"),
    [Input("date-picker", "start_date"), Input("date-picker", "end_date")]
)
def update_chart(start_date, end_date):
    # Converter start_date e end_date para datetime.date
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    # Filtrar os dados com base no intervalo de datas selecionado
    df_filtered = df_vendas[(df_vendas["Data"] >= start_date) & (df_vendas["Data"] <= end_date)]

    # Criar gráfico de colunas com cor verde claro
    fig = px.bar(df_filtered, x="Data", y="Vendas", title="Total de Vendas por Dia", text_auto=True, color_discrete_sequence=["#32CD32"])
    fig.update_layout(template="plotly_white", height=400)

    return fig

# Rodar o aplicativo
if __name__ == "__main__":
    app.run_server(debug=False, port=8080, host="0.0.0.0")