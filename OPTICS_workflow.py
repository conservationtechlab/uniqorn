from ibeis.algo.verif.pairfeat import PairwiseFeatureExtractor
from ibeis.control.manual_annot_funcs import * 
from ibeis.control.manual_feat_funcs import * 
import ibeis
import pandas as pd
import itertools as it
import sys
import integrating_names
import edit_unknown_names
import evaluation
import re
from sklearn.cluster import OPTICS
from sklearn.cluster import DBSCAN

# Workflow for trying on Nx128 SIFT features directly

database_name = "MySecondSmallDB" # IBEIS Database name to work on
photo_directory = "/home/yuerou/Downloads/14Crops_equalized/" #  File Path of the folder containing all the photos
stations_directory = "~/code/station_data_peru.csv" # File path of the csv containing the coordinates of the stations
images_summary_directory = "~/code/JaguarImagesSummary.csv" # File path of the csv containing all the metadata of the images, including station and survey number
csv_destination_dir = "/home/yuerou/largeIBEISDB.csv " # File path of the csv generated 


# Generate a csv with name name, GPS, time, viewpoint and individual name based on GPS and time
integrating_names.integrating_names(photo_directory, stations_directory, images_summary_directory, csv_destination_dir)

# Plug in the names to IBEIS
edit_unknown_names.edit_info_in_ibeis(database_name, csv_destination_dir)

ibs = ibeis.opendb(database_name)

matrix = np.array([])
#feat_df = pd.DataFrame({"aid":[]})
for aid in ibs.get_valid_aids():
    feat = ibs.get_annot_vecs(aid)
    if (matrix.size == 0):
        matrix = feat
    else:
        matrix = np.vstack([matrix, feat])
    print(aid)
    #for i in range(len(feat)):
    #    feat_df.loc[len(feat_df.index)] = [aid]

        

#clustering = DBSCAN().fit(matrix)
#feat_df["Label"] = clustering.labels_

#feat_df.to_csv("feat_vs_id_dbscan.csv")

## Filter the noise out of the features 
#valid_df = feat_df[feat_df["Label"]!=-1]
#valid_df = valid_df.reset_index()

# Create a pivot table of aid vs all the possible feature labels 

#count = pd.pivot_table(data = valid_df, index = ["aid"], columns = ["Label"], values = "index", aggfunc = "count")

# Get all possible labels
#feat_label_list = count.columns

# Plug in the current names for the aids based on GPS and time location 
#count["Name"] = count["Name"] = ibs.get_annot_name_texts(count.index.tolist())


# For each feature label,  if aids has >3 of it --> same name. 
#for feat_label in feat_label_list:
#    print(feat_label)
#    same_name_aid_list = count[(count[feat_label]>= 3)].index
#    # Also group with names based on GPS/time! They should already have the same name
#    additional_aids = [] 
#    final_name = "" # a very random way to decide what name this group will take on after this feature is examined
#    for name in np.unique(ibs.get_annot_name_texts(same_name_aid_list)):
#        additional_aids.append(count[count["Name"] == name].index)
#        final_name = name
#    same_name_aid_list = np.unique(same_name_aid_list.append(additional_aids))
#    ibs.set_annot_names(same_name_aid_list, [final_name for i in range(len(same_name_aid_list))])



   
