import ibeis
from ibeis.control.manual_annot_funcs import *  
import pandas as pd
import sys


database_name = sys.argv[1] # IBEIS Database name to work on
csv_dir = sys.argv[2] #  The metadata csv generated by the workflow. Will ve overwritten with the new names 

def export(database_name, csv_dir):
    '''
    After human review inside IBEIS, some names might change. Exporting the database will overwrite the predicted 
    name in the csv originally assigned to the images by the workflow. Other columns beside the predicted name column will remain the same 
    '''
    metadata = pd.read_csv(csv_dir)
    ibs = ibeis.opendb(database_name)
    aid_list = ibs.get_valid_aids()
    for aid in aid_list:
        name = ibs.get_annot_names(aid)
        ibs.get_annot_name_texts(aid)
        metadata.loc[metadata["File Name"] == ibs.get_annot_image_names(aid), "Predicted Name"] = name
    
    metadata.to_csv(csv_dir, index = False)

if __name__ == "__main__":
    export(database_name, csv_dir)