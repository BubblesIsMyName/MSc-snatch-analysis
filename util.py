#%%
import pandas as pd
import os
import datetime
import csv
import json
import mediapipe as mp # Import mediapipe
from copy import copy
# Import the pose capture methods from mediapipe
mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_pose = mp.solutions.pose # Mediapipe Solutions
#%%


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!! Utility functions !!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def select_id_rows(df,id_list = [12,7,13,8,14], inverse = False):
    '''
    Returns rows from only the id's in the selected list
    '''    

    if inverse:
        ids_all = df["id"].value_counts().keys().to_list()
        for id_item in id_list:
            ids_all.remove(id_item)
        id_list = ids_all
        
    
    
    frames = []
    for id_value in id_list:
        # Create a filter
        filter_0 = df["id"] == id_value
        
        df = df[filter_0].copy()
        
        frames.append(df)
        
        df = pd.concat(frames)
        df = df.reset_index()
        
        
    
    return df

def save_df_to_csv(df,save_path):
    # Save to csv
    df.to_csv(save_path)
    
    # Check if the data was written to the file
    bash_command = "tail -n 1 {}".format(save_path)    
    os.system(bash_command)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!! Funcitions regarding manipulating column names !!!!!! 
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def feature_column_names(df, dimensions = ["x","y","z"]):
    '''
    Funcition takes a dataframe and returns column names of given feature dimension
    and column names including "class","id","weight","frame_no".
    
    '''
    
    all_columns = df.columns.to_list()
    dimension_columns = []
    
    for item in all_columns:
        for dimension in dimensions:
            if dimension in item:
                dimension_columns.append(item)
    
    # all_columns = [
    # "class",
    # "id",
    # "weight",
    # "frame_no"	
    # ]

    # all_columns.extend(dimension_columns)
    
    return dimension_columns

def column_and_landmark_names(select_features = [0,12,24,16],dimensions = ["y"],all_flag = None):
    '''
    Function retunrns selected feature, column and landmark names lists, by defeault returns
    x,y,z dimension column and feature names for: Nose, Shoulder, Hip and Wrist
    
    '''

    if all_flag == "all":
        select_features = list(range(0,33))

    # Column Names
    column_names = []
    for feature in select_features:
        for dimension in dimensions:
            column_names.append("{}{}".format(dimension,feature))
        
        
    # Landmark Names:
    all_landmark_names_list = [str(item).split(".")[1] for item in mp_pose.PoseLandmark]
    
    landmark_names = []
    for feature in select_features:
        for dimension in dimensions:
            landmark_names.append("{}_{}".format(all_landmark_names_list[feature],dimension))
    
    return column_names, landmark_names

def save_json_output(dict_to_save,name):
        out_file = open("./{}.json".format(name),"w")
        json.dump(dict_to_save,out_file,indent=4)
        out_file.close()

def load_json(name):
        in_file = open("./{}.json".format(name),"r")
        dict_out  = json.load(in_file)
        return dict_out

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!! Normalise data !!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!

def invert_dataframe(df_orig,column_names):
    '''
    Inverts the dataframe values for the feature values
    '''
    
    df = df_orig.copy(deep = True)
    df[column_names] = df[column_names].apply(lambda x:1-x)
    return df


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!! other functions !!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def create_csv_in_path(name_str,folder_path,columns,add_date = True):
    # Create a csv file with classes
    
    # Create name with date
    if add_date:
        csv_path = "{}/{}_{}.csv".format(
            folder_path,name_str,datetime.datetime.now().strftime("%Y_%m_%d__%H_%M"))
    else:
        csv_path = "{}/{}.csv".format(folder_path,name_str)


    with open(csv_path, mode='x', newline='') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(columns)

    # Check if the line was written to the file
    bash_command = "cat {}".format(csv_path)    
    os.system(bash_command)

    return csv_path

def exclude_list_from_list(full_list, list_to_remove):
    """
    Given two lists, creates a third list that excludes 
    the list_to_remove from full_list
    """
    full_list_copy = copy(full_list.to_list())
    print("Full list start size: {}".format(np.size(full_list_copy)))
    
    for value in list_to_remove:
        full_list_copy.remove(value)
    
    print("Full list final size: {}".format(np.size(full_list_copy)))
    return full_list_copy

