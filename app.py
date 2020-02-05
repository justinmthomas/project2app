#!/usr/bin/env python
# coding: utf-8

# In[1]:


#pip install flask-cors


# In[2]:

import os
import pandas as pd
import sqlalchemy
import pymysql
import sys
from pandas.io.json import json_normalize
pymysql.install_as_MySQLdb()


# In[3]:



from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


# In[4]:


from flask import (
    Flask,
    render_template,
    jsonify,
    request)


# In[5]:


from flask_cors import CORS


# In[6]:


from sqlalchemy import create_engine


# In[7]:


#Keep config file for our info. 
remote_db_endpoint = os.environ.get('remote_db_endpoint')
remote_db_port = os.environ.get('remote_db_port')
remote_gwsis_dbname = os.environ.get('remote_gwsis_dbname')
remote_gwsis_dbpwd = os.environ.get('remote_gwsis_dbpwd')
remote_gwsis_dbuser = os.environ.get('remote_gwsis_dbuser')


#from config import remote_db_endpoint, remote_db_port
#from config import remote_gwsis_dbname, remote_gwsis_dbuser, remote_gwsis_dbpwd


# In[8]:


#Create Cloud DB Connection. 
engine = create_engine(f"mysql+pymysql://{remote_gwsis_dbuser}:{remote_gwsis_dbpwd}@{remote_db_endpoint}:{remote_db_port}/{remote_gwsis_dbname}")


# In[9]:



# Create remote DB connection.
conn = engine.connect()   


# In[10]:


app = Flask(__name__)
CORS(app)



@app.route('/postjson', methods = ['POST'])
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

@app.route("/datavisualization")
def resultsAnalysis():
    """Return the Results analysis page."""
    return render_template("What_Are_Data_Visualizations.html")

@app.route("/quizexplained")
def quizExplained():
    """Return the Results analysis page."""
    return render_template("Quiz_Explained.html")

@app.route("/visualquiz")
def visualQuiz():
    """Return the Results analysis page."""
    return render_template("Visual_Quiz.html")


@app.route("/api/data/results", methods=["GET", "POST"])
def getSurveyResults():
    surveyResults = pd.read_sql(
        "SELECT value as QuestionNo, SUM(correct) AS NumCorrect, COUNT(*) AS NumAttempted, SUM(correct)/COUNT(*) AS PctCorrect FROM survey_results GROUP BY value", conn)

    return surveyResults.to_json(orient='records')

@app.route("/api/data/newresults", methods=["GET", "POST"])
def getNewSurveyResults():
    newResults = pd.read_sql(
        "SELECT COUNT(Distinct Survey_ID) AS numberOFattempts, COUNT(Value) AS questionsAnswered, (SUM(correct) / COUNT(*)) * 100 AS pctCorrect, SUM(correct) AS numCorrect, SUM(correct != 1) as numIncorrect FROM survey_results.survey_results", conn)
    return newResults.to_json(orient='records')


@app.route("/api/data/resultsavg", methods=["GET", "POST"])
def getAvgSurveyResults():
    avgResults = pd.read_sql(
        "select value as Question_Num, Data_Type, Chart_Type, sum(Correct) AS numCorrect, (sum(Correct) / (COUNT(Distinct Survey_ID))) * 100 As percent_correct from survey_results.survey_results group by value", conn)
    return avgResults.to_json(orient='records')



#app.run(host='127.0.0.1', port)




