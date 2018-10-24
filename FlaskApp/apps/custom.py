import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from collections import deque
import plotly.graph_objs as go
import psycopg2
import pandas as pd
from dash.dependencies import Output, Event, Input, State
import dash_table_experiments as dt
#Switch these two when putting live
#Live Code
import urllib.parse
#Testing Code
#import urllib
import sys


from ..base.basescript import app, server









###############################################################################
## Setup Code
###############################################################################



##function for colors
def color_col(x):
    if x in ["yes", "Working"]:
        return "rgb(0,255,0)"
    if x in ["no", "Not Working"]:
        return "rgb(255,0,0)"
    if x == "unknown":
        return "rgb(255, 153, 51)"

## Function to generate datatables
def generate_table(dataframe):
    return dt.DataTable(
        id='filter-table',
        rows=dataframe.to_dict('records'),

        # optional - sets the order of columns
        columns=dataframe.columns,

        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
    )


## Connect and pull initial df
conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
query = "SELECT country_name, district, sub_district, current_status_text, fuzzy_water_source, fuzzy_water_tech,  today_preds_text, one_year_preds_text, one_km_population, one_km_functioning_water_points, impact_text, management, lat_deg, lon_deg, map_lat, map_lon from final_all WHERE country_name = 'Kenya'"
df_init = pd.read_sql_query(query, conn)
df_init["color"] = df_init["today_preds_text"].apply(color_col)
### Can probably clean this part up
df_init2 = df_init.copy()
df2_init = df_init2.drop(['color', 'lat_deg', 'lon_deg', 'map_lat', 'map_lon', 'management'], axis=1, inplace= True)
df_init2.columns =['Country', 'District', 'Subdistrict', 'Last Known Status', 'Water Source', 'Water Tech', 'Predicted Status: Today',
    'Predicted Status: 1 Year', 'Pop. within 1km', 'Func. Water Points within 1km', 'Impact Level']
conn.close()
mapbox_access_token = 'pk.eyJ1IjoiZHdhdHNvbjgyOCIsImEiOiJjamVycHp0b3cxY2dyMnhsdGc4eHBkcW85In0.uGPxMK4_u-nAs_J74yw70A'

## pull in full menu table for filters
## The menu table is built in the db pulling all distinct combinations that could be made in dropdowns
conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
q2 = "SELECT * FROM menu_table"
df2 = pd.read_sql_query(q2, conn)
conn.close()


###############################################################################
## App Structure
###############################################################################



layout = html.Div([
    # Column: Title + Map
        # Row: Title
        
        html.Div([
        html.A("Switch to easy filtering", href ="/easy" ),
        # Row: Map
        html.Div([
        dcc.Dropdown(className = "dropdown", id = 'country-select',
            options=[
            {'label': i, 'value': i} for i in df2.country_name.sort_values().unique()],
             #value = df2.country_name."sort_values().unique()[0], 
            placeholder = "Select a Country",
            value = "Kenya"      
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(className = "dropdown", id = 'district-select',
            options=[
            {'label': i, 'value': i} for i in df2.district.sort_values().unique()],
            placeholder = "Select a District",
            multi = True     
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'sub-district-select',
            options = [
            {'label': i, 'value': i} for i in df2.sub_district.sort_values().unique()],
            placeholder = 'Select a Sub-District',
            multi = True
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'status-select',
            options = [
            {'label': i, 'value': i} for i in df2.current_status_text.sort_values().unique()],
            placeholder = "Last Known Status",
            multi = True
        ),
        ], style = {"padding":"5px"}),
        #fix to update only to available
        html.Div([
        dcc.Dropdown(id = 'watersource-select',
            options=[
             {'label': i, 'value': i} for i in df2.fuzzy_water_source.sort_values().unique()],
             #value = df_init.fuzzy_water_source.sort_values().unique()[0:2], 
             placeholder = "Select a Water Source",
             multi= True       
        ),
        ], style = {"padding":"5px"}),
        #fix to update only to available
        html.Div([
        dcc.Dropdown(id = 'watertech-select',
            options=[
             {'label': i, 'value': i} for i in df2.fuzzy_water_tech.sort_values().unique()],
             #value = df_init.fuzzy_water_tech.sort_values().unique()[0:2], 
             placeholder = "Select a Water Tech",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        #Fix to update only to available
        html.Div([
        dcc.Dropdown(id = 'management-select',
            options=[
             {'label': i, 'value': i} for i in df2.management.sort_values().unique()],
             #value =  df_init.management.sort_values().unique()[0:2],
             placeholder = "Select Water Point Management",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'today-pred-select',
            options=[
             {'label': i, 'value': i} for i in df2.today_preds_text.sort_values().unique()],
             placeholder = "Select Today's Prediction",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'one-year-pred-select',
            options=[
             {'label': i, 'value': i} for i in df2.one_year_preds_text.sort_values().unique()],
             placeholder = "Select One Year Prediction",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'three-year-pred-select',
            options=[
             {'label': i, 'value': i} for i in df2.three_year_preds_text.sort_values().unique()],
             placeholder = "Select Three Year Prediction",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'five-year-pred-select',
            options=[
             {'label': i, 'value': i} for i in df2.five_year_preds_text.sort_values().unique()],
             placeholder = "Select Five Year Prediction",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'impact-level-select',
            options=[
             {'label': i, 'value': i} for i in df2.impact_text.sort_values().unique()],
             placeholder = "Select Impact Level",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        html.H6(children = "Color Water Points By:"),
        dcc.Dropdown(id = 'point-color-select',
            options=[
                {'label': ' Last Known Status', 'value': 1},
                {'label': ' Today\'s Prediction', 'value': 2},
                {'label': ' One Year Prediction', 'value':3},
                {'label': 'Three Year Prediction', 'value':4},
                {'label': 'Five Year Prediction', 'value':5}
            ],
            value = 2,
            multi=False,
            #labelStyle={'display': 'block', 'font-size':'14px'}                   
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        html.Button('Submit', id= 'submit-button')
        ],
        style = {"padding":"5px"}),
        html.Div([
        html.H6(children = "", id = "well_text"),
        html.A('Download Data', id= 'download-link', download ="waterpoint_data.csv", href="", target= "_blank"),
        ]),
        ], className="col-md-4"),
    
    html.Div([
        dcc.Graph(id = "output-graph",
        config={
        'displayModeBar': False
        },
        figure ={"data": [
                {
                    "type": "scattermapbox",
                    "lat": df_init.lat_deg,
                    "lon": df_init.lon_deg,
                    "text": df_init.today_preds_text,
                    "cluster": True,
                    "mode": "markers",
                    "marker": {
                        "size": 8,
                        "opacity": 1.0,
                        "color" : df_init['color'] 
                    }
                }
            ],
        "layout": {
            "autosize": True,
            "margin" : dict(l = 0, r = 0, t = 20, b = 0),
            "hovermode": "closest",
            "mapbox": {
                "accesstoken": mapbox_access_token,
                "center": {
                    "lat": df_init.map_lat.mean(),
                    "lon": df_init.map_lon.mean()
                },
                "cluster": True,
                "pitch": 0,
                "zoom": 4,
                "style": "outdoors"
            }
        }
    })
    ], className="col-md-8", style = {'border':'1px solid black','height':'470px'}),
    
    html.Div([
        generate_table(df_init2)
        ], className="col-md-12", style = {"font-size":"small"}),

], className="container-fluid row")



###############################################################################
## Outputs and Callbacks
###############################################################################

###############################################################################
## Update map 
###############################################################################
@app.callback(Output('output-graph', 'figure'), [Input('submit-button', 'n_clicks')], state= [State('country-select', 'value'), State('status-select', 'value'), State('district-select', 'value'), State('sub-district-select', 'value'), State('watersource-select', 'value'), State('watertech-select', 'value'), State('management-select', 'value'), State('today-pred-select', 'value'), State('one-year-pred-select', 'value'), State('three-year-pred-select', 'value'), State('five-year-pred-select', 'value'), State('impact-level-select', 'value'), State('point-color-select', 'value')])
def run_query(submit_button,  country, status, district, sub_district, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text, point_color_select):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")

    base_query = "SELECT lat_deg, lon_deg, current_status_text, today_preds_text, one_year_preds_text, map_lat, map_lon from final_all WHERE country_name =" + "'" + str(country) + "'"

    if not status:
        pass
    else:
        base_query = base_query + " and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"


    df = pd.read_sql_query(base_query, conn)
    if point_color_select == 1:
        df["color"]= df["current_status_text"].apply(color_col)
    if point_color_select ==2:
        df["color"]=df["today_preds_text"].apply(color_col)
    if point_color_select ==3:
        df["color"] = df["one_year_preds_text"].apply(color_col)
    if point_color_select ==4:
        df["color"] = df["three_year_preds_text"].apply(color_col)
    if point_color_select ==5:
        df["color"] = df["five_year_preds_text"].apply(color_col)

    conn.close()
    mapbox_access_token = 'pk.eyJ1IjoiZHdhdHNvbjgyOCIsImEiOiJjamVycHp0b3cxY2dyMnhsdGc4eHBkcW85In0.uGPxMK4_u-nAs_J74yw70A'
    figure = { "data": [
                {
                    "type": "scattermapbox",
                    "lat": df.lat_deg,
                    "lon": df.lon_deg,
                    "text": df.today_preds_text,

                    "mode": "markers",
                    "marker": {
                        "size": 8,
                        "opacity": .8,
                        "color" : df['color']                        
                    }
                }
            ],
        "layout": {
            "autosize": True,
            "margin" : dict(l = 0, r = 0, t = 20, b = 0),
            "hovermode": "closest",
            "mapbox": {
                "accesstoken": mapbox_access_token,
                "center": {
                    "lat": df.map_lat.mean(),
                    "lon": df.map_lon.mean()
                },
                "pitch": 0,
                "zoom": 4,
                "style": "outdoors",
                "cluster": True,
            }
        }
    }
    return figure

    


###############################################################################
## Update Table- Not currently working correctly
###############################################################################
@app.callback(Output('filter-table', 'rows'), [Input('submit-button', 'n_clicks')], state= [State('country-select', 'value'), State('status-select', 'value'), State('district-select', 'value'), State('sub-district-select', 'value'), State('watersource-select', 'value'), State('watertech-select', 'value'), State('management-select', 'value'), State('today-pred-select', 'value'), State('one-year-pred-select', 'value'), State('three-year-pred-select', 'value'), State('five-year-pred-select', 'value'), State('impact-level-select', 'value')])
def run_query(submit_button, country, status, district, sub_district, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    


    base_query = "SELECT country_name, district, sub_district, current_status_text, fuzzy_water_source, fuzzy_water_tech, today_preds_text, one_year_preds_text, one_km_population, one_km_functioning_water_points, impact_text, management, lat_deg, lon_deg FROM final_all WHERE country_name =" + "'" + str(country) + "'"

    if not status:
        pass
    else:
        base_query = base_query + " and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    df.drop(['management', 'lat_deg', 'lon_deg'], axis = 1, inplace= True)
    df.columns = ['Country', 'District', 'Subdistrict', 'Last Known Status', 'Water Source', 'Water Tech', 'Predicted Status: Today',
    'Predicted Status: 1 Year', 'Pop. within 1km', 'Func. Water Points within 1km', 'Impact Level']
    conn.close()

    return df.to_dict('records')


## Update well_text for number of water points
@app.callback(Output("well_text", 'children'), [Input('filter-table', 'rows')])
def update_well_text(rows):
    return "Filters matched {} results".format(str(len(rows)))



###############################################################################
##update districts menu
###############################################################################
@app.callback(Output('district-select', 'options'), [Input('country-select', 'value'), Input('sub-district-select', 'value'),
    Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_district(country, sub_district, status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT district from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not status:
        pass
    else:
        base_query = base_query + " and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.district.sort_values().unique()]


###############################################################################
##update subdistricts menu
###############################################################################

@app.callback(Output('sub-district-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value'),  Input('impact-level-select', 'value')])
def update_subdistrict(country, district, status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT sub_district from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not status:
        pass
    else:
        base_query = base_query + " and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.sub_district.sort_values().unique()]


###############################################################################
##update status
###############################################################################
@app.callback(Output('status-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_status(country, district, sub_district, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT current_status_text from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.current_status_text.sort_values().unique()]


###############################################################################
##update water source
###############################################################################    
@app.callback(Output('watersource-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_watersource(country, district, sub_district, status, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT fuzzy_water_source from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.fuzzy_water_source.sort_values().unique()]


###############################################################################
##update water tech
###############################################################################
@app.callback(Output('watertech-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_watertech(country,  district, sub_district, status, fuzzy_water_source,  management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT fuzzy_water_tech from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.fuzzy_water_tech.sort_values().unique()]


###############################################################################
##update management
###############################################################################
@app.callback(Output('management-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_management(country,  district, sub_district, status, fuzzy_water_source, fuzzy_water_tech, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT management from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.management.sort_values().unique()]

###############################################################################
##update today_pred menu
###############################################################################
@app.callback(Output('today-pred-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('management-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_today_pre(country,  district, sub_district, status, fuzzy_water_source, fuzzy_water_tech, management,  one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT today_preds_text from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.today_preds_text.sort_values().unique()]



###############################################################################
##update one year pred menu
###############################################################################
@app.callback(Output('one-year-pred-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('management-select', 'value'), Input('today-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_one_year_pred(country,  district, sub_district,status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT one_year_preds_text from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"        

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.one_year_preds_text.sort_values().unique()]


###############################################################################
##update three year pred menu
###############################################################################
@app.callback(Output('three-year-pred-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('management-select', 'value'), Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('five-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_three_year_pred(country,  district, sub_district,status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT three_year_preds_text from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"        

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.three_year_preds_text.sort_values().unique()]


###############################################################################
##update five year pred menu
###############################################################################
@app.callback(Output('five-year-pred-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('management-select', 'value'), Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('impact-level-select', 'value')])
def update_year_pred(country,  district, sub_district,status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT five_year_preds_text from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"        

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.five_year_preds_text.sort_values().unique()]


###############################################################################
##Impact Level Update
###############################################################################
@app.callback(Output('impact-level-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('management-select', 'value'), Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value'), Input('three-year-pred-select', 'value'), Input('five-year-pred-select', 'value')])
def update_impact_level(country,  district, sub_district,status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT impact_text from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"  

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"     

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.impact_text.sort_values().unique()]


###############################################################################
##Download Update
###############################################################################

@app.callback(Output('download-link', 'href'), [Input('submit-button', 'n_clicks')], state= [State('country-select', 'value'),
 State('status-select', 'value'), State('district-select', 'value'), State('sub-district-select', 'value'), State('watersource-select', 'value'), State('watertech-select', 'value'),
 State('management-select', 'value'), State('today-pred-select', 'value'), State('one-year-pred-select', 'value'), State('three-year-pred-select', 'value'), State('five-year-pred-select', 'value'), State('impact-level-select', 'value')])
def run_query(n_clicks, country, status, district, sub_district, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, impact_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT country_name, district, sub_district, current_status_text, fuzzy_water_source, fuzzy_water_tech, today_preds_text, one_year_preds_text, three_year_preds_text, five_year_preds_text, one_km_population, one_km_functioning_water_points, impact_text, management, lat_deg, lon_deg from final_all WHERE country_name =" + "'" + str(country) + "'"


    if not status:
        pass
    else:
        base_query = base_query + " and current_status_text in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    if not three_year_preds_text:
        pass
    else:
        base_query = base_query +" and three_year_preds_text in (" + ', '.join("'" + i + "'" for i in three_year_preds_text) + ")"

    if not five_year_preds_text:
        pass
    else:
        base_query = base_query +" and five_year_preds_text in (" + ', '.join("'" + i + "'" for i in five_year_preds_text) + ")"

    if not impact_text:
        pass
    else:
        base_query = base_query +" and impact_text in (" + ', '.join("'" + i + "'" for i in impact_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    df.columns = ['Country', 'District', 'Subdistrict', 'Last Known Status', 'Water Source', 'Water Tech', 'Predicted Status: Today',
    'Predicted Status: 1 Year', 'Predicted Status: 3 Year', 'Predicted Status: 5 Year', 'Pop. within 1km', 'Func. Water Points within 1km', 'Impact Level', 'Management', 'Lat_Deg', 'Lon_Deg']
    conn.close()
    csv_string = df.to_csv(index=False, encoding='utf-8')
    #Switch these two when pushing live
    #Live Code
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    #Testing Code
    #csv_string = "data:text/csv;charset=utf-8," + urllib.quote(csv_string)

    return csv_string

