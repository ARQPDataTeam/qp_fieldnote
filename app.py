from dash import Dash, html, dcc ,dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from sqlalchemy import create_engine,text
from credentials import get_host_environment, get_credentials, create_dash_app
from flask import request
from datetime import datetime
import os
import logging
from dash_breakpoints import WindowBreakpoints
import socket
import traceback

# Local dev boolean
computer = socket.gethostname()
if computer == 'WONTN774787':
    local = True
else:
    local = False

# Version number to display
version = "2.4"

# Setup logger
if not os.path.exists('logs'):
    os.mkdir('logs')
    
logging.basicConfig(
    format = '%(message)s',
    filename='logs/log.log', 
    filemode='w+',
    level = 20)

logging.getLogger("azure").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Global variable to store headers
request_headers = {}

# set up path details
parent_dir = os.getcwd()
path_prefix = '/' + os.path.basename(os.path.normpath(parent_dir)) + '/'

# set up the sql connection string
COMPUTER, SERVER, VIEWER_USER, VIEWER_PASSWORD, EDITOR_USER, EDITOR_PASSWORD, DATABASE, URL_PREFIX = get_credentials(parent_dir)

# determine host environment
host = get_host_environment(COMPUTER)

# initialize the app based on host, specify the url_prefix if needed
app, server = create_dash_app(host, path_prefix, URL_PREFIX)

# # Get connection string
sql_engine_string=('postgresql://{}:{}@{}/{}?sslmode=require').format(EDITOR_USER,EDITOR_PASSWORD,SERVER,'dcp')
dcp_sql_engine=create_engine(sql_engine_string)


# Setup the app layout
## MOBILE
def serve_layout():
    
    global databases
    global users
    global sites
    global instruments
    global projects
    global flag_table
    
    # pull required data from tables
    databases = pd.read_sql_table("databases",dcp_sql_engine)
    users = pd.read_sql_table("users", dcp_sql_engine)
    sites = pd.read_sql_query(
        "select * from stations", 
        dcp_sql_engine)
    instruments = pd.read_sql_query(
        "select * from instrument_history where active = 'True'", 
        dcp_sql_engine)
    projects = databases['label'].loc[databases['active']==True].values
    flag_table = pd.read_sql_query(
        "select * from flags", 
        dcp_sql_engine)
    
    dcp_sql_engine.dispose()
    
    
    return(
        html.Div([
            html.Div(id = "display",style={'textAlign': 'center'}),
            WindowBreakpoints(
                id="breakpoints",
                # Define the breakpoint thresholds
                widthBreakpointThresholdsPx=[768],
                widthBreakpointNames=["sm", "lg"]
            )
        ])
    )

@app.callback(
    Output("display", "children"),
    Input("breakpoints", "widthBreakpoint"),
    State("breakpoints", "width"),
)
def change_layout(breakpoint_name: str, window_width: int):
    if breakpoint_name=="sm":
        return([
            #title + instructions
            html.H1('QP FieldNote'),
            html.Div([
                html.Span('Required fields indicated by '),
                html.Span('*',style={"color": "red","font-weight": "bold"})
            ]),
            html.Span('v. '+version),
            html.Br(),
            
            # User
            dbc.Row([
                dbc.Col(
                    [dbc.Label(html.H2([
                        "User",
                        html.Span('*',style={"color": "red","font-weight": "bold"})
                    ])),
                    html.Br(),
                    dcc.Input(
                        style={'textAlign': 'center'},
                        id = "user",
                        placeholder="..."
                    ),
                    html.Br()],
                    width = 8
                )],
                id = "user_div",
                justify = "center"
            ),
            
            # Project
            dbc.Row([
                dbc.Col(
                    [dbc.Label(html.H2([
                        "Project",
                        html.Span('*',style={"color": "red","font-weight": "bold"})
                    ])),
                    dcc.Dropdown(
                        projects,
                        id = "project",
                        placeholder="..."
                    ),
                    html.Br()],
                    width = 8
                )],
                id = "project_div",
                justify = "center"
            ),
            
            # Site
            dbc.Row([
                dbc.Col(
                    [dbc.Label(html.H2([
                        "Site",
                        html.Span('*',style={"color": "red","font-weight": "bold"})
                    ])),
                    dcc.Dropdown(
                        id = "site",
                        placeholder="...",
                        optionHeight=50
                    ),
                    html.Br()],
                    width = 8
                )],
                id = "site_div",
                justify = "center",
                style={'display':'none'}
            ),
            
            # Instrument
            dbc.Row([
                dbc.Col(
                    [dbc.Label(html.H2([
                        "Instrument",
                        html.Span('*',style={"color": "red","font-weight": "bold"})
                    ])),
                    dcc.Dropdown(
                        id = "instrument",
                        placeholder="...",
                        optionHeight=50
                    ),
                    html.Br()],
                    width = 8
                )],
                id = "instrument_div",
                justify = "center",
                style={'display':'none'}
            ),
            
            # Flag Category
            dbc.Row([
                dbc.Col(
                    [dbc.Label(html.H2("Flag Category")),
                    dcc.Dropdown(
                        options=list(set(flag_table['category'].tolist())),
                        id = "flag_cat",
                        placeholder="...",
                        optionHeight=50
                    ),
                    html.Br()],
                    width = 8
                )],
                id = "flagcat_div",
                justify = "center",
                style={'display':'none'}
            ),
            
            # Flag
            dbc.Row([
                dbc.Col(
                    [dbc.Label(html.H2("Flag")),
                    dcc.Dropdown(
                        id = "flag",
                        placeholder="...",
                        optionHeight=50
                    ),
                    html.Br()],
                    width = 8
                )],
                id = "flag_div",
                justify = "center",
                style={'display':'none'}
            ),
            
            # Note
            dbc.Row([
                dbc.Col(
                    [dbc.Label(html.H2("Note")),
                    dbc.Input(
                        placeholder="...", 
                        id = "note",
                        type="text"),
                    html.Br()],
                    width = 8
                )],
                id = "note_div",
                justify = "center",
                style={'display':'none'}
            ),
            
            # Date and time
            dbc.Row([
                dbc.Col(
                    [dbc.Label(html.H2([
                        "Datetime",
                        html.Span('*',style={"color": "red","font-weight": "bold"})
                    ])),
                    dbc.Input(
                        value = datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        placeholder="...",
                        id = "startdt",
                        type="datetime-local",
                        step="1"
                    )],
                    width = 8
                )],
                id = "date_div",
                justify = "center",
                style={'display':'none'}
            ),
            
            # Timezone
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        options = ["UTC","EST","EDT"],
                        value = "EST",
                        id = "timezone",
                        placeholder="Timezone",
                        optionHeight=50
                    ),
                    html.Br()],
                    width = 4
                )],
                id = "tz_div",
                justify = "center",
                style={'display':'none'}
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Submit",
                        id = "submit_button",
                        color="info", 
                        disabled=True),
                    html.Br()],
                    width = 4
                )],
                id = "buttons_div",
                justify = "center",
                className="d-grid gap-2"
            ),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    dcc.Loading(
                        id="loading",
                        type="default",
                        children=html.Div(id="submit_button_loading")
                    )],
                    width = 8
                )],
                id = "loading_div",
                justify = "center"
            ),
            dbc.Tooltip(
                "Required input missing",
                id="submit_tooltip",
                target="buttons_div",
                placement="bottom"
            ),
            
            dbc.Row([
                dbc.Col(id = "logtable_div",
                        width = 9,
                        align = "center")
                ],
                justify = "center",
                style={'display':'none'}
            ),
            
            html.Div(id='logs'),
            dcc.Interval(id='log_updater',interval = 2000)
        ])
    else:
        return([
            dbc.Row([
                #title + instructions
                html.H1('QP FieldNote'),
                html.Div([
                    html.Span('Required fields indicated by '),
                    html.Span('*',style={"color": "red","font-weight": "bold"})
                ]),
                html.Span('v. '+version),
                html.Br(),
            ]),
            
            html.Br(),
            dbc.Row([
                # User
                dbc.Col(
                    dbc.Row(
                        dbc.Col(
                            [dbc.Label(html.H2([
                                "User",
                                html.Span('*',style={"color": "red","font-weight": "bold"})
                            ])),
                            html.Br(),
                            dcc.Input(
                                style={'textAlign': 'center'},
                                id = "user",
                                placeholder="...",
                            )]
                        ),
                        justify = "center",
                        style = {'display':'block'}
                    ),
                    id = "user_div",
                    width = 3,
                    align = "center"
                ),
                # Project
                dbc.Col(
                    [dbc.Label(html.H2([
                        "Project",
                        html.Span('*',style={"color": "red","font-weight": "bold"})
                    ])),
                    dcc.Dropdown(
                        projects,
                        id = "project",
                        placeholder="..."
                    )],
                    width = 3,
                    id = "project_div",
                    align = "center"
                ),
                # Site
                dbc.Col(
                    dbc.Row(
                        dbc.Col(
                            [dbc.Label(html.H2([
                                "Site",
                                html.Span('*',style={"color": "red","font-weight": "bold"})
                                ])),
                            dcc.Dropdown(
                                id = "site",
                                placeholder="...",
                                optionHeight=50
                            )],
                        ),
                        justify = "center",
                        style = {'display':'block'}
                    ),
                    width = 3,
                    id = "site_div",
                    style = {'display':'none'}
                )],
                justify = "center"
            ),
            
            html.Br(),
            dbc.Row([
                # Instrument
                dbc.Col(
                    [dbc.Label(html.H2([
                        "Instrument",
                        html.Span('*',style={"color": "red","font-weight": "bold"})
                    ])),
                    dcc.Dropdown(
                        id = "instrument",
                        placeholder="...",
                        optionHeight=50
                    )],
                    width = 3,
                    id = "instrument_div",
                    align = "center",
                    style = {'display':'none'}
                ),
                
                # Flag Category
                dbc.Col(
                    [dbc.Label(html.H2("Flag Category")),
                    dcc.Dropdown(
                        options=list(set(flag_table['category'].tolist())),
                        id = "flag_cat",
                        placeholder="...",
                        optionHeight=50
                    )],
                    width = 3,
                    id = "flagcat_div",
                    align = "center",
                    style = {'display':'none'}
                ),
                
                # Flag
                dbc.Col(
                    [dbc.Label(html.H2("Flag")),
                    dcc.Dropdown(
                        id = "flag",
                        placeholder="...",
                        optionHeight=50
                    )],
                    width = 3,
                    id = "flag_div",
                    align = "center",
                    style = {'display':'none'}
                )],
                justify = "center"
            ),
            
            html.Br(),
            dbc.Row([
                # Note
                dbc.Col(
                    dbc.Row(
                        dbc.Col(
                            [dbc.Label(html.H2("Note")),
                            html.Br(),
                            dcc.Textarea(
                                placeholder="...", 
                                id = "note",
                                style={'width': '75%'}),
                            ],
                        ),
                        justify='center',
                        style = {'display':'block'}
                    ),
                    width = 6,
                    id = "note_div",
                    align = "center",
                    style = {'display':'none'}
                ),
                # Datetime and timezone
                dbc.Col([
                    dbc.Row(
                        dbc.Col([
                            dbc.Label(html.H2([
                                "Datetime",
                                html.Span('*',style={"color": "red","font-weight": "bold"})
                            ])),
                            dbc.Input(
                                value = datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                                placeholder="...",
                                id = "startdt",
                                type="datetime-local",
                                step="1"
                            )],
                        ),
                        id ="date_div",
                        justify = "center",
                        style = {'display':'none','width':'75%'}
                    ),
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                options = ["UTC","EST","EDT"],
                                value = "EST",
                                id = "timezone",
                                placeholder="Timezone",
                                optionHeight=50
                            )],
                            width = 3
                        )],
                        id = "tz_div",
                        justify = "center",
                        style={'display':'none','width':'75%'}
                    )],
                    width = 6,
                    align = "center"
                )],
                
                justify = "center"
            ),
            
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Submit",
                        id = "submit_button",
                        color="info", 
                        disabled=True),
                    html.Br()],
                    width = 4
                )],
                id = "buttons_div",
                justify = "center",
                className="d-grid gap-2"
            ),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    dcc.Loading(
                        id="loading",
                        type="default",
                        children=html.Div(id="submit_button_loading")
                    )],
                    width = 8
                )],
                id = "loading_div",
                justify = "center"
            ),
            dbc.Tooltip(
                "Required input missing",
                id="submit_tooltip",
                target="buttons_div",
                placement="bottom"
            ),
            
            
            html.Br(),
            dbc.Row([
                dbc.Col(id = "logtable_div",
                        width = 9,
                        align = "center")
                ],
                justify = "center"
            ),
            
            
            
            html.Div(id='logs'),
            dcc.Interval(id='log_updater',interval = 5000)
            
        ])

#%% Select project callback
@app.callback(
    Output('site_div', 'style'),
    Output('site','options'),
    Output('logtable_div','children'),
    Input('project','value'),
    Input('submit_button','disabled'),
    State("breakpoints", "widthBreakpoint"))
def project_update(project,temp_var,breakpoint_name: str):
    
    
    global logs
    
    # sites for selected project
    sites_filtered = np.sort(sites.loc[sites["projectid"]==project]['short_description']).tolist()
    
    # show row and update
    if project == "" or project is None:
        return [{'display':'none'},sites_filtered,""]
    elif breakpoint_name =="sm":
        return [{'display':'flex'},sites_filtered,""]
    else:
        
        # Find database corresponding to selected project
        database = databases['database'].loc[databases['label']==project].tolist()[0]  
        
        sql_engine_string=('postgresql://{}:{}@{}/{}?sslmode=require').format(EDITOR_USER,EDITOR_PASSWORD,SERVER,database)
        sql_engine=create_engine(sql_engine_string)
        
        logs = pd.read_sql_query(
            "select * from logs", 
            sql_engine)
        sql_engine.dispose()
        
        # Format logs table
        logs_formatted = logs.loc[:,['loguser','datetime','startdt',
                                     'station','instrument','field_flag',
                                     'field_comment']]
        logs_formatted.columns = ['User','Submission Datetime',
                                  'Log Datetime','Station','Instrument',
                                  'Flag','Note']
        
        # Sort and format dt
        logs_formatted = logs_formatted.sort_values(by='Submission Datetime', ascending=False)    
        logs_formatted['Submission Datetime'] = logs_formatted['Submission Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        logs_formatted['Log Datetime'] = logs_formatted['Log Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        
        
        return_logs_table = [dash_table.DataTable(
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '50px', 'width': '100px', 'maxWidth': '400px',
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
            style_cell={'textAlign': 'center'},
            style_filter={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },  
            filter_action="native",
            filter_options={"placeholder_text": "Filter..."},
            sort_action="native",
            sort_mode="single",
            page_size=10,
            data = logs_formatted.to_dict('records'),
            columns=[{"name": i, "id": i} for i in logs_formatted.columns]
        )]
        return [{'display':'block'},sites_filtered,return_logs_table]


#%% Site selection callback
@app.callback(
    Output('instrument_div', 'style'),
    Output('flagcat_div', 'style'),
    Output('flag_div', 'style'),
    Output('note_div', 'style'),
    Output('date_div', 'style'),
    Output('tz_div', 'style'),
    Output('instrument','options'),
    Input('site','value'),
    State('project','value'),
    State("breakpoints", "widthBreakpoint"))
def site_update(site,project,breakpoint_name: str):
    
    # show all remaining rows
    if site == "" or site is None:
        d = {'display':'none'}
        return_list = [d]*6
        return_list.append([''])
    else:
        if breakpoint_name =="sm":
            d ={'display':'flex'}
            return_list = [d]*6
        else:
            d ={'display':'block'}
            return_list = [d]*4
            return_list.append({'display':'block','width':'75%'}) # datetime div
            return_list.append({'display':'flex','width':'75%'}) # tz div
        
        # instruments for selected site
        siteid = sites[(sites['short_description']==site) &
                               (sites['projectid']==project)]['siteid'].tolist()[0]
        
        instruments_filtered = np.sort(instruments.loc[
                (instruments["projectid"]==project) &
                (instruments["currentlocation"] == siteid)]['instrumentnamelabel']).tolist()
        
        return_list.append(instruments_filtered)
        
    return return_list
        

#%% Flag category selection callback 
@app.callback(
    Output('flag','options'),
    Input('flag_cat','value'))
def flag_update(flag_cat):
    
    # flags for selected category
    if flag_cat == "" or flag_cat is None:
        flags = [""]
    else:
        flags = np.sort(flag_table.loc[flag_table["category"]==flag_cat]['description']).tolist()
    return flags



#%% Show submit button when all required inputs are put in
@app.callback(
    Output('submit_button','disabled'),
    Output('submit_tooltip','children'),
    Input('user','value'),
    Input('project','value'),
    Input('site','value'),
    Input('instrument','value'),
    Input('startdt','value'),
    Input('timezone','value'),
    Input('flag_cat','value'),
    Input('flag','value'),
    Input('note','value'))
    
def button_update(user,project,site,instrument,startdt,timezone,flag_cat,flag,note):
    
    if any([user is None, 
            project is None,
            site is None,
            instrument is None,
            startdt is None,
            timezone is None]):
        return [True,"Required input missing"]
    else:
        return [False,"Ready to submit"]


#%% Submit to database
@app.callback(
    Output('submit_button_loading','children'),
    Output('submit_button_loading','style'),
    Output('submit_button','disabled',allow_duplicate=True),
    Output('submit_tooltip','children',allow_duplicate=True),
    Input('submit_button', 'n_clicks'),
    State('site','value'),
    State('instrument','value'),
    State('project','value'),
    State('startdt','value'),
    State('timezone','value'),
    State('user','value'),
    State('note','value'),
    State('flag','value'),
    prevent_initial_call=True
)

def upload_log(n,site,instrument,project,startdt,timezone,userinput,note,flag):
    # Find database corresponding to selected project
    database = databases['database'].loc[databases['label']==project].tolist()[0]  
    sql_engine_string=('postgresql://{}:{}@{}/{}?sslmode=require').format(EDITOR_USER,EDITOR_PASSWORD,SERVER,database)
    sql_engine=create_engine(sql_engine_string)
    
    
    # create db connection
    with sql_engine.connect() as conn:
    
        # parse all variables going to db
        siteid = sites[(sites['short_description']==site) &
                       (sites['projectid']==project)]['siteid'].tolist()[0]
        submitdt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        startdt = startdt.replace("T", " ")
        note = note or "" 
        if isinstance(note,list):
            note = ','.join(note)
            
        if flag == "" or flag is None:
            flag_shortcode = ""
        else:
            flag_shortcode = flag_table['flag_code'].loc[flag_table['description']==flag].tolist()[0]
            
        try:
            user = users['usershort'].loc[users['piemail'].str.lower()==userinput.lower()].values[0]
        except:
            user = userinput
                    
        try:
            # queries
            tz_set_query = text("""SET TIME ZONE 'EST5EDT';""")
           
            InsertLog = text('''
            INSERT INTO logs (station,datetime,loguser,logtype,startdt,enddt,field_comment,site_location,instrument,field_flag)
            VALUES ('{0}', '{1}', '{2}','{3}',NULLIF('{4}','')::timestamp,NULLIF('{5}','')::timestamp,'{6}',NULLIF('{7}',''),NULLIF('{8}',''),NULLIF('{9}',''))
            ON CONFLICT DO NOTHING;
            '''.format(siteid,submitdt,
            user,'FIELD', 
            startdt,'', 
            note.replace("'","''"),'', 
            instrument,flag_shortcode))
            
    
            conn.execute(tz_set_query)
            conn.execute(InsertLog)
            conn.commit()
            
            return ["Upload to database successful!",
                    {"color": "green","font-weight": "bold","font-size": "large"},
                    True,
                    "Submission complete!"]
        except Exception as e:
            
            logging.exception(e)
            
            return [traceback.format_exc(),
                    {"color": "red","font-weight": "bold","font-size": "large"},
                    False,
                    "Ready to submit"]
        
    
#%% Callback to update user field based on page headers
@app.callback(
    Output('user', 'value'),
    Output('user', 'disabled'),
    Output('user_div','style'),
    Input('user', 'id')  # This triggers the callback on page load
)
def display_headers(_):
    if request_headers.get('Dh-User'):
        return [request_headers.get('Dh-User'),True,{'display':'none'}]
    else:
        #return [None,False,{'display':'flex'}]
        return ['YousifM',False,{'display':'none'}]



#%% Server route to automatically capture headers when the page is first loaded
@app.server.before_request
def before_request():
    global request_headers
    request_headers = dict(request.headers)  # Capture headers before processing any request

#%% Print log statements
@app.callback(
    Output('logs', 'children'),
    Input('log_updater', 'n_intervals')
)
def update_log(n):
    with open("logs/log.log","r") as log:
        return log.read()

app.layout = serve_layout
if __name__ == "__main__":
    if host == "local":
        app.run(debug=True,port=8080)
    else:
        app.run(debug=False,port=8080)
