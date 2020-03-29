import dash_core_components as dcc
import dash_bootstrap_components as dbc 
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from app import app
from . import graphq_tibber as gt 

    # fig.add_trace(go.Scatter(
    #     x=dt['timestamp'],
    #     y=dt['accumulated_cost'],
    #     name='Cost Since Midnight',
    #     showlegend=False

    # ), row=1, col=1)

RESOLUTIONS = ['HOURLY', 'DAILY', 'WEEKLY', 'MONTHLY', 'ANNOLY']

def get_tibber(resolution='HOURLY', periode=96):
    return gt.get_all(resolution=resolution, periode=periode)

## Mal
def build_scatter_graph(id, resolution='HOURLY', periode=96):
    df_home, df_owner, df_consumtion = get_tibber()
    months = ['Jan', 'Feb', 'Mars', 'Apr', 'May']
    values = [150, 130, 120, 110, 85]
    graph = dcc.Graph(
            id= id,
            figure = {
                'data': [
                    go.Scatter(
                        x=df_consumtion['to'],
                        y=df_consumtion['consumption'],
                        opacity=0.5                        
                    )
                ],
                'layout': go.Layout()
            }
        )
    return graph

def build_bar_graph(id, resolution='DAILY', periode=7):
    df_home, df_owner, df_consumtion = get_tibber(resolution=resolution, periode=periode)
    months = ['Jan', 'Feb', 'Mars', 'Apr', 'May']
    values = [150, 130, 120, 110, 85]
    graph = dcc.Graph(
            id= id,
            figure = {
                'data': [
                    go.Bar(
                        x=df_consumtion['to'],
                        y=df_consumtion['consumption']
                    )
                ],
                'layout': go.Layout()
            }
        )
    return graph

def go_indicator():
    return  go.Indicator(
                domain = {'x': [0, 1], 'y': [0, 1]},
                value = 0.4,
                mode = "gauge+number+delta",
                title = {'text': "Last Price"},
                delta = {'reference': 0.2},
                gauge = {'axis': {'range': [None, 0.5]},
                'steps' : [{'range': [0, 0.25], 'color': "lightgray"},{'range': [0.25, 0.5], 'color': "gray"}],
                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 490}}
            ) 


main_row = html.Div(
    [
        html.H2(children="Oversikt Brakke 4", className=''),
        dbc.Row(
            dbc.Col(build_scatter_graph(id='sct-daily'), align='center', className='')
        ),
        dbc.Row(
            [
                dbc.Col(build_bar_graph(id='bar-year'), width=4, className=''),
                dbc.Col(build_bar_graph(id='bar-month'), width=4, className=''),
                dbc.Col(build_bar_graph(id='bar-week'), width=4, className='')
            ]
        ),
    ], className='livebody'
)

layout = html.Div([
    main_row
])