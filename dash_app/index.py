"""index.py
"""

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app #, models, execute_db
from apps import home, livedata


app.layout = html.Div([   
    html.Div([
        html.Div([
            html.H3('Heading for Multi Page App')
        ]),         
        dcc.Link('Home', href='/', style={'paddingRight':'10px'}),
        dcc.Link('Live', href='/live', style={'paddingRight':'10px'}),
        dcc.Location(id='url', refresh=False)
    ], className='navbar'),
    html.Div(id='main-content', children='Main', className='')
], className='')


@app.callback(Output('main-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return home.layout
    elif pathname == '/live':
        return livedata.layout
    else:
        return html.H3('Page not found 404')


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')