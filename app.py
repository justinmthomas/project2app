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
#app = flask.Flask(__name__)
#CORS(app)

server = flask.Flask(__name__)
CORS(server)
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
        "SELECT * FROM survey_results where value!='feedbk'", conn)

    return surveyResults.to_json(orient='records')

# app route to access all results 
@server.route("/api/data/all_raw_results", methods=["GET", "POST"])
def getAllRaw_SurveyResults():
    allsurveyResults = pd.read_sql(
        "SELECT * FROM survey_results", conn)

    return allsurveyResults.to_json(orient='records')

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