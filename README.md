# MSC Snatch analysis
 
The following repository contains some of the key scripts for the pipeline of tools and implementations of models.
## Pipeline Diagram
 
![alt text](https://github.com/BubblesIsMyName/MSc-snatch-analysis/blob/main/pipeline.png?raw=true)
 
## Contents of the repository
### Scripts
- **1_data_collection.ipynb** - File contains script for:
  - Downloading the video files.
  - Creating the file structure.
  - Capturing the pose data from the annotations.
- **2_data_cleaning_and _annotation_app.py** - the app created for cleaning and annotating classes in datasets.
   - NB! for the playback of video frames feature, the videos of the world championships data needs to be downloaded. (See the 1_data_collection.ipynb step 1 operations to download the videos and rename them)
- **3_train_classifier.ipymb** - script contains implementation of the classifier models
- **4_1_generate_GAN_training_data.ipynb** - Contains 2 methods for generating training data for use in the GAN model.
- **4_2_conditional_GAN.ipynb** - The code for training and running a conditional GAN model.
 
 
### Other files and folders *(the number of scripts utilising the file)
- **dependancies.txt** - dependencies file containing the list of dependencies for the python environment used by the project.
/data
- **filt_center_method.npy** - numpy object file containing prepared training images for use in training a GAN (4_2)
- **gradient_boost_classifier.pkl** - trained gradient boost classifier. (3)
- **pose_map.png** - map of the pose corresponding pose landmark points returned by mediapipe pose detector.
- **training_data.csv** - processed external data of sntaches performed by author, collected from a training session. (3)
- **world_championships_data.csv** - processed world championships data set. (2, 3, 4_1)
- **world_championships_updated.csv** - processed world championships data set, used as the save to file. (2)
- /videos/men - completed annotations and name files for all the recordings from the 2019 world championships
 - **plot.py** and **util.py** - files containing some of the commonly used functions.
 
 
## Installation
 
 - Create a python virtual environment and install the dependencies as following:
 - !!! The scripts were written and the environment were tested on Ubuntu impish (21.10) !!!
 
```
  python3 -m msc-snatch-env
  python3 -m pip install -r dependencies.txt
  source ./msc-snatch-env/bin/activate
```