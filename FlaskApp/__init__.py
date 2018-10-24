import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from collections import deque
import plotly.graph_objs as go
import psycopg2
import pandas as pd
from dash.dependencies import Output, Event, Input, State
import dash_table_experiments as dt
#Switch these two when putting live
#Live Code
#import urllib.parse
#Testing Code
import urllib

import sys
from .base.basescript import app, server
from .apps import custom, easy











## insertion point for css and js
external_css = [
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css'
]


for css in external_css:
    app.css.append_css({'external_url': css})


app.layout = html.Div([
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')

])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/easy':
         return easy.layout
    elif pathname == '/custom':
         return custom.layout
    else:
        return custom.layout

if __name__ == '__main__':
    app.run_server(debug=True)