import dash_core_components as dcc
import dash_bootstrap_components as dbc 
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from app import app

    # fig.add_trace(go.Scatter(
    #     x=dt['timestamp'],
    #     y=dt['accumulated_cost'],
    #     name='Cost Since Midnight',
    #     showlegend=False

    # ), row=1, col=1)

## Mal
def build_scatter_graph(id):
    months = ['Jan', 'Feb', 'Mars', 'Apr', 'May']
    values = [150, 130, 120, 110, 85]
    graph = dcc.Graph(
            id= id,
            figure = {
                'data': [
                    go.Scatter(
                        x=months,
                        y=values,
                        opacity=0.5                        
                    )
                ],
                'layout': go.Layout()
            }
        )
    return graph

def build_bar_graph(id):
    months = ['Jan', 'Feb', 'Mars', 'Apr', 'May']
    values = [150, 130, 120, 110, 85]
    graph = dcc.Graph(
            id= id,
            figure = {
                'data': [
                    go.Bar(
                        x=months,
                        y=values
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
        html.H2(children="Ovesikt Brakke 4", className=''),
        dbc.Row(
            dbc.Col(build_scatter_graph(id='sct-daily'), align='center', className='bg-light')
        ),
        dbc.Row(
            [
                dbc.Col(build_bar_graph(id='bar-year'), width=4, className='bg-light'),
                dbc.Col(build_bar_graph(id='bar-month'), width=4, className='bg-light'),
                dbc.Col(build_bar_graph(id='bar-week'), width=4, className='bg-light')
            ]
        ),
    ], className='align-items-center'
)

layout = html.Div([
    main_row
])