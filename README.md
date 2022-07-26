# uniqorn
Machine learning tools for individual identification using SIFT features

## Using uniqorn
1. Install [IBEIS](https://github.com/Erotemic/ibeis). uniqorn depends on IBEIS to extract SIFT features and computed annotation matches.
2. uniqorn assumes that the input files will consist of: 
    - A directory with two sub directories named "Left" and "Right", which contains photos of corresponding viewpoint. 
    - Photos which contains the date and time of the photo in the format 'yyyymmdd_hhmmss' somewhere in the name. Finally if evaluation of the results of uniqorn is need (when you know the true names of the individuals), this will will also need to be present somewhere in the file name.
    - A CSV containing the name of the files (with column name either "Image1" or "Image2"), name of the survey ("SurveyID"), station ID ("StationID")
    - A CSV containing the station ID ("StationID"), the station's latitude ("Lat") and longitude ("Long")
3. Import the photos in the photo directory into IBEIS. If the photos are already cropped, then select all the photos and use  `Add annotation from entire image", otherwise crop the images to obtain annotations one by one. 
4. Set the annotation species.
5. To use the one vs one sum to compute matches, call
```
python vsone_workflow.py [database_name] [photo_dir] [stations_dir] [images_summary_dir] [csv_destination_dir] [symlink_dir]
```
`databse_name`: name of the IBEIS database to work on, e.g. "MyNewIBEISDatabase"
`photo_dir`: The directory of the images to be queried on
`stations_dir`: The CSV containing the station ID and coordinates of the stations.
`images_summary_dir`: The CSV containing the survey and station information of the image. 
`csv_destination_dir`: uniqorn will generate a new CSV containing the metadata of the images. Specify the directory of that CSV here. 
`symlink_dir`: where the symbolic links for manual review of photos will be stored

Example call:
```
python -i vsone_workflow.py "tinyDB" "/home/yuerou/tiny/" "~/code/station_data_peru.csv" "~/code/JaguarImagesSummary.csv" "/home/yuerou/generated_info.csv" "/home/yuerou/symlinktest/"
```
6. The results will be reflected in the `Name` column inside IBEIS. The Tree of Names will also reflect the clustering.
### Manual Review
Sometimes when images are blurry, the workflow cannot identify the same individual from different images. Usually the workflow will have more false negatives (the same individual were put into different groups) than false positive (different individuals were put into the same group). Therefore manual review is necessary. When the workflow finish, it will put photos which it predicts to be the same individual under the same folder under the directory specified by `symlink_dir`. If there's any images that you believe should belong to another group (ie. merging two groups), you can run 
`python -i utils.py` then run `review_photo_change(image_name, reviewed_name, csv_dir, symlink_dir)` to move the photo to desired folder under the reviewed name. For example, 
```
review_photo_change("RSDZG  12_20140729_133315_POM 75.jpg", 1, "/home/yuerou/500.csv", "/home/yuerou/symlinktest/")
```



## How it works
Uniqorn will first group images based on their GPS coordinates and time. If the time difference between two images are smaller than 120 second and they have the same GPS coordinates, then the two images will be considered from the same occurrence. Next uniqorn will try to group the occurrences of the same individual together. Each images will be queried against images of other occurrences using the One Vs One algorithm from IBEIS. If the algorithm considers two images a match, then the two occurrences the images are from will be grouped together. 