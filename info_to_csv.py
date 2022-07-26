import os
from turtle import right
from exif import Image
import pandas as pd
import re
import datetime
import time

# Put file name, (temporary) jaguar individual name, time, and GPS to a csv. Pictures with time 
# within a threshold value and has the same GPS location will be considered the same
# occurrence.

'''
For reference
database_name = "DB500" # IBEIS Database name to work on
photo_directory = "/home/yuerou/selected_photos/" #  File Path of the folder containing all the photos
stations_directory = "~/code/station_data_peru.csv" # File path of the csv containing the coordinates of the stations
images_summary_directory = "~/code/JaguarImagesSummary.csv" # File path of the csv containing all the metadata of the images, including station and survey number
csv_destination_dir = "/home/yuerou/500.csv" # File path of the csv generated 
'''

timestamp_threshold = 200

def integrating_info(input_csv, csv_destination_dir):
    ''' Extract information on name, time, GPS, viewpoint of images and store them into a csv file.
    
    Args: 
        photo_directory: The directory in which the photos are in. Need to contain two sub directories, one named  `Left` and the other `Right` for collecting viewpoint purpose. 
        stations_dir: The path for the csv that contains coordinates of the stations
        images_summary_dir: File path of the csv containing all the metadata of the images, including station ID and survey number
        csv_destination_dir: Designated file path of the metadata csv generated 

    '''

    metadata = pd.read_csv(input_csv)
    
    # metadata = pd.DataFrame({"File Name": [], "Individual Name":[], "Time": [], "GPS": [], "Viewpoint": []})

    # Check if the some images already has a name 
    if "Name" not in metadata.columns:
        metadata["Name"] = ""

    # Sort the dataframe so that the ones with an existing name can be at the top
    metadata = metadata.sort_values("Name")
    metadata = metadata.reset_index(drop = True)

    # Get a new dataframe of entries with known names, and append to it 
    metadata_with_name = metadata[(metadata["Name"].notna()) & (metadata["Name"] != "")]
    print(len(metadata_with_name))
    for i in range(len(metadata_with_name), len(metadata)):
        unix_time = metadata.iloc[i,:]["Time"]
        gps_info = metadata.iloc[i, :]["GPS"]
        same_occurrence = metadata[(abs(metadata["Time"] - unix_time) <= timestamp_threshold) & (metadata["GPS"] == gps_info) & (metadata["Name"].notna())  & (metadata["Name"] != "")]
        print(same_occurrence)
        if same_occurrence.empty:
            metadata.at[i, "Name"] = unix_time # The new name will be the unix time of the image to prevent duplicates (will there ever be two jaguars on camera at the same time but at two different locations???)
        else:
            metadata.at[i, "Name"] = same_occurrence["Name"].values[0]
        print(metadata)

    metadata.to_csv(csv_destination_dir, index = False)







        
        
        
        