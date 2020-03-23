import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import numpy as np 

from app import app

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

    fig.add_trace(go.Indicator(
        value = price,
        name = 'Tarzan',
        title={'text':'Current Price'},
        mode='gauge+number',
        delta = {'reference': 200},
        gauge = {
            'axis': {'visible': True},
            'bgcolor':'blue'},
        domain = {'row': 0, 'column': 0}))

    fig.add_trace(go.Indicator(
        value = power,
        title={'text':'Power'},
        delta = {'reference': 200},
        mode='gauge+number',
        gauge = {
            'axis': {'visible': True},
            'bgcolor':'blue'},        
        domain = {'row': 0, 'column': 1}))

    fig.add_trace(go.Indicator(
        value = consumption,
        title={'text':'Cunsumtion since midnight'},
        delta = {'reference': 200},
        mode='gauge+number',
        gauge = {
            'axis': {'visible': True},
            'bgcolor':'blue'},
        domain = {'row': 0, 'column': 2}))

    fig.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"}
        )


    return fig

def build_3trends():
    fig = make_subplots(rows=1, cols=3)

    x = [0,1,2,3,4,5]
    y = [0,1,2,3,4,5]

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        name='Current Price',
        showlegend=False

    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        name='Current Power',
        showlegend=False

    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        name='Consumption since midnight',
        showlegend=False

    ), row=1, col=3)   

    fig.update_layout(title_text='Title')

    return fig


layout = html.Div([
    dcc.Interval(
        id='interval_indicators',
        interval=2000,
        n_intervals=0
    ),
    dcc.Graph(
        id='Testing_3',
        figure = build_3figures()
    ),
    dcc.Graph(
        id='testing_trends',
        figure=build_3trends()
    )
], className='main livebody')



@app.callback(
    Output('Testing_3', 'figure'),
    [Input('interval_indicators', 'n_intervals')]
)
def update_indicators(n_intervals):
    price = np.random.random()
    power = 3000 * price
    consumption = 30 * price
    return build_3figures(price=price, power=power, consumption=consumption)
