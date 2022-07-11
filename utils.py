import numpy as np
from ibeis.control.manual_annot_funcs import *  
import ibeis
import edit_info_in_ibeis
import info_to_csv
import itertools as it



# Utility functions

def list_to_tuple(same_annot_from_feat_list): 
    '''
    Generate a list of tuples of the combination of the elements from an input list 
    '''
    tuples = []
    for i in range(int(len(same_annot_from_feat_list)/2)):
        tuples.append((same_annot_from_feat_list[2*i], same_annot_from_feat_list[2*i+1]))
    if ((len(same_annot_from_feat_list)%2 != 0) & (len(same_annot_from_feat_list) >1)):
            tuples.append((same_annot_from_feat_list[len(same_annot_from_feat_list)-2], same_annot_from_feat_list[len(same_annot_from_feat_list)-1]))


    return tuples


def connect(db_name, lst_of_same_individual, modify_db = False):
    '''
    Think of each aid as a node and each tuple as an edge. Goal: find all the connected components. Edit the results in IBEIS.
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
        counter = 0
        for key in connected_components:
            ibs.set_annot_names(connected_components[key], [str(counter) for i in range(len(connected_components[key]))])
            counter += 1
    else:
        return connected_components


def workflow(database_name, photo_directory, stations_directory, images_summary_directory, csv_destination_dir, clustering_func):
    '''
    The complete workflow for extracting names from csv, computing matches and editing names in ibeis
    '''
    # Generate a csv with name name, GPS, time, viewpoint and individual name based on GPS and time
    info_to_csv.integrating_info(photo_directory, stations_directory, images_summary_directory, csv_destination_dir)

    # Plug in the names to IBEIS
    edit_info_in_ibeis.edit_info_in_ibeis(database_name, csv_destination_dir)

    ibs = ibeis.opendb(database_name)


    # Find all permutations of aids except aids under the same individual
    all_required_edges = [] # All edges that requires inspection
    all_comb = list(it.combinations(list(ibs.annots()), 2))
    lst_of_same_individual = [] # List for storing aids of the same individual

    for edge in all_comb:
        if (ibs.get_annot_name_texts(edge[0]) != ibs.get_annot_name_texts(edge[1])) & ((edge[1], edge[0]) not in all_required_edges) & ((ibs.get_annot_viewpoint_code([edge[0]]) == ibs.get_annot_viewpoint_code([edge[1]]))):
            all_required_edges.append(edge)
        elif (ibs.get_annot_name_texts(edge[0]) == ibs.get_annot_name_texts(edge[1])) & ((edge[1], edge[0]) not in lst_of_same_individual):
            lst_of_same_individual.append(edge)
        
    lst_of_same_individual = clustering_func(all_required_edges, lst_of_same_individual) # Obtains a list of tuples of matches

    connect(database_name, lst_of_same_individual, modify_db= True) # Traverse the list of tuples to mark all connected components as the same individual