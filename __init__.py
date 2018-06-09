#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3
import pandas as pd
import datetime
import time
import configparser




####  PROD ####
if server_type == 'PROD':
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
