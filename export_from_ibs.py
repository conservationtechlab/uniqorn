import ibeis
from ibeis.control.manual_annot_funcs import *  
import pandas as pd


def export(database_name, csv_dir):
    metadata = pd.read_csv(csv_dir)
    ibs = ibeis.opendb(database_name)
    aid_list = ibs.get_valid_aids()
    for aid in aid_list:
        name = ibs.get_annot_names(aid)
        ibs.get_annot_name_texts(aid)
        metadata.loc[metadata["File Name"] == ibs.get_annot_image_names(aid), "Predicted Name"] = name
    
    metadata.to_csv(csv_dir, index = False)