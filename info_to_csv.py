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

timestamp_threshold = 120

def integrating_info(photo_directory, stations_dir, images_summary_dir, csv_destination_dir):
    ''' Extract information on name, time, GPS, viewpoint of images and store them into a csv file.
    
    Args: 
        photo_directory: The directory in which the photos are in. Need to contain two sub directories, one named  `Left` and the other `Right` for collecting viewpoint purpose. 
        stations_dir: The path for the csv that contains coordinates of the stations
        images_summary_dir: File path of the csv containing all the metadata of the images, including station ID and survey number
        csv_destination_dir: Designated file path of the metadata csv generated 

    '''

    stations = pd.read_csv(stations_dir)
    images_summary = pd.read_csv(images_summary_dir)
    
    metadata = pd.DataFrame({"File Name": [], "Individual Name":[], "Time": [], "GPS": [], "Viewpoint": []})

    num_occurrences = 0
    unix_time = 0
    left_photo_dir = photo_directory + "Left/"
    right_photo_dir = photo_directory + "Right/"
    for photo_dir in [left_photo_dir, right_photo_dir]:
        for filename in os.listdir(photo_dir):
            if "jpg" in filename: # Only look at jpg images for now

                #with open(photo_dir+filename, "rb") as img_file:
                #    img = Image(img_file)

                # Get time from filename
                date = re.findall("\d{8}", filename)[0]
                time_of_day = re.findall("\d{8}_(\d{6})", filename)[0]
                
                # changing to unix time
                date_time = datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]), int(time_of_day[0:2]), int(time_of_day[2:4]), int(time_of_day[4:6]))
                unix_time = time.mktime(date_time.timetuple())

                
                #Get time from EXIF
                '''
                time_original = re.sub(":", " ", img.get("datetime_original"))
                time_parsed = re.findall("\d+", time_original)
                date_time = datetime.datetime(int(time_parsed[0]), int(time_parsed[1]), int(time_parsed[2]), int(time_parsed[3]), int(time_parsed[4]), int(time_parsed[5]))
                unix_time = time.mktime(date_time.timetuple())
                '''

                # adding GPS location
                filename2 = re.findall("(\d+_\d+_\d+)", filename)[0]
                survey_id = images_summary[(images_summary["Image1"].str.contains(filename2, na = False)) | (images_summary["Image2"].str.contains(filename2, na = False))]["SurveyID"].reset_index()["SurveyID"][0]
                station_id = images_summary[(images_summary["Image1"].str.contains(filename2, na = False)) | (images_summary["Image2"].str.contains(filename2, na = False))]["StationID"].reset_index()["StationID"][0]
            
                lat = stations[(stations["SurveyID"] == survey_id) & (stations["StationID"] == station_id)]["Lat"].values[0]
                long = stations[(stations["SurveyID"] == survey_id) & (stations["StationID"] == station_id)]["Long"].values[0]
                gps_info = (lat, long)
                
                # determine the individual name from time stamp and GPS location. Look through traversed images to see if there's any images from the same occurrence. 
                same_occurrence = metadata[(abs(metadata["Time"] - unix_time) <= timestamp_threshold) & (metadata["GPS"] == gps_info)]


                if (same_occurrence.empty):
                    name = "Individual No. " + str(num_occurrences)

                    num_occurrences += 1 # A new individual is added to the metadata df
                else:
                    name = same_occurrence["Individual Name"].values[0]
                
                # Extracting viewpoint info from the directory it was in
                if photo_dir == right_photo_dir:
                    viewpoint = 1
                else:
                    viewpoint = 5 # In constants.py left is 5

                # adding time and GPS to data frame
                metadata.loc[len(metadata.index)] = [filename, name, unix_time, gps_info, viewpoint] 


    metadata.to_csv(csv_destination_dir)





        
        
        
        