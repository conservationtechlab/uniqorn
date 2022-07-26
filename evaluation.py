import pandas as pd
import re
from sklearn.metrics.cluster import rand_score
import ibeis
from ibeis.control.manual_annot_funcs import * 
from scipy.special import comb 
import itertools as it


def evaluate(db_name, aid_list = None):
    ''' Returns tp, tn, fp, fn of the clustering compared with the true grouping (extracted from the file name)
    Args: 
        db_name: Name of the database to evaluate
    Returns:
        list: a list of true positive, true negative, false positive, false negative counts. These were calculated on pairs of points. For example, true positive is the number of pairs of annotations that are in the same group in the true/real grouping and in the same group in the predicted grouping. 
    '''
    true_names = {}
    true_names_lst = []
    predicted_names = {}
    predicted_names_lst = []
    ibs = ibeis.opendb(db_name)
    if (aid_list == None):
        aid_list = ibs.get_valid_aids()


    for aid in aid_list:
        image_name = ibs.get_annot_image_names(aid)
        individual_name = re.findall("P\w\w\s\d\d", image_name) # Extract True Names
        if individual_name != []:
            true_names[aid] = individual_name[0]
            true_names_lst.append(individual_name[0])
            predicted_name = ibs.get_annot_name_texts(aid)
            predicted_names_lst.append(predicted_name)
            predicted_names[aid] = predicted_name
    
    return evaluate_components(true_names, predicted_names), true_names_lst, predicted_names_lst


def evaluate_components(true_names, predicted_names):
    ''' 
    Args:
        true_names: dictionary of true names. key: aid of the corresponding image. Value: Actual name of the jaguar
        predicted_name: dictionary of predicted names. key: aid of the corresponding image. Value: Predicted name of the jaguar
    Returns:
        list: a list of true positive, true negative, false positive, false negative counts. 
    
    '''
    unique_classification_names, unique_classfication_counts = np.unique(list(predicted_names.values()), return_counts = True)
    tp_plus_fp = comb(unique_classfication_counts, 2).sum() # np.bincount will return a list of the count of the labels. Then do N choose 2 on each of the labels to get the total number of possible pairs inside each label, and then sum the total number of pairs up.
    unique_true_names, true_name_val_counts = np.unique(list(true_names.values()), return_counts = True)
    tp_plut_fn = comb(true_name_val_counts, 2).sum()
    num_of_individuals = len(true_names)
    pair_indices = list(it.combinations(list(true_names.keys()), 2))
    tp = 0
    for pair_index in pair_indices:
        first_index = pair_index[0]
        second_index = pair_index[1]
        if (true_names[first_index] == true_names[second_index]) & (predicted_names[first_index] == predicted_names[second_index]):
            tp += 1
    
    fp = tp_plus_fp - tp
    fn = tp_plut_fn - tp
    tn = comb(num_of_individuals, 2) - tp - fn -fp
    return [tp, tn, fp, fn]

    
    
    














