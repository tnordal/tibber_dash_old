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

RESOLUTIONS = ['HOURLY', 'DAILY', 'WEEKLY', 'MONTHLY', 'ANNUAL']

def get_tibber(resolution='HOURLY', periode=96):
    return gt.get_all(resolution=resolution, periode=periode)

## Mal
def build_scatter_graph(resolution='HOURLY', periode=96):
    df_home, df_owner, df_consumtion = get_tibber(resolution=resolution, periode=periode)
    sum_consumtion = df_consumtion['consumption'].sum()
    figure = {
        'data': [
            go.Scatter(
                x=df_consumtion['to'],
                y=df_consumtion['consumption'],
                opacity=0.5                        
            )
        ],
        'layout': go.Layout(
            title='Forbruk siste {} timene: {:.2f} kwh'.format(periode, sum_consumtion)
        )
    }

    return figure

def build_bar_graph(resolution='DAILY', periode=7):
    df_home, df_owner, df_consumtion = get_tibber(resolution=resolution, periode=periode)
    months = ['Jan', 'Feb', 'Mars', 'Apr', 'May']
    values = [150, 130, 120, 110, 85]
    figure = {
        'data': [
            go.Bar(
                x=df_consumtion['to'],
                y=df_consumtion['consumption']
            )
        ],
        'layout': go.Layout()
    }
    return figure

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
        dcc.Interval(
            id='interval_home',
            interval= (60*1000),
            n_intervals=0
        ),        
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='Hourly-trend',
                    figure=build_scatter_graph(),
                    config={
                        'displayModeBar':False
                    }          
                )
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='bar-year',
                        figure= build_bar_graph(resolution='MONTHLY', periode=12)
                    ),
                    width=4, className=''
                ),
                dbc.Col(
                    dcc.Graph(
                        id='bar-month',
                        figure= build_bar_graph(resolution='WEEKLY', periode=4),
                        config={
                            'displayModeBar':False
                        }
                    ),
                    width=4, className=''
                ),                    
                dbc.Col(
                    dcc.Graph(
                        id='bar-week',
                        figure= build_bar_graph(resolution='DAILY', periode=7),
                        config={
                            'displayModeBar':False
                        }                    
                    ),                    
                    width=4, className=''
                )
            ]
        ),
    ], className='livebody'
)

layout = html.Div([
    main_row
])


@app.callback(
    Output('Hourly-trend', 'figure'),
    [Input('interval_home', 'n_intervals')]
)
def update_hour_trend(n):
    return build_scatter_graph(resolution='HOURLY', periode=24)

@app.callback(
    Output('bar-year', 'figure'),
    [Input('interval_home', 'n_intervals')]
)
def update_bar_year(n):
    return build_bar_graph(resolution='MONTHLY', periode=12)

@app.callback(
    Output('bar-month', 'figure'),
    [Input('interval_home', 'n_intervals')]
)
def update_bar_month(n):
    return build_bar_graph(resolution='WEEKLY', periode=4)

@app.callback(
    Output('bar-week', 'figure'),
    [Input('interval_home', 'n_intervals')]
)
def update_bar_week(n):
    # print('=========== Oppdateres ============')
    return build_bar_graph(resolution='DAILY', periode=7)
