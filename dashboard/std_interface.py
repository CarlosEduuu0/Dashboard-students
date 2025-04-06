from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from app import * 
from dash_bootstrap_templates import ThemeSwitchAIO

# Carregar os dados
df = pd.read_csv("Students_Grading.csv")

# Temas
url_theme1 = dbc.themes.SOLAR
url_theme2 = dbc.themes.SPACELAB    

# Opções para os Dropdowns
grade_options = [{'label': x, 'value': x} for x in df['Grade'].unique()] 
marjors_options = [{'label': x, 'value': x} for x in df['Department'].unique()] 

# Templates Plotly
template_theme1 = 'solar'
template_theme2 = 'spacelab'

# Layout
app.layout = dbc.Container([
    # Linha 1
    dbc.Row([
        dbc.Col([
            ThemeSwitchAIO(aio_id='theme', themes=[url_theme1, url_theme2]),
            html.H3('Nível financeiro x Notas'),
            dcc.Dropdown(
                id='grades',
                value=[state['label'] for state in grade_options[:5]],
                multi=True,
                options=grade_options
            ),
            dcc.Graph(id='line_graph')
        ])
    ]),
    # Linha 2
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="curso1",
                value=marjors_options[0]['label'],
                options=marjors_options
            )
        ], sm=12, md=6),
        dbc.Col([
            dcc.Dropdown(
                id='curso2',
                value=marjors_options[1]['label'],
                options=marjors_options
            )
        ], sm=12, md=6),
    ]),
    #linha 3
    dbc.Row([
        dbc.Col([dcc.Graph(id='indicator1')], sm=12, md=6),
        dbc.Col([dcc.Graph(id='indicator2')], sm=12, md=6),
    ]),
     #linha 4
    dbc.Row([
      dbc.Col([
        html.H4("Distribuição de Horas de Estudo por Nota"),
        dcc.Graph(id='pizza_grafico')
    ])
  ]),
  #linha5
  dbc.Row([
    dbc.Col([
        html.H4("Correlação: Estresse vs Horas de Sono"),
        dcc.Graph(id='grafico_estresse_sono')
    ]),
    #linha 6
    dbc.Row([
    dbc.Col([
        html.H4("Distribuição de Notas por Curso"),
        dcc.Graph(id='grafico_nota_curso')
    ])
  ]),
#linha 7
dbc.Row([
    dbc.Col([
        html.H4("Correlação entre Educação dos Pais e Notas"),
        dcc.Graph(id='radar_educacao_grade')
    ])
 ])

])
])

#grafico de radar

@app.callback(
    Output('radar_educacao_grade', 'figure'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)

def radar_educacao_grade(toggle):
    template = template_theme1 if toggle else template_theme2

    df_data = df.copy()

    
    df_grouped = df_data.groupby(['Grade', 'Parent_Education_Level']).size().reset_index(name='Count')

    
    df_pivot = df_grouped.pivot(index='Grade', columns='Parent_Education_Level', values='Count').fillna(0)

    fig = go.Figure()

    for col in df_pivot.columns:
        fig.add_trace(go.Scatterpolar(
            r=df_pivot[col],
            theta=df_pivot.index,
            fill='toself',
            name=col
        ))

    fig.update_layout(
        title="Distribuição de Notas por Nível de Educação dos Pais",
        polar=dict(radialaxis=dict(visible=True)),
        template=template
    )

    return fig


#calback notas
@app.callback(
    Output('grafico_nota_curso', 'figure'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def grafico_nota_por_curso(toggle):
    template = template_theme1 if toggle else template_theme2

    df_data = df.copy()
    
    df_grouped = df_data.groupby(['Department', 'Grade']).size().reset_index(name='Count')

    fig = px.bar(
        df_grouped,
        x='Department',
        y='Count',
        color='Grade',
        barmode='group',
        title='Distribuição de Notas por Curso',
        template=template,
        labels={'Count': 'Número de Alunos', 'Department': 'Curso'}
    )

    return fig

# Callback do gráfico de linha
@app.callback(
    Output('line_graph', 'figure'),
    Input('grades', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),   
)
def line_graph(grades, toggle):
    template = template_theme1 if toggle else template_theme2
    df_data = df[df['Grade'].isin(grades)]

    df_grouped = df_data.groupby(['Family_Income_Level', 'Grade']).size().reset_index(name='Count')

    fig = px.line(df_grouped, x='Family_Income_Level', y='Count', color='Grade',
                  markers=True, title='Contagem de Alunos por Nível Financeiro e Nota',
                  template=template)
    return fig

# callback ddo grafico de pizza


@app.callback(
    Output('pizza_grafico', 'figure'), 
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)

def grafico_pizza(toggle):
    template = template_theme1 if toggle else template_theme2

    
    df['Study_Hours_per_Week'] = pd.to_numeric(df['Study_Hours_per_Week'], errors='coerce')

    
    df_grouped = df.groupby('Grade')['Study_Hours_per_Week'].sum().reset_index()

    fig = px.pie(df_grouped, names='Grade', values='Study_Hours_per_Week',
                 title='Total de Horas de Estudo por Nota',
                 template=template, hole=0.4)

    fig.update_traces(textinfo='percent+label')
    return fig

#callback sono
@app.callback(
    Output('grafico_estresse_sono', 'figure'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def grafico_estresse_barras(toggle):
    template = template_theme1 if toggle else template_theme2

    df_data = df.copy()
    df_data['Sleep_Hours_per_Night'] = pd.to_numeric(df_data['Sleep_Hours_per_Night'], errors='coerce')
    df_data['Stress_Level (1-10)'] = pd.to_numeric(df_data['Stress_Level (1-10)'], errors='coerce')

   
    bins = [0, 4, 6, 8, 10]
    labels = ['0-4h', '4-6h', '6-8h', '8-10h']
    df_data['Faixa_Sono'] = pd.cut(df_data['Sleep_Hours_per_Night'], bins=bins, labels=labels)

    
    df_grouped = df_data.groupby('Faixa_Sono')['Stress_Level (1-10)'].mean().reset_index()

    fig = px.bar(
        df_grouped,
        x='Faixa_Sono',
        y='Stress_Level (1-10)',
        title='Média de Estresse por Faixa de Horas de Sono',
        template=template,
        labels={'Stress_Level (1-10)': 'Estresse Médio', 'Faixa_Sono': 'Horas de Sono'}
    )

    fig.update_layout(yaxis_range=[0, 10])
    return fig

# callback dos indicadores de estresse
@app.callback(
    Output('indicator1', 'figure'),
    Output('indicator2', 'figure'),
    Input('curso1', 'value'),
    Input('curso2', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)

def indicator(curso1, curso2, toggle):
    template = template_theme1 if toggle else template_theme2

    fig1 = go.Figure()
    fig2 = go.Figure()

    stress_mean_1 = df[df['Department'] == curso1]['Stress_Level (1-10)'].mean()
    stress_mean_2 = df[df['Department'] == curso2]['Stress_Level (1-10)'].mean()

    fig1.add_trace(go.Indicator(
        mode='number',
        value=round(stress_mean_1, 2),
        title={'text': f"Média de Estresse - {curso1}"},
        number={'suffix': " / 10"},
    ))
    fig1.update_layout(template=template)

    fig2.add_trace(go.Indicator(
        mode='number',
        value=round(stress_mean_2, 2),
        title={'text': f"Média de Estresse - {curso2}"},
        number={'suffix': " / 10"},
    ))
    fig2.update_layout(template=template)

    return fig1, fig2

# Rodar o app
if __name__ == '__main__':
    app.run(debug=True, port=8051)
