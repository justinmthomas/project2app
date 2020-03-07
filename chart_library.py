import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px

df = pd.read_csv(r"C:\Users\Aaron\Documents\GW_Data_Course\AIsaacson_GW_HW\GW_Project2\sources\Quiz_results_29FEB_noon.csv")
df.head()

a=df['Data_Type']
c=df['Chart_Type']
b=df['Correct']

def bar_function(x,y): 

    aggs = ["count","sum","avg","median","mode","rms","stddev","min","max","first","last"]

    agg = []
    agg_func = []
    for i in range(0, len(aggs)):
        agg = dict(
            args=['transforms[0].aggregations[0].func', aggs[i],
            'transforms[0].aggregations[1].func', aggs[i]],
            label=aggs[i],
            method='restyle'
        )
        agg_func.append(agg)

    return{
    'data' : [dict(
        type = 'bar',
        x = x,
        y = y,
        text = y,
        textposition='outside',
        transforms = [dict(
            type = 'aggregate',
            groups = x,
            aggregations = [
                dict(
                target = 'y', func = 'sum', enabled = True),
                dict(
                target = 'text', func = 'count', enabled = True),
                ]),
            # dict(
            # type = 'aggregate',
            # groups = x,
            # aggregations = [
            #     dict(
            #     target = 'text', func = 'count', enabled = True),
            #     ]
            # )
            ]

        )],

    'layout' : dict(
        title = '<b>Plotly Aggregations</b><br>use dropdown to change aggregation',
        xaxis = dict(title = x.name),
        yaxis = dict(title = y.name),
        updatemenus = [dict(
                yanchor = 'top',
                active = 1,
                showactive = False,
                buttons = agg_func
            )]
        )
    }


def line_function(x,y): 

    aggs = ["count","sum","avg","median","mode","rms","stddev","min","max","first","last"]

    agg = []
    agg_func = []
    for i in range(0, len(aggs)):
        agg = dict(
            args=['transforms[0].aggregations[0].func', aggs[i]],
            label=aggs[i],
            method='restyle'
        )
        agg_func.append(agg)


    return{
    'data' : [dict(
        type = 'line',
        x = x,
        y = y,
        text = y,
        textposition='auto',
        transforms = [dict(
            type = 'aggregate',
            groups = x,
            aggregations = [
                dict(
                target = 'y', func = 'sum', enabled = True),
                # dict(
                # target = 'text', func = 'sum', enabled = True)
                ]
            )]
        )],

    'layout' : dict(
        title = '<b>Plotly Aggregations</b><br>use dropdown to change aggregation',
        xaxis = dict(title = 'Column A Header'),
        yaxis = dict(title = 'Column B Header'),
        updatemenus = [dict(
                yanchor = 'top',
                active = 1,
                showactive = False,
                buttons = agg_func
            )]
        )
    }




def pie_function(x,y): 

    aggs = ["count","sum","avg","median","mode","rms","stddev","min","max","first","last"]

    agg = []
    agg_func = []
    for i in range(0, len(aggs)):
        agg = dict(
            args=['transforms[0].aggregations[0].func', aggs[i]],
            label=aggs[i],
            method='restyle'
        )
        agg_func.append(agg)
        
    return{
        'data' : [dict(
            type = 'pie',
            labels = x,
            values = y,
            text = x,
            textposition='auto',
            transforms = [dict(
                type = 'aggregate',
                groups = x,
                aggregations = [
                    dict(
                    target = 'values', func = 'sum', enabled = True),
                    ]
                )]
            )],

        'layout' : dict(
            title = f"<b>{x.name} by Number {y.name}</b><br>use dropdown to change aggregation",
            updatemenus = [dict(
                    yanchor = 'top',
                    active = 1,
                    showactive = False,
                    buttons = agg_func
                )]
            )
        }