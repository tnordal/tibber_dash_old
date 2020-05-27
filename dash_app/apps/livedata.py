import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import numpy as np 
import os
import pandas as pd 

from app import app
from . import db

dt = db.live_data_history()

dropdown_options = []
for i in range(1,61):
    opt = {'label': str(i) + ' minutes', 'value': i}
    dropdown_options.append(opt)


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



def build_3figures(price=0.25, power=2500, consumption=30.6):

    fig = go.Figure()

    max_range_power = 7000
    if power > max_range_power:
        max_range_power = power * 1.2
    
    if power >=5000:
        power_bar_color = 'red'
    elif power > 2000:
        power_bar_color = 'yellow'
    else:
        power_bar_color = 'green'
    
    max_consumtion = 50
    if consumption > max_consumtion:
        max_consumtion = consumption * 1.2
    
    if consumption >= 50:
        consumption_bar_color = 'red'
    elif consumption >= 40:
        consumption_bar_color = 'yellow'
    else:
        consumption_bar_color = 'green'

    max_cost = 5
    if price > max_cost:
        max_cost = price * 1.2
    
    if price >= 5:
        price_bar_color = 'red'
    elif price >= 4:
        price_bar_color = 'yellow'
    else:
        price_bar_color = 'green'
    
    fig.add_trace(go.Indicator(
        value = price,
        number= {'valueformat':'.3s'},
        name = 'Tarzan',
        title={'text':'Cost since midnight'},
        mode='gauge+number+delta',
        delta = {'reference': 5, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':'#3D9970'}},
        gauge = {
            'axis': {'visible': True, 'range': [None, max_cost]},
            'bgcolor':'blue',
            'bar':{'color':price_bar_color},
            'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 4}},
        domain = {'row': 0, 'column': 0}))

    fig.add_trace(go.Indicator(
        value = power,
        title={'text':'Power'},
        delta = {'reference': 2000, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':'#3D9970'}},
        mode='gauge+number+delta',
        gauge = {
            'axis': {'visible': True, 'range': [None, max_range_power]},
            'bgcolor':'blue',
            'bar':{'color':power_bar_color},
            'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 2000}},        
        domain = {'row': 0, 'column': 1}))

    fig.add_trace(go.Indicator(
        value = consumption,
        number= {'valueformat':'.4s'},
        title={'text':'Cunsumtion since midnight'},
        delta = {'reference': 40, 'increasing':{'color':'#FF4136'}, 'decreasing':{'color':'#3D9970'}},
        mode='gauge+number+delta',
        gauge = {
            'axis': {'visible': True, 'range': [None, max_consumtion]},
            'bgcolor':'blue',
            'bar':{'color':consumption_bar_color},
            'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 40}},                 
        domain = {'row': 0, 'column': 2}))

    fig.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"},
        template='plotly_dark'
        )


    return fig

def build_3trends(dt):
    fig = make_subplots(rows=1, cols=1)
    dt['min'] = dt['power'].min()
    dt['max'] = dt['power'].max()
    if len(dt) > 0: 
        x = dt['timestamp']
        y = dt['power']
        y2 = dt['min']
        y3 = dt['max']
    else:
        x = [0,1,2,3,4,5]
        y = [0,1,2,3,4,5]
        y2 = [10,11,12,13,14,15]
        y3 = [10,11,12,13,14,15]

    fig.add_trace(go.Scatter(
        x=x,
        y=y3,
        name='Max Power',
        showlegend=True
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        name='Current Power',
        showlegend=True

    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=x,
        y=y2,
        name='Min Power',
        showlegend=True
    ), row=1, col=1)

    fig.update_layout(title_text='Current power use!', template='plotly_dark', yaxis={'rangemode':'normal'})

    return fig


layout = html.Div([
    dcc.Interval(
        id='interval_indicators',
        interval=2000,
        n_intervals=0
    ),
    dcc.Graph(
        id='Testing_3',
        figure = build_3figures(),
        config = {
            'displayModeBar':False
        }
    ),
    html.Div(
        [
            html.P('Choose minutes for trend:', style={'padding-right':'5px', 'padding-left':'20px','padding-top':'5px', 'font-weight':'bold'}),
            dcc.Dropdown(
                id='dropdown-trend-interval',
                options=dropdown_options,
                value=15,
                style={'width':'200px', 'background':'#ccc'}
            )         
        ],
        className='row',
        style={'vertical-align':'middle'}
    ),
    dcc.Graph(
        id='testing_trends',
        figure=build_3trends(dt),
        config = {
            'displayModeBar':False
        }        
    )
], className='main livebody', style={"height" : "100vh"})



@app.callback(
    Output('Testing_3', 'figure'),
    [Input('interval_indicators', 'n_intervals')]
)
def update_indicators(n_intervals):
    results = db.live_data()
    price = results['accumulated_cost']
    power = results['power']
    consumption = results['accumulated']
    return build_3figures(price=price, power=power, consumption=consumption)


@app.callback(
    Output('testing_trends', 'figure'),
    [
        Input('interval_indicators', 'n_intervals'),
        Input('dropdown-trend-interval', 'value')
    ]
)
def update_trends(n_intervals, interval):
    if interval == None:
        interval=15
    dt = db.live_data_history(minutes=interval)
    return build_3trends(dt)



