#!/usr/bin/env python
# coding: utf-8

# In[1]:


#pip install flask-cors


# In[2]:


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
from config import remote_db_endpoint, remote_db_port
from config import remote_gwsis_dbname, remote_gwsis_dbuser, remote_gwsis_dbpwd


# In[8]:


#Create Cloud DB Connection. 
engine = create_engine(f"mysql+pymysql://{remote_gwsis_dbuser}:{remote_gwsis_dbpwd}@{remote_db_endpoint}:{remote_db_port}/{remote_gwsis_dbname}")


# In[9]:



# Create remote DB connection.
conn = engine.connect()   


# In[10]:


app = Flask(__name__)
CORS(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = ""

#db = SQLAlchemy(app)


# In[ ]:





# In[ ]:





# In[ ]:



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

#     for key, value in content.items():
#         setattr(survey_results, key, value) 


app.run(host='127.0.0.1', port= 5000)


# In[ ]:





# In[ ]:





# In[ ]:


parsed = json.loads(content)
print json.dumps(parsed, indent=4, sort_keys=True)


# In[ ]:



# def update_survey():
#     orders_entries = []
#     for orders in data["all_orders"]:
#         new_entry = SalesOrders(order_id=orders['id'],
#                                 order_number=orders['number'])
#         orders_entries.append(new_entry)
#     db.session.add_all(orders_entries)
#     db.session.commit()


# if __name__ == "__main__":
#     app.run(debug=True)


# In[ ]:


# @app.route("/send", methods=["GET", "POST"])
# def send():
#     if request.method == "POST":
#         nickname = request.form["nickname"]
#         age = request.form["age"]
#         pet = Pet(nickname=nickname, age=age)
#         db.session.add(pet)
#         db.session.commit()

#         return "Thanks for the form data!"

#     return render_template("form.html")

