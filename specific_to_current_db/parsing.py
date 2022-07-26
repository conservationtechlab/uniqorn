import os
from turtle import right
from exif import Image
import pandas as pd
import re
import datetime
import time

# Parse the info required for metadata processing from filenames. Specific to the input I received (14)

'''
For reference
database_name = "DB500" # IBEIS Database name to work on
photo_directory = "/home/yuerou/selected_photos/" #  File Path of the folder containing all the photos
stations_directory = "~/code/station_data_peru.csv" # File path of the csv containing the coordinates of the stations
images_summary_directory = "~/code/JaguarImagesSummary.csv" # File path of the csv containing all the metadata of the images, including station and survey number
csv_destination_dir = "/home/yuerou/500.csv" # File path of the csv generated 
'''


def parse_info_from_filename(photo_directory, stations_dir, images_summary_dir, csv_destination_dir):
    ''' Extract information on name, time, GPS, viewpoint of images and store them into a csv file.
    
    Args: 
        photo_directory: The directory in which the photos are in. Need to contain two sub directories, one named  `Left` and the other `Right` for collecting viewpoint purpose. 
        stations_dir: The path for the csv that contains coordinates of the stations
        images_summary_dir: File path of the csv containing all the metadata of the images, including station ID and survey number
        csv_destination_dir: Designated file path of the metadata csv generated 

    '''

    stations = pd.read_csv(stations_dir)
    images_summary = pd.read_csv(images_summary_dir)
    
    metadata = pd.DataFrame({"File Name": [], "Time": [], "GPS": [], "Viewpoint": []})

    left_photo_dir = photo_directory + "Left/"
    right_photo_dir = photo_directory + "Right/"
    for photo_dir in [left_photo_dir, right_photo_dir]:
        for filename in os.listdir(photo_dir):
            if "jpg" in filename: # Only look at jpg images for now

                # Get time from filename
                date = re.findall("\d{8}", filename)[0]
                time_of_day = re.findall("\d{8}_(\d{6})", filename)[0]
                
                # changing to unix time
                date_time = datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]), int(time_of_day[0:2]), int(time_of_day[2:4]), int(time_of_day[4:6]))
                unix_time = time.mktime(date_time.timetuple())

                # adding GPS location
                filename2 = re.findall("(\d+_\d+_\d+)", filename)[0]
                survey_id = images_summary[(images_summary["Image1"].str.contains(filename2, na = False)) | (images_summary["Image2"].str.contains(filename2, na = False)) | (images_summary["Image2Full"].str.contains(filename2, na = False)) | (images_summary["Image1Full"].str.contains(filename2, na = False))]["SurveyID"].reset_index()["SurveyID"][0]
                station_id = images_summary[(images_summary["Image1"].str.contains(filename2, na = False)) | (images_summary["Image2"].str.contains(filename2, na = False)) | (images_summary["Image2Full"].str.contains(filename2, na = False)) | (images_summary["Image1Full"].str.contains(filename2, na = False))]["StationID"].reset_index()["StationID"][0]

                lat = stations[(stations["SurveyID"] == survey_id) & (stations["StationID"] == station_id)]["Lat"].values[0]
                long = stations[(stations["SurveyID"] == survey_id) & (stations["StationID"] == station_id)]["Long"].values[0]
                gps_info = (lat, long)
                
                # Extracting viewpoint info from the directory it was in
                if photo_dir == right_photo_dir:
                    viewpoint = 1
                else:
                    viewpoint = 5 # In constants.py left is 5
                # adding time and GPS to data frame
                metadata.loc[len(metadata.index)] = [filename, unix_time, gps_info, viewpoint] 

    metadata.to_csv(csv_destination_dir, index = False)





        
        
        
        