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

# sys.path.append('..')
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
        id='filter-table-e',
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
query = "SELECT country_name, district, sub_district, current_status_text, fuzzy_water_source, fuzzy_water_tech,  today_preds_text, one_year_preds_text, one_km_population, one_km_functioning_water_points, impact_text, management, lat_deg, lon_deg, map_lat, map_lon  from final_all WHERE country_name = 'Kenya'"
df_init = pd.read_sql_query(query, conn)
df_init["color"] = df_init["today_preds_text"].apply(color_col)
### Can probably clean this part up
df_init2 = df_init.copy()
df2_init = df_init2.drop(['color', 'lat_deg', 'lon_deg', 'map_lat', 'map_lon',  'management'], axis=1, inplace= True)
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
        html.A("Switch to full filtering", href ="/custom" ),
        # Row: Map
        html.Div([
        dcc.Dropdown(className = "dropdown", id = 'country-select-e',
            options=[
            {'label': i, 'value': i} for i in df2.country_name.sort_values().unique()],
             #value = df2.country_name."sort_values().unique()[0], 
            placeholder = "Select a Country",
            value = "Kenya"      
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(className = "dropdown", id = 'district-select-e',
            options=[
            {'label': i, 'value': i} for i in df2.district.sort_values().unique()],
            placeholder = "Select a District",
            multi = True     
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'sub-district-select-e',
            options = [
            {'label': i, 'value': i} for i in df2.sub_district.sort_values().unique()],
            placeholder = 'Select a Sub-District',
            multi = True
        ),
        ], style = {"padding":"5px"}),
        
        html.Div([
        html.H6(children = "Color Water Points By:"),
        dcc.Dropdown(id = 'point-color-select-e',
            options=[
                {'label': ' Last Known Status', 'value': 1},
                {'label': ' Today\'s Prediction', 'value': 2},
                {'label': ' One Year Prediction', 'value':3},
            ],
            value = 3,
            multi=False,
            #labelStyle={'display': 'block', 'font-size':'14px'}                   
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        html.Button('Submit', id= 'submit-button-e')
        ],
        style = {"padding":"5px"}),
        html.Div([
        html.H6(children = "", id = "well_text-e"),
        html.A('Download Data', id= 'download-link-e', download ="waterpoint_data.csv", href="", target= "_blank"),
        ]),
        ], className="col-md-4"),
    
    html.Div([
        dcc.Graph(id = "output-graph-e",
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
## Update map 
###############################################################################
@app.callback(Output('output-graph-e', 'figure'), [Input('submit-button-e', 'n_clicks')], state= [State('country-select-e', 'value'),  State('district-select-e', 'value'), State('sub-district-select-e', 'value'), State('point-color-select-e', 'value')])
def run_query(submit_button, country, district, sub_district, point_color_select):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")


    base_query = "SELECT lat_deg, lon_deg, current_status_text, today_preds_text, one_year_preds_text from final_all WHERE current_status_text =  'Working' and one_year_preds_text ='Not Working' and country_name = '" + str(country) + "'"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"


    df = pd.read_sql_query(base_query, conn)
    if point_color_select == 1:
        df["color"]= df["current_status_text"].apply(color_col)
    if point_color_select ==2:
        df["color"]=df["today_preds_text"].apply(color_col)
    if point_color_select ==3:
        df["color"] = df["one_year_preds_text"].apply(color_col)

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
                    "lat": df.lat_deg.mean(),
                    "lon": df.lon_deg.mean()
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
@app.callback(Output('filter-table-e', 'rows'), [Input('submit-button-e', 'n_clicks')], state= [State('country-select-e', 'value'),  State('district-select-e', 'value'), State('sub-district-select-e', 'value')])
def run_query(submit_button,  country, district, sub_district):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    
    base_query = "SELECT country_name, district, sub_district, current_status_text, fuzzy_water_source, fuzzy_water_tech,  today_preds_text, one_year_preds_text, one_km_population, one_km_functioning_water_points, impact_text, management, lat_deg, lon_deg from final_all WHERE current_status_text =  'Working' and one_year_preds_text = 'Not Working' and country_name = '" + str(country) + "'"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    df = pd.read_sql_query(base_query, conn)
    df.drop(['lat_deg', 'lon_deg', 'management'], axis=1, inplace= True)
    df.columns =['Country', 'District', 'Subdistrict', 'Last Known Status', 'Water Source', 'Water Tech', 'Predicted Status: Today',
    'Predicted Status: 1 Year', 'Pop. within 1km', 'Func. Water Points within 1km', 'Impact Level']
    conn.close()
    return df.to_dict('records')


## Update well_text for number of water points
@app.callback(Output("well_text-e", 'children'), [Input('filter-table-e', 'rows')])
def update_well_text(rows):
    return "Filters matched {} results".format(str(len(rows)))


###############################################################################
##update districts menu
###############################################################################
@app.callback(Output('district-select-e', 'options'), [Input('country-select-e', 'value'), Input('sub-district-select-e', 'value')])
def update_district(country, sub_district):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT district from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.district.sort_values().unique()]


###############################################################################
##update subdistricts menu
###############################################################################

@app.callback(Output('sub-district-select-e', 'options'), [Input('country-select-e', 'value'), Input('district-select-e', 'value')])
def update_subdistrict(country, district):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT sub_district from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.sub_district.sort_values().unique()]



###############################################################################
##Download Update
###############################################################################

@app.callback(Output('download-link-e', 'href'), [Input('submit-button-e', 'n_clicks')], state= [State('country-select-e', 'value'),
  State('district-select-e', 'value'), State('sub-district-select-e', 'value')])
def run_query(n_clicks, country, district, sub_district):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT country_name, district, sub_district, current_status_text, fuzzy_water_source, fuzzy_water_tech, today_preds_text, one_year_preds_text, one_km_population, one_km_functioning_water_points, impact_text, management, lat_deg, lon_deg from final_all WHERE current_status_text =  'Working' and one_year_preds_text = 'Not Working' and country_name = '" + str(country) + "'"


    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    df = pd.read_sql_query(base_query, conn)
    df.columns = ['Country', 'District', 'Subdistrict', 'Last Known Status', 'Water Source', 'Water Tech', 'Predicted Status: Today',
    'Predicted Status: 1 Year',  'Pop. within 1km', 'Func. Water Points within 1km', 'Impact Level', 'Management', 'Lat_Deg', 'Lon_Deg']
    conn.close()
    csv_string = df.to_csv(index=False, encoding='utf-8')
    #Switch these two when pushing live
    #Live Code
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    #Testing Code
    #csv_string = "data:text/csv;charset=utf-8," + urllib.quote(csv_string)

    return csv_string




