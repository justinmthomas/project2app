import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px


def bar_function(x,y): 

    aggs = ["count","sum","avg","median","mode","rms","stddev","min","max","first","last"]

    agg = []
    agg_func = []
    for i in range(0, len(aggs)):
        agg = dict(
            args=[{'transforms[0].aggregations[0].func': aggs[i],
            'transforms[0].aggregations[1].func': aggs[i]}],
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
        hoverinfo='text',
        transforms = [dict(
            type = 'aggregate',
            groups = x,
            aggregations = [
                dict(
                target = 'y', func = 'sum', enabled = True),
                dict(
                target = 'text', func = 'sum', enabled = True),
                ]),
            ]

        )],

    'layout' : dict(
        title = f'<b>{x.name} vs {y.name}</b><br>use dropdown to change aggregation',
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
            args=[{'transforms[0].aggregations[0].func': aggs[i],
            'transforms[0].aggregations[1].func': aggs[i]}],
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
        hoverinfo='text',
        transforms = [dict(
            type = 'aggregate',
            groups = x,
            aggregations = [
                dict(
                target = 'y', func = 'sum', enabled = True),
                dict(
                target = 'text', func = 'sum', enabled = True)
                ]
            )]
        )],

    'layout' : dict(
        title = f'<b>{x.name} vs {y.name}</b><br>use dropdown to change aggregation',
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
            args=[{'transforms[0].aggregations[0].func': aggs[i],
            'transforms[0].aggregations[1].func': aggs[i]}],
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
            hoverinfo='text',
            transforms = [dict(
                type = 'aggregate',
                groups = x,
                aggregations = [
                dict(
                target = 'y', func = 'sum', enabled = True),
                dict(
                target = 'text', func = 'sum', enabled = True),
                ]),
                ]
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



def scatter_function(x,y): 
    return px.scatter (
        x = x,
        y = y)




def bubble_function (x,y):
    # g=pd.Series(y)
    # t=pd.cut(y, bins=6).max()
    # print (t)
    categories, edges = pd.cut(y, 6, retbins=True, duplicates='drop', labels=False)
    df = pd.DataFrame({'original':y,
                'bin_max': edges[1:][categories]},
                columns = ['original', 'bin_max'])
    s = df['bin_max'].unique()

    return px.scatter(
        x=x,
        y=y,
        size=y
        # color=[0, 1, 2, 3]
    )            


def map_function (x,y,z):
    
    scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

    data = [ dict(
            type = 'scattergeo',
            # locationmode = 'USA-states',
            lon = y,
            lat = z,
            text = x,
            mode = 'markers',
            marker = dict(
                size = 8,
                opacity = 0.8,
                reversescale = True,
                autocolorscale = False,
                # symbol = 'square',
                line = dict(
                    width=1,
                    color='rgba(102, 102, 102)'
                ),
                colorscale = scl,
                cmin = 0,
                # color = df['cnt'],
                # cmax = df['cnt'].max(),
                colorbar=dict(
                    title="your map"
                )
            ))]

    layout = dict(
            title = 'Map',
            colorbar = True,
            # geo = dict(
            #     scope='usa',
            #     projection=dict( type='albers usa' ),
            #     showland = True,
            #     landcolor = "rgb(250, 250, 250)",
            #     subunitcolor = "rgb(217, 217, 217)",
            #     countrycolor = "rgb(217, 217, 217)",
            #     countrywidth = 0.5,
            #     subunitwidth = 0.5
            )
        # )

    fig = dict( data=data, layout=layout )  

    return fig

def chart_function (x,df):
    
    return dash_table.DataTable(
        id= 'table',
        columns=[{'name': i, 'id': i} for i in df],
        data=df.to_dict('rows')
        )