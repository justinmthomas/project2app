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
import flask
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#Importing additional elemtns for S3 self signed URL generation
from flask import Flask, render_template, request, redirect, url_for

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
from sqlalchemy import create_engine


#Keep config file for our info. 
remote_db_endpoint = os.environ.get('remote_db_endpoint')
remote_db_port = os.environ.get('remote_db_port')
remote_gwsis_dbname = os.environ.get('remote_gwsis_dbname')
remote_gwsis_dbpwd = os.environ.get('remote_gwsis_dbpwd')
remote_gwsis_dbuser = os.environ.get('remote_gwsis_dbuser')


#from config import remote_db_endpoint, remote_db_port
#from config import remote_gwsis_dbname, remote_gwsis_dbuser, remote_gwsis_dbpwd


#Create Cloud DB Connection. 
engine = create_engine(f"mysql+pymysql://{remote_gwsis_dbuser}:{remote_gwsis_dbpwd}@{remote_db_endpoint}:{remote_db_port}/{remote_gwsis_dbname}")

# Create remote DB connection.
conn = engine.connect()
app = flask.Flask(__name__)
CORS(app)

server = flask.Flask(__name__)

@server.route('/')
def index():
    return 'Hello Flask app'


@server.route('/postjson', methods = ['POST'])
def postJsonHandler():
    print (request.is_json)
    # read in JSON from POST requuest into content 
    content = request.get_json()
    print(content)
        
    #extract Survey ID from first entry in JSON "Survey ID"
    survey_id = (content["Survey_ID"])
    print(survey_id)
        
    ## Create Survey Dataframe form "result" entry in JSON
    survey_df = pd.DataFrame(content["result"])
   
    #set column names of dataframe
   
    survey_df.insert(0, "Survey_ID", 'null')
    survey_df["Survey_ID"] = survey_id
    survey_df.columns = ["Survey_ID", "value", "Data_Type", "Chart_Type", "Correct"]
    print (survey_df)
       
    #[print(key, value) for key, value in content.items()] 
  
    #write surve.df to SQL 
    survey_df.to_sql(con=conn, name='survey_results', if_exists='append', index=False)
    #session.commit()
    return jsonify(content)

@server.route("/datavisualization")
def resultsAnalysis():
    """Return the Results analysis page."""
    return render_template("What_Are_Data_Visualizations.html")

@server.route("/quizexplained")
def quizExplained():
    """Return the Results analysis page."""
    return render_template("Quiz_Explained.html")

@server.route("/visualquiz")
def visualQuiz():
    """Return the Results analysis page."""
    return render_template("Visual_Quiz.html")


@server.route("/api/data/results", methods=["GET", "POST"])
def getSurveyResults():
    surveyResults = pd.read_sql(
        "SELECT value as QuestionNo, SUM(correct) AS NumCorrect, COUNT(*) AS NumAttempted, SUM(correct)/COUNT(*) AS PctCorrect FROM survey_results GROUP BY value", conn)

    return surveyResults.to_json(orient='records')

# app route to access all survey results 
@server.route("/api/data/raw_results", methods=["GET", "POST"])
def getRaw_SurveyResults():
    surveyResults = pd.read_sql(
        "SELECT * FROM survey_results", conn)

    return surveyResults.to_json(orient='records')

@server.route("/api/data/newresults", methods=["GET", "POST"])
def getNewSurveyResults():
    newResults = pd.read_sql(
        "SELECT COUNT(Distinct Survey_ID) AS numberOFattempts, COUNT(Value) AS questionsAnswered, (SUM(correct) / COUNT(*)) * 100 AS pctCorrect, SUM(correct) AS numCorrect, SUM(correct != 1) as numIncorrect,  SUM(correct)/COUNT(Distinct Survey_ID) AS avgScore FROM survey_results.survey_results", conn)
    return newResults.to_json(orient='records')


@server.route("/api/data/resultsavg", methods=["GET", "POST"])
def getAvgSurveyResults():
    avgResults = pd.read_sql(
        "select value as Question_Num, Data_Type, Chart_Type, sum(Correct) AS numCorrect, (sum(Correct) / (COUNT(Distinct Survey_ID))) * 100 As percent_correct from survey_results.survey_results group by value", conn)
    return avgResults.to_json(orient='records')

@server.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        #if 'file' not in request.files:
          #  flash('No file part')
           # return redirect(request.url)
     file = request.files['file']
    # look at the first ten thousand bytes to guess the character encoding
     
    result = chardet.detect(file.read(10000))
     # check what the character encoding might be
    print(result)
    print(result['encoding'])
    file_df = pd.read_csv(file,encoding=result['encoding'])
    print(file_df)

@server.route('/headers', methods=['GET'])
def print_headers():
    headers = list(file.df)
    return headers

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,server=server,
    routes_pathname_prefix='/dash/')


app.config['suppress_callback_exceptions'] = True

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

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
    html.Ul(id="complete-upload"),

    html.Br(),
    html.Button(
        id='propagate-button',
        n_clicks=0,
        children='Load Columns'
    ),
    html.Br(),
    html.Label('Select columns to graph:'),
    html.Br(),
    dcc.Checklist(id='output-column-upload',
                    # n_clicks=0,
                    labelStyle = dict(display='inline')),

    # dcc.Graph(id='Mygraph'),
    # html.Div(id='output-data-upload')

    html.Div(id='display-selected-values')

    # html.Div(id='output-reserve', style={'display': 'none'}),
    # html.Div(id='datatable-interactivity-container')
    ])


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

@app.callback(

                Output('output-column-upload', 'options'),

                # Output('output-data-upload', 'children'),

#             [
#                 Output('output-data-upload', 'children'),
#                 Output('output-column-selected', 'selected_columns')
#             ],

#             # [
#             #     Output('output-data-upload', 'children'),
#             #     Output('output-column-upload', 'options')
#             #     ],
            [
                Input('propagate-button', 'n_clicks'),
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ],
                # State('upload_data', 'last_modified')
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

@app.callback(
                Output('complete-upload', 'children'),

                [Input('upload-data', 'filename')]
            )

def upload_complete(filename):

    filename = filename

    if filename is None:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(filename) for filename in filename]


@app.callback(
    Output('display-selected-values', 'children'),
    [Input('output-column-upload', 'value')]
    )
def set_display_children(selected_column):
    return u'{} is the column you selected'.format(
        selected_column
    )

# def update_table(contents, filename):
#     table = html.Div()

#     if contents:
#         contents = contents[0]
#         filename = filename[0]
#         df = parse_data(contents, filename)
#         column_head = [{'label': i, 'value': i} for i in df.columns]

#         table = html.Div([
#             html.H5('Select columns to graph:'),
#             dcc.Checklist(options=column_head,
#             labelStyle = dict(display='inline')),
#             html.H5(filename),
#             dash_table.DataTable(
#                 id='user_data',
#                 data=df.to_dict('rows'),
#                 columns=[{'name': i, 'id': i, "selectable": True} for i in df.columns],
#                 fixed_rows={ 'headers': True, 'data': 0 },
#                 column_selectable = 'multi',
#                 selected_columns=[],
#                 # filter_action="native",
#                 sort_action="native",
#                 sort_mode="multi",
#                 page_action="native",
#                 page_size= 20,
#                 style_table={
#                     'maxHeight': '500px',
#                     # 'overflowY': 'scroll',
#                     'overflowX': 'scroll',
#                 },
#                 style_cell_conditional=create_conditional_style(df)
#             ),
#         ])
#         # print(table)
#         column_head = [{'label': i, 'value': i} for i in df.columns]
#     # return table, column_head
#         # app.layout = serve_layout
#     return table

def create_conditional_style(df):
    style=[]
    for col in df.columns:
        name_length = len(col)
        pixel = 50 + round(name_length*1)
        pixel = str(pixel) + "px"
        style.append({'if': {'column_id': col}, 'minWidth': pixel})

    return style


# @app.callback(
#                 Output('output-reserve', 'id'),
#                 Input('user_data', 'n_clicks')
#             )

# def serve_layout():
#     layout = [html.Div(id='output-data-upload'),
#             html.Div(id='output-column-selected', style={'display': 'none'})]
    
#     return layout

# app.layout = serve_layout

# @app.callback(
#                 Output('output-data-upload', 'id'),
#                 [Input('user_data', 'n_clicks')]
#             )
# def set_checks_value(available_options):
#     print('hi')
#     print(available_options)
#     #return available_options[0]['value']
#     return available_options

# @app.callback(
#                 Output('output-column-upload', 'options')
#                 ,
#                 Input('output-data-upload', 'children')
#             )
# def set_checks_value(available_options):
#     return available_options[0]['value']


# @app.callback(
#     Output('datatable-interactivity-container', "children"),
#     [Input('user_data', 'selected_columns'),
#      Input('output-data-upload', "derived_virtual_selected_columns")])
# def update_graphs(columns, derived_virtual_selected_columns):
#     # When the table is first rendered, `derived_virtual_data` and
#     # `derived_virtual_selected_rows` will be `None`. This is due to an
#     # idiosyncracy in Dash (unsupplied properties are always None and Dash
#     # calls the dependent callbacks when the component is first rendered).
#     # So, if `rows` is `None`, then the component was just rendered
#     # and its value will be the same as the component's dataframe.
#     # Instead of setting `None` in here, you could also set
#     # `derived_virtual_data=df.to_rows('dict')` when you initialize
#     # the component.
#     if derived_virtual_selected_columns is None:
#         derived_virtual_selected_columns = []

#     dff = df if columns is None else pd.DataFrame(columns)

#     colors = ['#7FDBFF' if i in derived_virtual_selected_columns else '#0074D9'
#               for i in range(len(dff))]

#     return [
#         dcc.Graph(
#             id=column,
#             figure={
#                 "data": [
#                     {
#                         "x": dff["Chart_Type"],
#                         "y": dff[column],
#                         "type": "bar",
#                         "marker": {"color": colors},
#                     }
#                 ],
#                 "layout": {
#                     "xaxis": {"automargin": True},
#                     "yaxis": {
#                         "automargin": True,
#                         "title": {"text": column}
#                     },
#                     "height": 250,
#                     "margin": {"t": 10, "l": 10, "r": 10},
#                 },
#             },
#         )
#         # check if column exists - user may have deleted it
# #         # If `column.deletable=False`, then you don't
# #         # need to do this check.
# #     #     for column in ["pop", "lifeExp", "gdpPercap"] if column in dff
#     ]




#app.run(host='127.0.0.1', port)




