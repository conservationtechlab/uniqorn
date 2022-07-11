from ibeis.algo.verif.pairfeat import PairwiseFeatureExtractor
from ibeis.control.manual_annot_funcs import *  
import ibeis
import pandas as pd
import itertools as it
import info_to_csv
import edit_info_in_ibeis



database_name = "tinyDB" # IBEIS Database name to work on
photo_directory = "/home/yuerou/tiny/" #  File Path of the folder containing all the photos
stations_directory = "~/code/station_data_peru.csv" # File path of the csv containing the coordinates of the stations
images_summary_directory = "~/code/JaguarImagesSummary.csv" # File path of the csv containing all the metadata of the images, including station and survey number
csv_destination_dir = "/home/yuerou/500.csv " # File path of the csv generated 

def clustering_func(all_required_edges, lst_of_same_individual):
    '''
    Takes in all edges that needs a comparison/evaluation. 
    Returns a list of paired individuals. 
    '''
    ibs = ibeis.opendb(database_name)
    #match_config = {"ratio_thresh": 0.65}
    extr = PairwiseFeatureExtractor(ibs)

    # Extract pairwise features for every requested pair of annotations
    matches = extr._exec_pairwise_match(all_required_edges)

    for match in matches:
        aid1 = match.annot1['aid']
        aid2 = match.annot2['aid']
        # Sum the fs (feature score) to get a simplified scalar score for each pair
        score = match.fs.sum()
        if (score > 0) :
            lst_of_same_individual.append((aid1, aid2))
    
    return lst_of_same_individual




def connect(db_name, lst_of_same_individual, modify_db = False):
    '''
    Think of each aid as a node and each tuple as an edge. Goal: find all the connected components
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



def workflow(database_name, photo_directory, stations_directory, images_summary_directory, csv_destination_dir):
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
        
    print(all_required_edges)

    lst_of_same_individual = clustering_func(all_required_edges, lst_of_same_individual) # Obtains a list of tuples of matches

    connect(database_name, lst_of_same_individual, modify_db= True) # Traverse the list of tuples to mark all connected components as the same individual


        




if __name__ == '__main__':
   workflow(database_name, photo_directory, stations_directory, images_summary_directory, csv_destination_dir)






