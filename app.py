import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import datetime
from dash import html, dcc
from google.cloud import bigquery
import os

# Configurar credenciais do BigQuery
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = (r'bi-sndb.json')

# Inicializar a aplicação Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Conectar ao BigQuery e obter os dados
project_id = 'bi-sndb'
client = bigquery.Client(project=project_id)

query = """
    SELECT * FROM `bi-sndb.bi_sn.dash_transacoes_mensais`
"""
query_job = client.query(query)
results = query_job.result()
data = [dict(row) for row in results]
df_vendas_total = pd.DataFrame(data)

hoje = datetime.datetime.today()
ano_mes_atual = hoje.strftime("%Y-%m")

df_vendas_total = df_vendas_total.sort_values(by="ano_mes")

# Obter dados do mês anterior
mes_anterior = (hoje - datetime.timedelta(days=30)).strftime("%Y-%m")
df_mes_anterior = df_vendas_total[df_vendas_total["ano_mes"] == mes_anterior]

# Se o mês anterior não tiver dados, usar 1 para evitar divisão por zero
faturamento_anterior = df_mes_anterior["aprovadas"].sum() if not df_mes_anterior.empty else 1
produtos_anterior = df_mes_anterior["qtd_produto"].sum() if not df_mes_anterior.empty else 1
clientes_anterior = df_mes_anterior["novos_clientes"].sum() if not df_mes_anterior.empty else 1




df_vendas = df_vendas_total[df_vendas_total["ano_mes"] == ano_mes_atual]
# Se o DataFrame estiver vazio, preencher com valores padrão
if df_vendas.empty:
    df_vendas = pd.DataFrame({
        "ano_mes": [ano_mes_atual],
        "aprovadas": [0],
        "qtd_transacoes": [1],
        "qtd_produto": [0],
        "novos_clientes": [0],
        "reembolso": [0]
    })

# Calcular métricas derivadas
total_faturamento = round(df_vendas["aprovadas"].sum(), -1)
total_vendas = df_vendas["qtd_transacoes"].sum()
total_produtos = df_vendas["qtd_produto"].sum()
total_clientes_novos = df_vendas["novos_clientes"].sum()
total_reembolsos = round(df_vendas["reembolso"].sum(), -1)


# Calcular crescimento MoM
crescimento_faturamento = ((total_faturamento - faturamento_anterior) / faturamento_anterior) * 100
crescimento_produtos = ((total_produtos - produtos_anterior) / produtos_anterior) * 100
crescimento_clientes = ((total_clientes_novos - clientes_anterior) / clientes_anterior) * 100

# Formatar crescimento
def format_growth(value):
    if value > 0:
        return f"📈 +{value:.1f}%"
    elif value < 0:
        return f"📉 {value:.1f}%"
    else:
        return f"➖ {value:.1f}%"
    
growth_faturamento = format_growth(crescimento_faturamento)
growth_produtos = format_growth(crescimento_produtos)
growth_clientes = format_growth(crescimento_clientes)

# Calcular Ticket Médio e Taxa de Reembolso
ticket_medio = total_faturamento / total_vendas if total_vendas > 0 else 0
taxa_reembolso = (total_reembolsos / total_faturamento) * 100 if total_faturamento > 0 else 0

# Formatar valores para exibição
def format_currency(value):
    return f"R$ {value:,.0f}".replace(",", ".")

def format_percent(value):
    return f"{value:.2f}%"


# Criar Card KPI
def create_kpi_card(title, value1, value2, label1, label2, icon):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(className=f"fa {icon} fa-2x", style={"color": "#D90718"}),
                        html.H5(title, className="card-title", style={"margin": "0", "font-size": "16px"}),
                    ],
                    style={"display": "flex", "align-items": "center", "gap": "8px", "justify-content": "center"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(value1, style={"color": "#D90718", "font-size": "20px", "margin": "0"}),
                                html.P(label1, className="card-text", style={"font-size": "12px", "color": "#0D0D0D", "margin": "0"}),
                            ],
                            style={"text-align": "center"},
                        ),
                        html.Div(
                            [
                                html.H2(value2, style={"color": "#0D0D0D", "font-size": "18px", "margin": "0"}),
                                html.P(label2, className="card-text", style={"font-size": "12px", "color": "#0D0D0D", "margin": "0"}),
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
            "justifyContent": "center",
            "backgroundColor": "#F2F2F2"
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
                dbc.Col(create_kpi_card("Faturamento", 
                                        format_currency(total_faturamento),
                                        growth_faturamento, 
                                        "Total", 
                                        "Crescimento MoM",
                                        "fa-dollar-sign"),
                                        width=2),
                dbc.Col(create_kpi_card("Qtd Vendas", 
                                        f"{total_vendas:,}".replace(",", "."), 
                                        format_currency(ticket_medio), 
                                        "Total",
                                         "Ticket Médio", 
                                         "fa-shopping-cart"), 
                                         width=2),
                dbc.Col(create_kpi_card("Produtos Vendidos",
                                        f"{total_produtos:,}".replace(",", "."), 
                                        growth_produtos, 
                                        "Total",
                                        "Crescimento MoM", 
                                        "fa-box"), width=2),
                dbc.Col(create_kpi_card("Clientes Novos",
                                         f"{total_clientes_novos:,}".replace(",", "."),
                                           growth_clientes, 
                                           "Total",
                                            "Crescimento MoM", 
                                            "fa-user-plus"), width=2),
                dbc.Col(create_kpi_card("Reembolso", 
                                        format_currency(total_reembolsos),
                                          format_percent(taxa_reembolso), 
                                          "Valor Total", 
                                          "Porcentagem", 
                                          "fa-hand-holding-usd"), width=2),
            ],
            className="mb-4 justify-content-center",
        ),

        # Gráfico de vendas
        dbc.Row(
            dbc.Col(dcc.Graph(id="bar-chart"), width=12),
        ),
    ],
    className="mt-4",
    style={"backgroundColor": "#FFFFFF"}
)

# Criar gráfico de colunas
fig = px.bar(
    df_vendas_total,
    x="ano_mes",
    y="aprovadas",
    title="Total de Vendas por Mês-Ano",
    text=df_vendas_total["aprovadas"].apply(lambda x: f"{x/1_000_000:.1f}MM" if x >= 1_000_000 else f"{x/1_000:.0f}K"),
    color_discrete_sequence=["#D90718"]
)

# Ajustar layout para rótulos na horizontal e bem posicionados
fig.update_traces(textposition='outside')  
max_value = df_vendas_total["aprovadas"].max()
y_axis_limit = max_value * 1.1  # Adiciona 10% para evitar sobreposição

fig.update_layout(
    yaxis=dict(
        title="aprovadas",
        range=[0, y_axis_limit],  # Ajusta o eixo Y para evitar sobreposição
        tickformat=".1s"  # Mantém a formatação em K e MM
    )
)
fig.update_layout(
    plot_bgcolor="white",  # Fundo branco no gráfico
    paper_bgcolor="white",  # Fundo branco no espaço ao redor
    yaxis=dict(showgrid=False),  # Remove linhas de grade se necessário
)
@app.callback(
    dash.Output("bar-chart", "figure"),
    [dash.Input("bar-chart", "id")]
)
def update_chart(_):
    return fig

# Rodar o aplicativo
if __name__ == "__main__":
    app.run_server(debug=False, port=8080, host="0.0.0.0")
