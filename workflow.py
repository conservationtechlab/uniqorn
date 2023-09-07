from ibeis.control.manual_annot_funcs import *
import ibeis
import edit_info_in_ibeis
import info_to_csv
from utils import connect
from preprocees import img_preprocess
import itertools as it
import pandas as pd
import os


def workflow_ibeis(database_name, photo_directory, input_csv, csv_destination_dir,
                   clustering_func, symlink_dir, threshold, aid_list=None):
    ''' The complete workflow for extracting information from csv,
        computing matches and editing names in ibeis
    Args:
        database_name: the database to be edited on in IBEIS
        photo_directory: The directory in which the photos are in.
                         Need to contain two sub directories, one named
                         `Left` and the other `Right` for viewpoint
        csv_destination_dir: Designated file path of the metadata csv generated
        clustering_func: the clustering function to be used on. Best one is vsone score.
        symlink_dir: the directory in which the manual review of photos will take place.
    '''
    # Generate a csv with name name, GPS, time, viewpoint and individual name
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

    if (aid_list is None):
        aid_list = ibs.get_valid_aids()

    # Find all permutations of aids except aids under the same individual
    all_required_edges = []
    all_comb = list(it.combinations(aid_list, 2))
    lst_of_same_individual = []  # List for storing aids of the same individual

    for edge in all_comb:
        if (ibs.get_annot_name_texts(edge[0]) != ibs.get_annot_name_texts(edge[1])) &\
        ((edge[1], edge[0]) not in all_required_edges) &\
        (ibs.get_annot_viewpoint_code([edge[0]]) == ibs.get_annot_viewpoint_code([edge[1]])):
           all_required_edges.append(edge)
        elif (ibs.get_annot_name_texts(edge[0]) == ibs.get_annot_name_texts(edge[1])) &\
             ((edge[1], edge[0]) not in lst_of_same_individual):
            lst_of_same_individual.append(edge)

    # Obtains a list of tuples of matches
    lst_of_same_individual = clustering_func(database_name, all_required_edges,
                                             lst_of_same_individual, threshold)
    # Traverse the list of tuples to mark all connected components as the same individual
    connect(database_name, lst_of_same_individual, modify_db=True)

    metadata["Predicted Name"] = ""

    for aid in aid_list:
        predicted_name = ibs.get_annot_name_texts(aid)
        metadata.loc[metadata["File Name"] == ibs.get_annot_image_names(aid), "Predicted Name"] = predicted_name

    metadata.to_csv(csv_destination_dir)

    #sort_photos_for_manual_review(csv_destination_dir, symlink_dir, photo_directory)
    return aid_list
