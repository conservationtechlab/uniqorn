import pathlib
import re
import pandas as pd
import ibeis
from ibeis.control.manual_annot_funcs import * 


def edit_info_in_ibeis(database_name, csv_location):
    ''' Get the info (name and viewpoint) from the metadata csv
    Args:
        database_name: the name of the database to be edited
        csv_location: the file path of the metadata csv
    '''

    # Get Database
    ibs = ibeis.opendb(database_name)

    # Reads the csv to df that contains all the name and viewpoint information
    df = pd.read_csv(csv_location)
        
    # Get a reference to every annotation
    aid_list = ibs.get_valid_aids()

    viewpoint_list = [] # for some reason I can't set individual viewpoints from individual aid
    for aid in aid_list:
        image_name = ibs.get_annot_image_names(aid)
        new_name = df[df["File Name"] == image_name]["Individual Name"].values[0]
        ibs.set_annot_names(aid, new_name) # Set the name in IBEIS
        viewpoint = df[df["File Name"] == image_name]["Viewpoint"].values[0]
        viewpoint_list.append(viewpoint)
    
    ibs.set_annot_viewpoint_int(aid_list, viewpoint_list)


    