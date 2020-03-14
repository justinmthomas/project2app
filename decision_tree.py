
from sklearn import tree
import pandas as pd


def decision(chart_type):
    url="https://gwprojectflask.herokuapp.com/api/data/all_raw_results"
    df = pd.read_json(url)


    df_data=df[['Data_Type','Correct']]
    df_target=df['Chart_Type']
    df_target.unique()
  

    df_data_dummies = pd.get_dummies(df_data)
   


    data_names = ['Number Correct','Mapping','DimensionVsMeasure','Comparison','Dimension(Location)VsMeasure','Dimension(Time)VsMeasure','MeasureVsMeasure']
    target_names = df_target.unique()


    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(df_data_dummies, df_target)

    prediction = clf.predict([chart_type])

    print(prediction)

    return prediction

