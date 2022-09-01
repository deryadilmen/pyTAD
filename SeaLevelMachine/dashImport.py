import dash as dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, redirect
import flask as flask
import urllib as urllib
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import socket,platform,os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','technip.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

appserver=app.server

app.config.suppress_callback_exceptions = True








