# install dash / plotly / pandas
# !pip install dash jupyter-dash pandas

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!  IMPORT   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#%%
from dash import Dash, html, dcc, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import util
from copy import copy
from ast import literal_eval
import datetime 
import plot
from os import getcwd as wd
#%%

app = Dash(__name__)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   LOAD DATAFRAME   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def return_lift_ids(df_orig,column,filter):
    df = df_orig.copy(deep=True)
    ids = df[df[column]==filter]["id"].unique()
    return ids

df_path = f"{wd()}/data/world_championships_data.csv"
global df
df = pd.read_csv(df_path,low_memory=False)

all_lifts_dict = {}
all_lifts_dict['successful'] = return_lift_ids(df,"success",1)
all_lifts_dict['failed'] = return_lift_ids(df,"success",0)

deleted_lifts_list = []

# Dictionanry for selecting the column
# col_names, land_names = util.column_and_landmark_names(all_flag="all")
col_names, land_names = util.column_and_landmark_names(select_features=[0,15,11,23,27,31,16,12,24,28,32])
all_col_dict = {land_names[no]:col_names[no] for no in range(len(col_names))}

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   Some globals   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Value incremented and decremented, when stepping through displayed figures
global window_size
window_size = 10
path_to_saved_df = f"{wd()}/data/world_championships_data_updated.csv"

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   general funcitons   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def plot_feature_given_id_list_centered(lift_id_list,df_orig,title,feature_column = "y0"):
    """
    Given a list of ids plots all the lifts given feature column using "plotly".
    All the lifts are aligned by the local maximum in the y0 (nose).
    """
    df = df_orig.copy(deep=True)
    fig = go.Figure()
    # print("plot ids")
    # print(lift_id_list)
    for id_value in lift_id_list:

            # create a df with only the values for this id.
            df_plot = df[df["id"]==id_value].copy()

            # Find the peak value in the nose feature
            peak = df_plot["y0"].max()

            # Find the index fpr the [eak value]
            index_value = df_plot[df_plot["y0"] == peak].index.to_list()[0]
            index_value = index_value - df_plot.index[0]
            
            start = 0 - index_value
            end = df_plot.shape[0] - index_value
            df_plot.index = range(start,end)
            
            name = "{}:{}".format(id_value,df_plot["name"][0])
            
            # fig.add_trace(go.Scatter(y=df_plot[feature_column], x=df_plot.index, mode="markers",name=name))
            fig.add_trace(go.Scatter(y=df_plot[feature_column], x=df_plot.index, mode="lines",name=name))
    # format figure
    # fig.update_layout(
    #     title = "{} - {}".format(len(lift_id_list),title)
    # )

    return fig

def plot_feature_given_id(lift_id:int,df_orig,feature_column:dict):
    """
    Given a lift id, create a figure displaying the lift
    """
    # print("in the plot function",lift_id,feature_column)
    df = df_orig.copy(deep=True)
    
    # create a df with only the values for this id.
    filter_id = df['id'] == lift_id
    df_plot = df[filter_id].copy()
    fig1 = px.line(df_plot,y = list(feature_column.values()))
    fig2 = px.scatter(df_plot,y = list(feature_column.values()),color="class")

    fig = go.Figure(data=fig1.data + fig2.data) # combine the 2 figures
    return fig

def return_value_from_string(input_str:str,sep_str:str):
    return literal_eval(input_str.split(sep_str)[-1])

def save_df():
    df.to_csv(path_or_buf=path_to_saved_df)

def update_existing_df():
    global df 
    df = pd.read_csv(path_to_saved_df,low_memory=False,index_col=0)

    global all_lifts_dict
    all_lifts_dict = {}
    all_lifts_dict['successful'] = return_lift_ids(df,"success",1)
    all_lifts_dict['failed'] = return_lift_ids(df,"success",0)

def drop_id(id_to_drop):
    '''Remove id from the dataframe and the all lifts dictionary'''
    global df
    print("!!!! In drop id - Start !!!!")
    print(id_to_drop in df['id'].unique()) #check if id dropped

    global all_lifts_dict
    all_lifts_dict  = {}
    try:
        # drop in dataframe
        df = df.drop(index = df[df["id"]==id_to_drop].index)
        print(id_to_drop in df['id'].unique()) #check if id dropped
        
        
        # update the all_lifts_dict
        all_lifts_dict['successful'] = return_lift_ids(df,"success",1)
        all_lifts_dict['failed'] = return_lift_ids(df,"success",0)
        deleted_lifts_list.append(id_to_drop)
        print(f'lift id: {id_to_drop}, {len(deleted_lifts_list)} lifts dropped.')
    except Exception as e:
        print(e)
    



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   LAYOUT   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

app.layout = html.Div(children=[
    # !!!!!!!!!! Selection of lifts !!!!!!!!!!
    html.H1(children='Application for cleaning scraped lift data'),

    html.H2(children='Filter the selected lifts'),

    html.Br(),

    dcc.Dropdown(land_names,land_names[0],id='column-selector-dropdown'),

    dcc.Dropdown(['failed','successful'],'successful',id='success-selector-dropdown'),

    html.Br(),
    html.Div(id="number-of-values"), # number of ids in the selected filters from dropdown
    html.Br(),

    html.Button("Previous 10", id="previous-button",n_clicks=0),
    html.Button("Next 10", id="next-button",n_clicks=1),
    html.Button("All", id="all-button",n_clicks=0),
    html.Br(),
    html.Br(),
    
    # html.Div(id='selected-lift-id'), # selected lift id value in the graph

    dcc.Graph(
        id='lifts-graph'
    ),

    dcc.RangeSlider(
        min = 1,
        max = 10,
        step = 1,
        id = 'range-slider',
        value=[1,10],
    ),

    # !!!!!!!!!! Selected lift point editing controlls !!!!!!!!!!
    
    html.H2(id='selected-lift-id'),
    dcc.Dropdown(land_names,land_names[0:6],id='selected-lift-feature-dropdown',multi=True),
    html.Br(),
    html.Div(id = 'selected-points'),
    html.Br(),

    html.Button("Delete Selected", id="delete-button",n_clicks=0),
    html.Button("Remove lift", id="remove-id-button",n_clicks=0),
    html.Div(id = 'delete-confirm'),
    html.Br(),
    
    html.Button("Save Dataframe", id="save-button",n_clicks=0),
    html.Button("Load Dataframe", id="load-button",n_clicks=0),
    html.Div(id = 'save-load-confirm'),
    html.Br(),
    

    html.Button("set start", id="start-id-button",n_clicks=0),
    html.Button("set extension", id="extension-id-button",n_clicks=0),
    html.Button("set overturn", id="overturn-id-button",n_clicks=0),
    html.Button("set catch", id="catch-id-button",n_clicks=0),
    html.Button("set end", id="end-id-button",n_clicks=0),
    html.Div(id = 'set-class-confirm'),
    html.Br(),
    html.Button("prev id", id="prev-id-button",n_clicks=0),
    html.Button("next id", id="next-id-button",n_clicks=0),
    html.Br(),

    html.Button("PLAY ID", id="play-id-button",n_clicks=0),
    html.Div(id = 'play-confirm'),
    html.Br(),

    dcc.Graph(
        id='selected-lift-graph'
    ),
    dcc.Graph(
        id='lift-frames'
    )
])


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!              !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   CALLBACS   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!              !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   figures   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.callback(
    Output(component_id='lifts-graph',component_property='figure'),
    Input(component_id='range-slider',component_property='value'),
    Input(component_id='column-selector-dropdown',component_property='value'),
    Input(component_id='success-selector-dropdown',component_property='value'),
    Input(component_id='delete-confirm',component_property='children'),
    Input(component_id='save-load-confirm',component_property='children')
    
)



def update_figure(range_slider_value,column_selection,success_selection,deleteConfirm,saveLoadConfirm):
    column_selected = all_col_dict[column_selection]
    fig = plot_feature_given_id_list_centered(
                                              all_lifts_dict[success_selection][range_slider_value[0]:range_slider_value[-1]],
                                              df,
                                              title="All lifts",
                                              feature_column=column_selected)
    fig.update_layout(transition_duration=500)

    return fig

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   filter   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.callback(
    Output('number-of-values','children'),
    Input('success-selector-dropdown','value'),
    Input('delete-confirm','children'),
    Input('save-load-confirm','children')

)

def selected_lifts(successSelection,deleteConfirm,saveLoadConfirm):
    filtered_id_len = len(all_lifts_dict[successSelection])
    return f'Number of total lifts for filter: {filtered_id_len}'


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   id selection   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.callback(
    Output(component_id='selected-lift-id',component_property='children'),
    Input(component_id='lifts-graph',component_property='clickData'),
    State(component_id='range-slider',component_property='value'),
    Input(component_id='success-selector-dropdown',component_property='value'),
    Input(component_id='next-id-button',component_property='n_clicks'),
    Input(component_id='prev-id-button',component_property='n_clicks')

)

def selected_lift_id(selectedData,range_slider_value,success_selection,nextId,prevId):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    try:
        # Curve number of the selected graph
        curveNumber = selectedData["points"][0]["curveNumber"]
        # All the lift ids that are selected on the "lifts-graph"
        figure_lift_ids = all_lifts_dict[success_selection][range_slider_value[0]:range_slider_value[-1]]
        lift_id = figure_lift_ids[curveNumber]
    except:
        figure_lift_ids = all_lifts_dict[success_selection][range_slider_value[0]:range_slider_value[-1]]
        lift_id = figure_lift_ids[0]
    
    # move to next id in the list
    if "next-id" in changed_id or "prev-id" in changed_id:
        print(changed_id)
        lift_id = all_lifts_dict[success_selection][nextId-prevId]

    return f'Selected lift id: {lift_id}'

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   slider   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.callback(
    Output('range-slider','value'),
    Output('range-slider','max'),
    Output('range-slider','min'),
    Input('previous-button','n_clicks'),
    Input('next-button','n_clicks'),
    Input('all-button','n_clicks'),
    State('number-of-values','children')
    
)
def adjust_range_displayed(previous,next,all,number_of_values_all):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    if "all-button" in changed_id:
        max_slider = int(return_value_from_string(number_of_values_all,"r: "))
        min_slider = 0
        value_slider = [0,max_slider]
    elif ("next-button" in changed_id) or ("previous-button" in changed_id):
        max_slider = window_size*(next-previous)
        min_slider = 0+(max_slider-window_size)
        value_slider = [min_slider,max_slider]
    else:
        max_slider = window_size
        min_slider = 0
        value_slider = [min_slider,max_slider]

    return value_slider,max_slider,min_slider



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   display selected graph   !!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.callback(
    Output('selected-lift-graph','figure'),
    Input('selected-lift-id','children'),
    Input('selected-lift-feature-dropdown','value'),
    Input('set-class-confirm','children')
)

def update_selected_lift_id_graph(selected_id,column_selection,setClassConfirm):
    column_selection_landmark =  copy(column_selection)
    
    column_selection_dict = {}
    if type(column_selection) is list:
        column_selection_dict = {col:all_col_dict[col] for col in column_selection_landmark}
    else:
        column_selection_dict[column_selection_landmark] = all_col_dict[column_selection_landmark]

    selected_id = int(return_value_from_string(selected_id,'id: '))

    fig = plot_feature_given_id(selected_id,df,column_selection_dict)
    fig.update_layout(transition_duration=500,dragmode = 'select')
    return fig

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   selected points   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.callback(
    Output('selected-points','children'),
    Input('selected-lift-graph','selectedData')
)

def select_points(selectedPoints):
    try:
        selected_points_index = {index_val["x"] for index_val in selectedPoints["points"]}
        selected_points_index_list = list(selected_points_index)
        selected_points_index_list.sort()
    except:
        selected_points_index_list = "Nothing Selected"
    return f'Selected points: {selected_points_index_list}'


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   remove selected points   !!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@app.callback(
    Output('delete-confirm','children'),
    Input('delete-button','n_clicks'),
    Input('remove-id-button','n_clicks'),
    State('selected-points','children'),
    State('selected-lift-id','children')
)

def delete_selected_points_from_df(delete,removeId,selectedPoints,selected_id):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    try:
        selectedPoints = return_value_from_string(selectedPoints,'s: ')
    except:
        selectedPoints = None
        output_str = "Deleted Nothing"
    
    try:    
        selected_id = return_value_from_string(selected_id,'id: ') # Defaults to first id in the all_lifts_dic
    except:
        selected_id = None
        output_str = "Deleted Nothing"

    if 'remove-id-button' in changed_id:
        drop_id(selected_id)
        print(selected_id,"remove id pressed")
        output_str = f'Deleted id: {selected_id}'

    if 'delete-button' in changed_id:
        # Deletes the points from the gloabal dataframe
        global df
        df = df.drop(index=selectedPoints)
        output_str = f'Deleted points: {selectedPoints}'

    return output_str


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   change class for selected points   !!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@app.callback(
    Output('set-class-confirm','children'),
    Input("start-id-button",'n_clicks'),
    Input("extension-id-button",'n_clicks'),
    Input("overturn-id-button",'n_clicks'),
    Input("catch-id-button",'n_clicks'),
    Input("end-id-button",'n_clicks'),
    State('selected-points','children'),
    State('selected-lift-id','children')
)

def change_class(start,extension,overturn,catch,end,selectedPoints,selected_id):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    try:
        selectedPoints = return_value_from_string(selectedPoints,'s: ')
    except:
        selectedPoints = None
        output_str = "Changed Nothing"
    
    try:    
        selected_id = return_value_from_string(selected_id,'id: ') # Defaults to first id in the all_lifts_dic
    except:
        selected_id = None
        output_str = "Changed Nothing"


    for class_name in ["start","extension","overturn","catch","end"]:
        if class_name in changed_id:
            # Changes the class name for the selected points
            print(class_name)
            global df
            # df.iloc[selectedPoints]["class"] = class_name
            df.loc[selectedPoints,"class"] = class_name
            print(df.iloc[selectedPoints]["class"])
            output_str = f'Updated class points: {selectedPoints}'

    return output_str

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   save / load altered dataframe   !!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@app.callback(
    Output(component_id='save-load-confirm',component_property='children'),
    Input(component_id='save-button',component_property='n_clicks'),
    Input(component_id='load-button',component_property='n_clicks')
)

def update_stored_datafrme(save_click,load_click):

    status_string = "Status: nothing_done"
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if "save-button" in changed_id:
        try:
            # print("saving the df")
            save_df()
            status_string = "Saved dataframe"
        except Exception as e:
            print(e)
    if "load-button" in changed_id:
        try:
            # print("loading the df")
            update_existing_df()
            # print(df)
            status_string = "Loaded dataframe"
        except Exception as e:
            print(e)
    
    status_string = f'{status_string} {datetime.datetime.now().strftime("%H:%M:%S")}'
    print(status_string)
    return status_string

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!   play selected id  !!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.callback(
    # Output('play-confirm','children'),    
    Output(component_id='lift-frames',component_property='figure'),
    Input('play-id-button','n_clicks'),
    State('selected-lift-id','children'),
    State('selected-points','children')
)

def play_the_selected_lift(playId,selected_id,selectedPoints):

    folder_path = f"{wd()}/data/videos/men"
 
    try:
        selectedPoints = return_value_from_string(selectedPoints,'s: ')
        selectedPoints = [selectedPoints[0],selectedPoints[-1]]
        print(selectedPoints)
        # selectedPoints = [0,1]
        
        
        divider = 6
        skip = 0
        selectedPointsLen = len(selectedPoints)
        
    except:
        selectedPoints = [0,1]
    
    try:    
        selected_id = return_value_from_string(selected_id,'id: ') # Defaults to first id in the all_lifts_dic
    except:
        selected_id = None
    
    id_details_dict = {}
    global df
    id_details_dict = plot.id_details([selected_id],df,start_end_index=selectedPoints)

    print(id_details_dict)

    # Get video file path
    try:
        weight = id_details_dict[selected_id]["weightclass"]
        video_path = plot.find_path_in_folder(weight,folder_path)
        print(video_path)
    except Exception as e:
        print(e)

    # play the video
    selected_frames = plot.play_video_at_time(video_path,
                            id_details_dict[selected_id]["start"],
                            id_details_dict[selected_id]["end"])

    
    print(selected_frames.shape)
    title= f'{id_details_dict[selected_id]["name"]}: attempted weight :{id_details_dict[selected_id]["weight"]}'
    # print(id_details_dict[selected_id]["name"])
    
    fig = px.imshow(selected_frames,
                    animation_frame=0,
                    binary_string=True,
                    labels=dict(animation_frame="slice"),
                    title = title
                    ) # binary_compression
    # fig = px.imshow(selected_frames,animation_frame=0)
    divide = 1.5
    fig.update_layout(width = 1920/divide,height = 1080/divide)
    return fig    
    # return str(id_details_dict)



if __name__ == '__main__':
    
    app.run_server(debug=True)

