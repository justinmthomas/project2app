#!/usr/bin/env python
# coding: utf-8

#pip install flask-cors

#pip install boto3

import os
import pandas as pd
import sqlalchemy
import pymysql
import sys
from pandas.io.json import json_normalize
pymysql.install_as_MySQLdb()
import chardet

#import dash dependencies
import base64
import datetime
import io
import plotly.graph_objs as go
import cufflinks as cf
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
import chart_library as cl
import itertools as it
import decision_tree as dt
import flask
import string
import secrets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#Importing additional elemtns for S3 self signed URL generation
from flask import Flask, render_template, request, redirect, url_for
#change
#Import JSON library and Amazon BOTO3 SDK library for Python
import json, boto3
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import (
    Flask,
    render_template,
    jsonify,
    request)
from flask_cors import CORS


#Keep config file for our info. 
remote_db_endpoint = os.environ.get('remote_db_endpoint')
remote_db_port = os.environ.get('remote_db_port')
remote_gwsis_dbname = os.environ.get('remote_gwsis_dbname')
remote_gwsis_dbpwd = os.environ.get('remote_gwsis_dbpwd')
remote_gwsis_dbuser = os.environ.get('remote_gwsis_dbuser')


#Create Cloud DB Connection. 
engine = create_engine(f"mysql+pymysql://{remote_gwsis_dbuser}:{remote_gwsis_dbpwd}@{remote_db_endpoint}:{remote_db_port}/{remote_gwsis_dbname}")
conn = engine.connect()

app = flask.Flask(__name__)
CORS(app)

server = flask.Flask(__name__)

@server.route('/')
def index():
    return 'Hello Flask app'

@server.route('/postfeedback', methods = ['POST'])
def postFeedbackHandler(feedback1):

    print(feedback1)
    print('sql started')
    
    #write feedback.df to SQL 
    feedback1.to_sql(con=conn, name='survey_results', if_exists='append', index=False)
    #session.commit()
    print('sql fired')
    return None


app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                routes_pathname_prefix='/dash/',
                server =server,
                meta_tags=[{
                    'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1.0'
                    }]
                )

# server = app.server

app.config['suppress_callback_exceptions'] = True

ddoptions = [
    {"label": "Category", "value": "CAT"},
    {"label": "Date", "value": "DTE"},
    {"label": "Value", "value": "VAL"},
    {"label": "Boolean", "value": "BOL"},
    {"label": "Location", "value": "LOC"},
    {"label": "Latitude", "value": "LAT"},
    {"label": "Longitude", "value": "LON"},
    ]   

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

def generateSecureRandomString(stringLength=50):
    """Generate a secure random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(password_characters) for i in range(stringLength))

def graph_maker(df,pairs):

    charts = []

    chartnum = 0

    for k,v in pairs.items():
        gcol = k.split('vs')
        xcol = gcol[0]
        ycol = gcol[1]
        try:
            zcol = gcol[2]
        except:
            None
        xval = df[xcol]
        yval = df[ycol]
        try:
            zval = df[zcol]
        except:
            None
        chartnum+=1
        if v[0] == "Bar":
            charts.append(html.Div([
                    dcc.Graph(id=f'auto-graph{chartnum}',
                    figure=cl.bar_function(xval,yval)),
                    html.Label("Does the above chart show what you wanted?"),
                    dcc.RadioItems(
                        id=f'auto-graph-radio{chartnum}',
                        options=[
                            {'label': 'Yes', 'value': f'y,{v[0]},{v[1]}'},
                            {'label': 'No', 'value': f'n,{v[0]},{v[1]}'}
                        ],
                        labelStyle={'display': 'inline-block'})
                    # html.Button(id=f'auto-graph-button{chartnum}',
                    # n_clicks=0,
                    # children='Download PNG')

                    ])
                    )
        elif v[0] == "Map":
            charts.append(html.Div([
                    dcc.Graph(id=f'auto-graph{chartnum}',
                    figure=cl.map_function(xval,yval,zval)),
                    html.Label("Does the above chart show what you wanted?"),
                    dcc.RadioItems(
                        id=f'auto-graph-radio{chartnum}',
                        options=[
                            {'label': 'Yes', 'value': f'y,{v[0]},{v[1]}'},
                            {'label': 'No', 'value': f'n,{v[0]},{v[1]}'}
                        ],
                        labelStyle={'display': 'inline-block'})
                    # html.Button(id=f'auto-graph-button{chartnum}',
                    # n_clicks=0,
                    # children='Download PNG')
                    ]))
        elif v[0] == "Rings":
            charts.append(html.Div([
                    dcc.Graph(id=f'auto-graph{chartnum}',
                    figure=cl.rings_function(xval,yval)),
                    html.Label("Does the above chart show what you wanted?"),
                    dcc.RadioItems(
                        id=f'auto-graph-radio{chartnum}',
                        options=[
                            {'label': 'Yes', 'value': f'y,{v[0]},{v[1]}'},
                            {'label': 'No', 'value': f'n,{v[0]},{v[1]}'}
                        ],
                        labelStyle={'display': 'inline-block'})
                    # html.Button(id=f'auto-graph-button{chartnum}',
                    # n_clicks=0,
                    # children='Download PNG')
                    ]))
        elif v[0] == "Bubble":
            charts.append(html.Div([
                    dcc.Graph(id=f'auto-graph{chartnum}',
                    figure=cl.bubble_function(xval,yval)),
                    html.Label("Does the above chart show what you wanted?"),
                    dcc.RadioItems(
                        id=f'auto-graph-radio{chartnum}',
                        options=[
                            {'label': 'Yes', 'value': f'y,{v[0]},{v[1]}'},
                            {'label': 'No', 'value': f'n,{v[0]},{v[1]}'}
                        ],
                        labelStyle={'display': 'inline-block'})
                    # html.Button(id=f'auto-graph-button{chartnum}',
                    # n_clicks=0,
                    # children='Download PNG')
                    ]))
        elif v[0] == "Table":
            charts.append(html.Div([
                    html.Div(id=f'auto-graph{chartnum}',
                    children=cl.chart_function(xval,df)),
                    html.Label("Does the above chart show what you wanted?"),
                    dcc.RadioItems(
                        id=f'auto-graph-radio{chartnum}',
                        options=[
                            {'label': 'Yes', 'value': f'y,{v[0]},{v[1]}'},
                            {'label': 'No', 'value': f'n,{v[0]},{v[1]}'}
                        ],
                        labelStyle={'display': 'inline-block'})
                    # html.Button(id=f'auto-graph-button{chartnum}',
                    # n_clicks=0,
                    # children='Download PNG')
                    ]))
        elif v[0] == "Scatter":
            charts.append(html.Div([
                    dcc.Graph(id=f'auto-graph{chartnum}',
                    figure=cl.scatter_function(xval,yval)),
                    html.Label("Does the above chart show what you wanted?"),
                    dcc.RadioItems(
                        id=f'auto-graph-radio{chartnum}',
                        options=[
                            {'label': 'Yes', 'value': f'y,{v[0]},{v[1]}'},
                            {'label': 'No', 'value': f'n,{v[0]},{v[1]}'}
                        ],
                        labelStyle={'display': 'inline-block'})
                    # html.Button(id=f'auto-graph-button{chartnum}',
                    # n_clicks=0,
                    # children='Download PNG')
                    ]))
        elif v[0] == "Pie":
            charts.append(html.Div([
                    dcc.Graph(id=f'auto-graph{chartnum}',
                    figure=cl.pie_function(xval,yval)),
                    html.Label("Does the above chart show what you wanted?"),
                    dcc.RadioItems(
                        id=f'auto-graph-radio{chartnum}',
                        options=[
                            {'label': 'Yes', 'value': f'y,{v[0]},{v[1]}'},
                            {'label': 'No', 'value': f'n,{v[0]},{v[1]}'}
                        ],
                        labelStyle={'display': 'inline-block'})
                    # html.Button(id=f'auto-graph-button{chartnum}',
                    # n_clicks=0,
                    # children='Download PNG')
                    ]))
        elif v[0] == "Line":
            charts.append(html.Div([
                    dcc.Graph(id=f'auto-graph{chartnum}',
                    figure=cl.line_function(xval,yval)),
                    html.Label("Does the above chart show what you wanted?"),
                    dcc.RadioItems(
                        id=f'auto-graph-radio{chartnum}',
                        options=[
                            {'label': 'Yes', 'value': f'y,{v[0]},{v[1]}'},
                            {'label': 'No', 'value': f'n,{v[0]},{v[1]}'}
                        ],
                        labelStyle={'display': 'inline-block'})
                    # html.Button(id=f'auto-graph-button{chartnum}',
                    # n_clicks=0,
                    # children='Download PNG')
                    ]))
    return charts

def feedback_maker(a):
    if a == "CATvsVAL":
        a = 'categoryvsvalue'
    elif a == "CATvsLATvsLON":
        a = 'categoryvslatvslon'
    elif a == "LOCvsVAL":
        a = 'valuevslocation'
    elif a == "DTEvsVAL":
        a = 'valuevstime'
    elif a == "VALvsVAL":
        a = 'valuevsvalue'
    elif a == "VALvsBOL" or v == "CATvsBOL":
        a = 'comparison'
    return a

def decision_func(d):
    all_pairs3 = [{j: d[j] for j in i} for i in it.permutations(d, 3)]
    all_pairs2 = [{j: d[j] for j in i} for i in it.permutations(d, 2)]
        

    data_pairsv = []
    data_pairsk = []
    data_pairsv1 = []
    data_pairsk1 = []


    for p in all_pairs2:
        data_pairsv.append(list(p.values()))

    for p in all_pairs2:
        data_pairsk.append(list(p.keys()))

    for p in all_pairs3:
        data_pairsv.append(list(p.values()))

    for p in all_pairs3:
        data_pairsk.append(list(p.keys()))

    for v in data_pairsv:
        data_pairsv1.append('vs'.join(v))

    for k in data_pairsk:
        data_pairsk1.append('vs'.join(k))

    zippedpairs = zip(data_pairsk1, data_pairsv1)
    fp = dict(zippedpairs)

    for k,v in fp.items():
        vlist = []
        if v == "CATvsVAL":
            a = dt.decision([1,1,0,0,0,0])
        elif v == "CATvsLATvsLON":
            # a = dt.decision([1,0,0,1,0,0])
            a = ['Map']
        elif v == "LOCvsVAL":
            a = dt.decision([1,0,0,1,0,0])
        elif v == "DTEvsVAL":
            a = dt.decision([1,0,0,0,1,0])
        elif v == "VALvsVAL":
            a = dt.decision([1,0,0,0,0,1])
        elif v == "VALvsBOL" or v == "CATvsBOL":
            a = dt.decision([1,0,1,0,0,0])
        else:
            a = "None"
        vlist.append(a[0])
        vlist.append(v)
        fp[k] = vlist

    print(fp)

    for k,v in list(fp.items()):
        if v[0] == "N":
            del fp[k]   

    return fp

def feedback_func(rvalue):

    try:
        if len(rvalue) is None:
            print("radio empty")
            return []
        else:
            
            radioval=rvalue.split(',')

            datatype = feedback_maker(radioval[2])

            if radioval[0] == 'y':
                feedback = dict(
                    Survey_ID=generateSecureRandomString(),
                    value='feedbk',
                    Data_Type=datatype,
                    Chart_Type=radioval[1],
                    Correct=1
                    )
                feedback = pd.DataFrame([feedback])
                feedback = feedback.reindex(columns=["Survey_ID", "value", "Data_Type", "Chart_Type", "Correct"])
                print(feedback)
                

            elif radioval[0] == 'n':
                feedback = dict(
                    Survey_ID=generateSecureRandomString(),
                    value='feedbk',
                    Data_Type=datatype,
                    Chart_Type=radioval[1],
                    Correct=0
                    )
                feedback = pd.DataFrame([feedback])
                feedback = feedback.reindex(columns=["Survey_ID", "value", "Data_Type", "Chart_Type", "Correct"])
                print(feedback)
                

            # return None
            return postFeedbackHandler(feedback)
    except:
        None


####start dash app scripting#####

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '99%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Label("File List"),
    html.Br(),
    html.Ul(id="complete-upload"),

    html.Br(),
    html.Label('Once your data has been uploaded click on "Load Columns"'),

    html.Br(),
    html.Button(
        id='propagate-button',
        n_clicks=0,
        children='Load Columns'
    ),
    html.Br(),
    html.Br(),
    html.Label(id='column-checklist_text'),
    html.Br(),
    dcc.Checklist(id='column-checklist',
                    labelStyle = {
                        'display': 'inline-block',
                        'marginRight': 10,
                        'value':[]
                        }),

    # dcc.Graph(id='Mygraph'),
    # html.Div(id = 'complete-df',
    #         # children = [data_dict],
    #         style = {'display': 'none'}),

    dcc.Store(id='complete-df'),


    # html.Div(id='display-selected-values'),
    html.Br(),
    html.Label(id='data-type-text'),
    html.Br(),
    html.Div(id='choosen_columns_data'),
    html.Br(),
    html.Div(id='submit_button'),

    html.Label(id ='mydropdown-1'),
    html.Label(id ='mydropdown-2'),
    html.Label(id ='mydropdown-3'),
    html.Label(id ='mydropdown-4'),
    html.Label(id ='mydropdown-5'),
    html.Label(id ='mydropdown-6'),

    html.Br(),
    # html.Div(id='dropdown-values2', style = {'display': 'none'}),
    # html.Div(id='dropdown-values3', style = {'display': 'none'}),
    # html.Div(id='dropdown-values4', style = {'display': 'none'}),
    # html.Div(id='dropdown-values5', style = {'display': 'none'}),
    # html.Div(id='dropdown-values6', style = {'display': 'none'}),


    html.Div(id='auto-graph-radio1-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio2-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio3-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio4-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio5-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio6-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio7-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio8-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio9-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio10-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio11-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio12-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio13-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio14-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio15-output', style = {'display': 'none'}),
    html.Div(id='auto-graph-radio16-output', style = {'display': 'none'}),
 

    html.Div(id='dropdown-values2'),
    html.Div(id='dropdown-values3'),
    html.Div(id='dropdown-values4'),
    html.Div(id='dropdown-values5'),
    html.Div(id='dropdown-values6'),
    ])

##Upload Data

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df

##Show when a file is uploaded
@app.callback(
                Output('complete-upload', 'children'),

                [Input('upload-data', 'filename')]
            )

def upload_complete(filename):

    filename = filename

    if filename is None:
        return [html.Li("No files have been loaded yet!")]
    else:
        return [html.Li(filename) for filename in filename]

####Create dataframe

@app.callback(
                Output('complete-df', 'data'),

                [
                Input('propagate-button', 'n_clicks'),
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
                ]
            )


def create_df(n_clicks_update, contents, filename):

    if n_clicks_update < 1:
        print("df empty")
        return []

    else:

        if contents:
            contents = contents[0]
            filename = filename[0]
            df = parse_data(contents, filename)
            df = df.to_json()
            
        # return df.to_dict('records')
        return df


## Display Select Columns Text
@app.callback(
                Output('column-checklist_text', 'children'),
                [
                Input('propagate-button', 'n_clicks'),
                ]
            )

def update_columns(n_clicks_update):

    if n_clicks_update < 1:
        print("df empty")
        return []

    else:
 
        return [html.Label("Select between two and six columns to visualize:")]

## Get Column Names when button is clicked and create check list
@app.callback(
                Output('column-checklist', 'options'),
                [
                Input('propagate-button', 'n_clicks'),
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
                ]
            )

def update_columns(n_clicks_update, contents, filename):

    if n_clicks_update < 1:
        print("df empty")
        return []

    else:

        if contents:
            contents = contents[0]
            filename = filename[0]
            df = parse_data(contents, filename)
            column_head = [{'label': i, 'value': i} for i in df.columns]

        return column_head

## Display Select Data type Text
@app.callback(
                Output('data-type-text', 'children'),
                [
                Input('column-checklist', 'value'),
                ]
            )

def update_columns(col_value):
    
    try:
        if len(col_value) is None:
            print("df empty")
            return []
        else:
            print(len(col_value))
            return [html.Label("Select the data type for each column:")]
    except:
        None



# hide unused graph id's
@app.callback(
                
                Output('dropdown-values2', 'style'),
                [
                Input('column-checklist', 'value'),
                ],
                [
                State('dropdown-values2', 'style')    
                ]
            )

def hide_ids2(col_values, current_style):

    try: 
        if len(col_values) == 2:
            current_style['display'] = ''
            print(f"{len(col_values)}s have been clicked display all 2")
        else:
            current_style['display'] = 'none'
            print(f"{len(col_values)}s have been clicked dont display 2")
        return current_style

    except:
        None

# hide unused graph id's
@app.callback(
                Output('dropdown-values3', 'style'),
                [
                Input('column-checklist', 'value'),
                ],
                [
                State('dropdown-values3', 'style')    
                ]
            )

def hide_ids3(col_values, current_style):

    try:
        if len(col_values) == 3:
            current_style['display'] = ''
            print(f"{len(col_values)}s have been clicked display all 3")
        else:
            current_style['display'] = 'none'
            print(f"{len(col_values)}s have been clicked dont display 3")
        return current_style

    except:
        None

# hide unused graph id's
@app.callback(
                Output('dropdown-values4', 'style'),
                [
                Input('column-checklist', 'value'),
                ],
                [
                State('dropdown-values4', 'style')    
                ]
            )

def hide_ids4(col_values, current_style):

    try:
        if len(col_values) == 4:
            current_style['display'] = ''
            print(f"{len(col_values)}s have been clicked display all 4")
        else:
            current_style['display'] = 'none'
            print(f"{len(col_values)}s have been clicked dont display 4")
        return current_style

    except:
        None

# hide unused graph id's
@app.callback(
                Output('dropdown-values5', 'style'),
                [
                Input('column-checklist', 'value'),
                ],
                [
                State('dropdown-values5', 'style')    
                ]
            )

def hide_ids5(col_values, current_style):

    try:
        if len(col_values) == 5:
            current_style['display'] = ''
            print(f"{len(col_values)}s have been clicked display all 5")
        else:
            current_style['display'] = 'none'
            print(f"{len(col_values)}s have been clicked dont display 5")
        return current_style

    except:
        None


# hide unused graph id's
@app.callback(
                Output('dropdown-values6', 'style'),
                [
                Input('column-checklist', 'value'),
                ],
                [
                State('dropdown-values6', 'style')    
                ]
            )

def hide_ids6(col_values, current_style):

    try:
        if len(col_values) == 6:
            current_style['display'] = ''
            print(f"{len(col_values)}s have been clicked display all 6")
        else:
            current_style['display'] = 'none'
            print(f"{len(col_values)}s have been clicked dont display 6")
        return current_style

    except:
        None


# List selected columns with dropdowns for data type
@app.callback(
                Output('choosen_columns_data', 'children'),
                [
                Input('column-checklist', 'value'),
                ]
            )

def create_dropdowns(selected_col):

    ddcreator = []

    x=0
    try:    
        print(len(selected_col))
        for i in selected_col:
            x+=1
            dd =html.Div(
                    html.Label(
                        [i,
                        dcc.Dropdown(
                            id=f"mydropdown-{x}",
                            # id="mydropdown-1",
                            className=i,
                            options = ddoptions,
                            persistence_type = 'memory',
                            persistence = True
                            )
                        ]
                    ),
                style={'width': '20%','marginRight': 10, 'display': 'inline-block'}
                # style={'width': f'{col_width}%','marginRight': 10, 'display': 'inline-block'}
                )
            

            ddcreator.append(dd)
    except:
        None


    return ddcreator

## Submit Button
@app.callback(
                Output('submit_button', 'children'),
                [
                # Input('choosen_columns_data', 'values'),
                Input('column-checklist', 'value'),
                ]
            )

def update_columns(values):

    try:    
        if len(values) < 1:
            print("df empty")
            return []
        else:
            button = html.Div([
                    html.Button(id='submit-button',
                    n_clicks=0,
                    children='Submit'
                    ),
                    # html.Button(id='refresh-button',
                    # n_clicks=0,
                    # children='Reset',
                    # style={
                    #     'marginRight': 10
                    # }
                    # )
                ])

            return button
    except:
        None

# ##reset page
# @app.callback(
#                 Output('reset_button', 'children'),
#                 [
#                 Input('refresh_button', 'n_clicks'),
#                 ]
#             )

# def reset_page(
#                     n_clicks,
#                     ):

#     try:
#         if n_clicks < 1:
#             print("reset button has not been clicked")
#             return []

#         else:
#             reset = html.A('Refresh', href='/')

#             return reset
        
#     except:
#         None


##Call Back for 6 Columns
@app.callback(
                Output('dropdown-values6', 'children'),
                [
                Input('submit_button', 'n_clicks'),
                Input('choosen_columns_data', 'value'),
                Input('complete-df', 'data'),
                ],
                [
                State('mydropdown-1', 'className'),
                State('mydropdown-1', 'value'),
                State('mydropdown-2', 'className'),
                State('mydropdown-2', 'value'),
                State('mydropdown-3', 'className'),
                State('mydropdown-3', 'value'),
                State('mydropdown-4', 'className'),
                State('mydropdown-4', 'value'),
                State('mydropdown-5', 'className'),
                State('mydropdown-5', 'value'),
                State('mydropdown-6', 'className'),
                State('mydropdown-6', 'value'),
                ]
            )

def update_columns6(
                    n_clicks,
                    ddvalues,
                    dfdata, 
                    dd1class, dd1value,
                    dd2class, dd2value,
                    dd3class, dd3value,
                    dd4class, dd4value,
                    dd5class, dd5value,
                    dd6class, dd6value,
                    # *ddclass, **ddvalue,
                    ):

    try:
        if n_clicks < 1:
            print("no drop down values")
            return []

        else:
            list1 = []
            list2 = []

            # for i in ddclass:
            #     list1.append(ddclass)

            # print(list1)
            
            list1.append(dd1class)
            list1.append(dd2class)
            list1.append(dd3class)
            list1.append(dd4class)
            list1.append(dd5class)
            list1.append(dd6class)


            list2.append(dd1value)
            list2.append(dd2value)
            list2.append(dd3value)
            list2.append(dd4value)
            list2.append(dd5value)
            list2.append(dd6value)

            zipped = zip(list1, list2)
            d = dict(zipped)

            finalpairs = decision_func(d)

            df = pd.read_json(dfdata)

            charts = graph_maker(df,finalpairs)

            return charts
        
    except:
        None

# ##Call Back for 5 Columns
@app.callback(
                Output('dropdown-values5', 'children'),
                [
                Input('submit_button', 'n_clicks'),
                Input('choosen_columns_data', 'value'),
                Input('complete-df', 'data'),
                ],
                [
                State('mydropdown-1', 'className'),
                State('mydropdown-1', 'value'),
                State('mydropdown-2', 'className'),
                State('mydropdown-2', 'value'),
                State('mydropdown-3', 'className'),
                State('mydropdown-3', 'value'),
                State('mydropdown-4', 'className'),
                State('mydropdown-4', 'value'),
                State('mydropdown-5', 'className'),
                State('mydropdown-5', 'value'),
                ]
            )

def update_columns5(n_clicks, ddvalues,
                    dfdata, 
                    dd1class, dd1value,
                    dd2class, dd2value,
                    dd3class, dd3value,
                    dd4class, dd4value,
                    dd5class, dd5value,
                    ):
    try:

        if n_clicks < 1:
            print("no drop down values")
            return []

        else:

            list1 = []
            list2 = []
            
            list1.append(dd1class)
            list1.append(dd2class)
            list1.append(dd3class)
            list1.append(dd4class)
            list1.append(dd5class)

            list2.append(dd1value)
            list2.append(dd2value)
            list2.append(dd3value)
            list2.append(dd4value)
            list2.append(dd5value)

            zipped = zip(list1, list2)
            d = dict(zipped)

            finalpairs = decision_func(d)

            df = pd.read_json(dfdata)

            charts = graph_maker(df,finalpairs)

            return charts
    except:
        None

# ##Call Back for 4 Columns
@app.callback(
                Output('dropdown-values4', 'children'),
                [
                Input('submit_button', 'n_clicks'),
                Input('choosen_columns_data', 'value'),
                Input('complete-df', 'data'),
                ],
                [
                State('mydropdown-1', 'className'),
                State('mydropdown-1', 'value'),
                State('mydropdown-2', 'className'),
                State('mydropdown-2', 'value'),
                State('mydropdown-3', 'className'),
                State('mydropdown-3', 'value'),
                State('mydropdown-4', 'className'),
                State('mydropdown-4', 'value'),
                ]
            )

def update_columns4(n_clicks, ddvalues,
                    dfdata,
                    dd1class, dd1value,
                    dd2class, dd2value,
                    dd3class, dd3value,
                    dd4class, dd4value,
                    ):

    try:
        if n_clicks < 1:
            print("no drop down values")
            return []

        else:

            list1 = []
            list2 = []
            
            list1.append(dd1class)
            list1.append(dd2class)
            list1.append(dd3class)
            list1.append(dd4class)

            list2.append(dd1value)
            list2.append(dd2value)
            list2.append(dd3value)
            list2.append(dd4value)

            zipped = zip(list1, list2)
            d = dict(zipped)

            finalpairs = decision_func(d)

            df = pd.read_json(dfdata)

            charts = graph_maker(df,finalpairs)

            print('4 columns')
            
            return charts

    except:
        None

# ##Call Back for 3 Columns
@app.callback(
                Output('dropdown-values3', 'children'),
                [
                Input('submit_button', 'n_clicks'),
                Input('choosen_columns_data', 'value'),
                Input('complete-df', 'data'),
                ],
                [
                State('mydropdown-1', 'className'),
                State('mydropdown-1', 'value'),
                State('mydropdown-2', 'className'),
                State('mydropdown-2', 'value'),
                State('mydropdown-3', 'className'),
                State('mydropdown-3', 'value'),
                ]
            )

def update_columns3(n_clicks, ddvalues,
                    dfdata, 
                    dd1class, dd1value,
                    dd2class, dd2value,
                    dd3class, dd3value,
                    ):

    try:
        if n_clicks < 1:
            print("no drop down values")
            return []

        else:

            list1 = []
            list2 = []
            
            list1.append(dd1class)
            list1.append(dd2class)
            list1.append(dd3class)

            list2.append(dd1value)
            list2.append(dd2value)
            list2.append(dd3value)

            zipped = zip(list1, list2)
            d = dict(zipped)

            finalpairs = decision_func(d)

            df = pd.read_json(dfdata)

            charts = graph_maker(df,finalpairs)

            print('3 columns')

            return charts

    except:
        None

# ##Call Back for 2 Columns
@app.callback(
                Output('dropdown-values2', 'children'),
                [
                Input('submit_button', 'n_clicks'),
                Input('choosen_columns_data', 'value'),
                Input('complete-df', 'data'),
                ],
                [
                State('mydropdown-1', 'className'),
                State('mydropdown-1', 'value'),
                State('mydropdown-2', 'className'),
                State('mydropdown-2', 'value'),
                ]
            )

def update_columns2(n_clicks, ddvalues,
                    dfdata, 
                    dd1class, dd1value,
                    dd2class, dd2value,                    
                    ):

    try:
        if n_clicks < 1:
            print("no drop down values")
            return []

        else:

            list1 = []
            list2 = []
            
            list1.append(dd1class)
            list1.append(dd2class)

            list2.append(dd1value)
            list2.append(dd2value)

            zipped = zip(list1, list2)
            d = dict(zipped)

            finalpairs = decision_func(d)

            df = pd.read_json(dfdata)

            charts = graph_maker(df,finalpairs)

            print('----------------')
            print('2 Columns')
            print('----------------')

            return charts

    except:
        None


#feedback button1
@app.callback(
                Output('auto-graph-radio1-output', 'children'),
                [
                Input('auto-graph-radio1', 'value')
                ]
            )

def radio_output1(
                radiovalue
                ):

    feedback_func(radiovalue)


#feedback button2
@app.callback(
                Output('auto-graph-radio2-output', 'children'),
                [
                Input('auto-graph-radio2', 'value')
                ]
            )

def radio_output2(
                radiovalue
                ):

    feedback_func(radiovalue)

#feedback button3
@app.callback(
                Output('auto-graph-radio3-output', 'children'),
                [
                Input('auto-graph-radio3', 'value')
                ]
            )

def radio_output3(
                radiovalue
                ):

    feedback_func(radiovalue)

#feedback button4
@app.callback(
                Output('auto-graph-radio4-output', 'children'),
                [
                Input('auto-graph-radio4', 'value')
                ]
            )

def radio_output4(
                radiovalue
                ):

    feedback_func(radiovalue)


#feedback button5
@app.callback(
                Output('auto-graph-radio5-output', 'children'),
                [
                Input('auto-graph-radio5', 'value')
                ]
            )

def radio_output5(
                radiovalue
                ):

    feedback_func(radiovalue)


#feedback button6
@app.callback(
                Output('auto-graph-radio6-output', 'children'),
                [
                Input('auto-graph-radio6', 'value')
                ]
            )

def radio_output6(
                radiovalue
                ):

    feedback_func(radiovalue)

#feedback button7
@app.callback(
                Output('auto-graph-radio7-output', 'children'),
                [
                Input('auto-graph-radio7', 'value')
                ]
            )

def radio_output7(
                radiovalue
                ):

    feedback_func(radiovalue)


#feedback button8
@app.callback(
                Output('auto-graph-radio8-output', 'children'),
                [
                Input('auto-graph-radio8', 'value')
                ]
            )

def radio_output8(
                radiovalue
                ):

    feedback_func(radiovalue)


#feedback button9
@app.callback(
                Output('auto-graph-radio9-output', 'children'),
                [
                Input('auto-graph-radio9', 'value')
                ]
            )

def radio_output9(
                radiovalue
                ):

    feedback_func(radiovalue)



#feedback button10
@app.callback(
                Output('auto-graph-radio10-output', 'children'),
                [
                Input('auto-graph-radio10', 'value')
                ]
            )

def radio_output10(
                radiovalue
                ):

    feedback_func(radiovalue)



#feedback button11
@app.callback(
                Output('auto-graph-radio11-output', 'children'),
                [
                Input('auto-graph-radio11', 'value')
                ]
            )

def radio_output11(
                radiovalue
                ):

    feedback_func(radiovalue)



#feedback button12
@app.callback(
                Output('auto-graph-radio12-output', 'children'),
                [
                Input('auto-graph-radio12', 'value')
                ]
            )

def radio_output12(
                radiovalue
                ):

    feedback_func(radiovalue)



    #feedback button13
@app.callback(
                Output('auto-graph-radio13-output', 'children'),
                [
                Input('auto-graph-radio13', 'value')
                ]
            )

def radio_output13(
                radiovalue
                ):

    feedback_func(radiovalue)


#feedback button14
@app.callback(
                Output('auto-graph-radio14-output', 'children'),
                [
                Input('auto-graph-radio14', 'value')
                ]
            )

def radio_output14(
                radiovalue
                ):

    feedback_func(radiovalue)


#feedback button15
@app.callback(
                Output('auto-graph-radio15-output', 'children'),
                [
                Input('auto-graph-radio15', 'value')
                ]
            )

def radio_output15(
                radiovalue
                ):

    feedback_func(radiovalue)


#feedback button16
@app.callback(
                Output('auto-graph-radio16-output', 'children'),
                [
                Input('auto-graph-radio16', 'value')
                ]
            )

def radio_output16(
                radiovalue
                ):

    feedback_func(radiovalue)