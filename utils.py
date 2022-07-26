from tkinter import LEFT
import numpy as np
from ibeis.control.manual_annot_funcs import *  
import ibeis
import edit_info_in_ibeis
import info_to_csv
import itertools as it
import pandas as pd
import os
import cv2
import re

# Utility functions

def list_to_tuple(same_annot_from_feat_list): 
    ''' Generate a list of tuples consist of the combination of the elements from an input list. For constructing the graph of annotations to traverse and finding connected components. 

    Args: 
        same_annot_from_feat_list: A list of annotations that are considered the same individual

    Returns:
        A list of tuples of the combinations of the annotations in the list.
    '''
    tuples = []
    for i in range(int(len(same_annot_from_feat_list)/2)):
        tuples.append((same_annot_from_feat_list[2*i], same_annot_from_feat_list[2*i+1]))
    if ((len(same_annot_from_feat_list)%2 != 0) & (len(same_annot_from_feat_list) >1)):
            tuples.append((same_annot_from_feat_list[len(same_annot_from_feat_list)-2], same_annot_from_feat_list[len(same_annot_from_feat_list)-1]))


    return tuples


def connect(db_name, lst_of_same_individual, modify_db = True):
    ''' Think of each aid as a node and each tuple as an edge. Goal: find all the connected components so that if there's a match between any images of the two groups, they will be considered the same group.

    Args:
        db_name: name of the database 
        lst_of_same_individual: a list which contains tuples of images that are already confirmed to be from the same individual (e.g. from time and GPS location)
        modify_db: whether the reflect of mergeing groups will be reflected in the IBEIS user interface. 
        
    '''

    def dfs(aid, key):
        ''' 
        key will serve as the key of connected_components for indexing purposes. Performs a DFS search of the node.
        '''
        visited.append(aid)
        connected_components[key].append(aid)
        for neighbor in adjacent_dict[aid]:
            if neighbor not in visited:
                dfs(neighbor, key)
                
    adjacent_dict = {} # dictionary for storing the neighbors of the aids

    for aid1, aid2 in lst_of_same_individual:
        if aid1 not in adjacent_dict.keys():
            adjacent_dict[aid1] = [aid2]
        else:
            adjacent_dict[aid1].append(aid2)
        if aid2 not in adjacent_dict.keys():
            adjacent_dict[aid2] = [aid1]
        else:
            adjacent_dict[aid2].append(aid1)


    visited = [] # visited nodes
    connected_components = {} # values will be a list of connected nodes


    for aid in adjacent_dict:
        if aid not in visited:
            connected_components[aid] = []
            dfs(aid, aid)

    if modify_db:
        ibs = ibeis.opendb(db_name)
        
        # Edit names in IBEIS
        for key in connected_components:
            existing_names =  [name for name in ibs.get_annot_name_texts(connected_components[key])]# if one of the names is not the default name, is when the csv was imported, it has a predesignated name, use that name
            final_name = ""
            for i in range(len(existing_names)):
                if (re.findall("^\d{10}$", existing_names[i]) == []):
                    final_name = existing_names[i]
            if final_name == "":
                final_name = existing_names[0] # Picked a random name from the annotations in the group 
            ibs.set_annot_names(connected_components[key], [final_name for i in range(len(connected_components[key]))])
    else:
        return connected_components


def workflow(database_name, photo_directory, input_csv, csv_destination_dir, clustering_func, symlink_dir, threshold, aid_list = None):
    ''' The complete workflow for extracting information from csv, computing matches and editing names in ibeis
    Args: 
        database_name: the database to be edited on in IBEIS 
        photo_directory: The directory in which the photos are in. Need to contain two sub directories, one named  `Left` and the other `Right` for collecting viewpoint purpose. 
        csv_destination_dir: Designated file path of the metadata csv generated 
        clustering_func: the clustering function to be used on. Currently the best one is vsone score. 
        symlink_dir: the directory in which the manual review of photos will take place. 
    '''
    # Generate a csv with name name, GPS, time, viewpoint and individual name based on GPS and time
    info_to_csv.integrating_info(input_csv, csv_destination_dir)
    metadata = pd.read_csv(csv_destination_dir)
    # Plug in the names to IBEIS
    edit_info_in_ibeis.edit_info_in_ibeis(database_name, csv_destination_dir)
    
    # Apply image equalization on the images if the images are too dark
    left_photo_dir = photo_directory + "Left/"
    right_photo_dir = photo_directory + "Right/"
    for photo_dir in [left_photo_dir, right_photo_dir]:
        img_preprocess(photo_dir)

    ibs = ibeis.opendb(database_name)
        # For bootstrapping purposes
    filenames = []
    for file in os.listdir(left_photo_dir):
        filenames.append(file)
    for file in os.listdir(right_photo_dir):
        filenames.append(file)

    if (aid_list == None):
        aid_list = ibs.get_valid_aids()
    # Find all permutations of aids except aids under the same individual
    all_required_edges = [] # All edges that requires inspection
    all_comb = list(it.combinations(aid_list, 2))
    lst_of_same_individual = [] # List for storing aids of the same individual

    for edge in all_comb:
        if (ibs.get_annot_name_texts(edge[0]) != ibs.get_annot_name_texts(edge[1])) & ((edge[1], edge[0]) not in all_required_edges) & ((ibs.get_annot_viewpoint_code([edge[0]]) == ibs.get_annot_viewpoint_code([edge[1]]))):
            all_required_edges.append(edge)
        elif (ibs.get_annot_name_texts(edge[0]) == ibs.get_annot_name_texts(edge[1])) & ((edge[1], edge[0]) not in lst_of_same_individual):
            lst_of_same_individual.append(edge)
        
    lst_of_same_individual = clustering_func(database_name, all_required_edges, lst_of_same_individual, threshold) # Obtains a list of tuples of matches

    connect(database_name, lst_of_same_individual, modify_db= True) # Traverse the list of tuples to mark all connected components as the same individual

    
    metadata["Predicted Name"] = ""
    
    for aid in aid_list:
        predicted_name = ibs.get_annot_name_texts(aid)
        metadata.loc[metadata["File Name"] == ibs.get_annot_image_names(aid), "Predicted Name"] = predicted_name
    
    metadata.to_csv(csv_destination_dir)
    
    #sort_photos_for_manual_review(csv_destination_dir, symlink_dir, photo_directory)
    return aid_list
    

    
def sort_photos_for_manual_review(csv_dir, symlink_dir, photo_dir):
    '''
    Reads in a metadata csv from csv_dir, put the symlink of photos into folders under symlink_dir
    Args:
        csv_dir: File path of the csv containing the metadata info
        symlink_dir: the directory in which the manual review of photos will take place. 
        photo_dir: original directory of where the photos were 
    '''
    metadata = pd.read_csv(csv_dir)
    metadata["Symlink Location"] = ""
    names_list = np.unique(metadata["Predicted Name"].tolist())
    left_photo_dir = photo_dir + "Left/"
    right_photo_dir = photo_dir + "Right/"

    for predicted_name in names_list:
        filename_lst = metadata[metadata["Predicted Name"] == predicted_name]["File Name"]
        folder_name= symlink_dir + str(predicted_name) + "/"
        os.mkdir(folder_name)
        for filename in filename_lst:
            dest = folder_name + filename
            if metadata[metadata["File Name"] == filename]["Viewpoint"].tolist()[0] == 5: # Photos with different viewpoints are in different folders!
                photo_dir = left_photo_dir
            else:
                photo_dir = right_photo_dir
            os.symlink(photo_dir + filename, dest)
            metadata.loc[metadata["File Name"] == filename, "Symlink Location"] = dest
    metadata.to_csv(csv_dir)

def review_photo_change(image_name, review_name, csv_dir, symlink_dir):
    '''
    Takes in the name of an image to be move and moved it to the folder under review_name. The change is also reflected in the metadata csv
    Args:
        image_name: image to be moved
        review_name: the name determined by human reviewers to be the individual; needs to be an existing name
        symlink_dir: the directory in which the manual review of photos will take place. 
    '''
    metadata = pd.read_csv(csv_dir)
    original_name = metadata[metadata["File Name"] == image_name]["Predicted Name"].tolist()[0]
    src_path = symlink_dir + str(original_name) + "/" + image_name
    dest_path = symlink_dir + str(review_name) + "/" + image_name
    metadata.loc[metadata["File Name"] == image_name, "Symlink Location"] = dest_path
    metadata.loc[metadata["File Name"] == image_name, "Predicted Name"] = review_name
    os.rename(src_path, dest_path)
    metadata.to_csv(csv_dir)

def img_preprocess(photo_dir):
    '''
    Apply histogram equalization on the images in the directory if it's too dark
    Args:
        photo_dir: the directory which contains images that needs to be stretched
    '''
    def show_hsv_equalized(image):
        H, S, V = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))
        eq_V = cv2.equalizeHist(V)
        eq_image = cv2.cvtColor(cv2.merge([H, S, eq_V]), cv2.COLOR_HSV2RGB)
        return eq_image

    for filename in os.listdir(photo_dir):
        img = cv2.imread(photo_dir + "/" + filename)
        img_array = img.flatten()
        if (np.percentile(img_array, 95) - np.percentile(img_array, 5) < 50):
            new_img = show_hsv_equalized(img)
            cv2.imwrite(photo_dir + "/" + filename, new_img)







