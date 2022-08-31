import plotly.express as px
# Allows us to create graph objects for making more customized plots
import plotly.graph_objects as go
import pandas as pd
import numpy as np



# !!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!! Data analysis !!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!

def check_data_quality(lift_id_list, df_orig):
        """
        Given a list of lift ids and a dataframe, go through the ids and plot them to see
        data quality for further processing, if the data is not sutitable or needs further 
        adjustment, enter "n" as input and this lift id will be added to a list of ids to 
        be CHECKED
        """
        df = df_orig.copy(deep=True)
        ids_to_inspect = []
        fig = go.Figure()
        lift_id_list = list(lift_id_list)

        for id_value in lift_id_list[:]:
                # fig.data = [] # empty the figure
                df_plot = df[df["id"]==id_value].copy(deep = True) # copy of dataframe for plotting
                peak = df_plot["y0"].max() # find the peak value
                index_value = df_plot[df_plot["y0"] == peak].index.to_list()[0] # index of the peak
                # df_plot = df_plot.loc[index_value-15:].reset_index().copy() # Reset
                df_plot = df_plot.loc[index_value-15:].reset_index() # Reset
                
                # !!!! PLOT !!!!
                fig = px.line(df_plot,
                        y = ["y0"],
                        title="id : {}, {}/{}".format(id_value,lift_id_list.index(id_value)+1,len(lift_id_list))
                        ).show()

                # !!! Check if you want to add to list !!!
                input_value = input("Good? (n - not good, q - quit)")

                if input_value=="n":
                        ids_to_inspect.append(id_value)
                        print("id: {}".format(id_value))
                if input_value=="q":
                        break
        return ids_to_inspect


# !!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!! Plotting data !!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!

def plot_feature_given_id_list(lift_id_list,df_orig,feature_column = "y0"):
    """
    Given a list of ids plots all the lifts given feature column using "plotly".
    All the lifts are aligned by the local maximum in the y0 (nose).
    """
    df = df_orig.copy(deep=True)
    fig = go.Figure()

    for id_value in lift_id_list:

            df_plot = df[df["id"]==id_value].copy()
            peak = df_plot["y0"].max()
            index_value = df_plot[df_plot["y0"] == peak].index.to_list()[0] # local peakx.to_list()[0]

        #     df_plot = df_plot.loc[index_value-15:index_value+30].reset_index().copy()
            df_plot = df_plot.loc[index_value-15:].reset_index().copy()
            name = "{}:{}".format(id_value,df_plot["name"][0])
            
            fig.add_trace(go.Scatter(y=df_plot[feature_column], mode="markers",name=name))
    fig.show()



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!! playback of a video !!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def id_details(id_list:list,df_orig:pd.DataFrame,start_end_index =[1,-1]):
    '''
    Given a video id, return a dictionary with 

    id_details[id][weightclass] - weightclass
    id_details[id][start] - start time in s
    id_details[id][end] - end time in s

    !!!!! NB - some of the first frame timestamps are incorect, so use the second frame !!!!!!!
    
    '''
    id_details_dic = {}
    try:
        for id in id_list:
            # df = df_orig[df_orig["id"]==id].copy().reset_index()
            df = df_orig[df_orig["id"]==id].copy()

            print(df.weight.unique()[0])
            # print(df["name"][0])
            id_details_dic[id] = {
                "weightclass":df["weightclass"].value_counts().keys()[0],
                # "start":round(df["time_ms"].iloc[start_end_index[0]]),
                # "end":round(df["time_ms"].iloc[start_end_index[1]]),
                "start":round(df["time_ms"].loc[start_end_index[0]]),
                "end":round(df["time_ms"].loc[start_end_index[1]]),
                "weight":int(df.weight.unique()[0]),
                "name":df.name.unique()[0]
                }
    except Exception as e:
        print(e)
    # print(id_details_dic)
    return id_details_dic

import os 

def find_path_in_folder(weight,folder_path):
    '''
    given a weight class, finds the approprite path to a file in a folder
    '''
    files_list = os.listdir(folder_path)
    for item in files_list:
        if ("{}_".format(weight) in item) and (".mp4" in item):
            return "{}/{}".format(folder_path,item)

import cv2

      
def play_video_at_time(vdeo_path,start,end):
    '''
    given a video path and start and end timestamps in us, plays the video on loop
    '''
    # all_frames = np.array((720, 1280, 3))
    # all_frames = np.array()
    print(start,end)
    all_frames = []
    cap = cv2.VideoCapture(vdeo_path) # Using video file
    current_time_ms = 0
    # print(start,end,current_time_ms)

    _, frame = cap.read()
    count = 0 
    cap.set(cv2.CAP_PROP_POS_MSEC,start)
    current_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    
    # print(start,end,current_time_ms)
    while current_time_ms < end:
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        current_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        count +=1
        if count == 5   :
            count = 0 
            all_frames.append(frame)
    
    # np.hstack(all_frames,np.array(frame))
    all_frames = np.array(all_frames)
    # print(all_frames.shape)
    
    
    cap.release()
    
    return all_frames