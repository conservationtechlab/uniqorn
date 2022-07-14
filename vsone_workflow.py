from os import symlink
from ibeis.algo.verif.pairfeat import PairwiseFeatureExtractor
from ibeis.control.manual_annot_funcs import *  
import ibeis
from utils import workflow
import sys


database_name = sys.argv[1] # IBEIS Database name to work on
photo_directory = sys.argv[2] #  File Path of the folder containing all the photos
stations_directory = sys.argv[3] # File path of the csv containing the coordinates of the stations
images_summary_directory = sys.argv[4] # File path of the csv containing all the metadata of the images, including station and survey number
csv_destination_dir = sys.argv[5] # File path of the csv generated 
symlink_dir = sys.argv[6] # Directory for manual review 


def clustering_func(all_required_edges, lst_of_same_individual):
    ''' Computes the dissimilarity score and cluster based on the dissimilarity matrix. 
  
    Args: 
        all_required_edges: A list of tuples of edges that requires inspection by the algorithm
        lst_of_same_individual: A list of tuples of edges that are confirmed to be the same individual determined by time and GPS. 
    Returns:
        list: A complete list of edges that are determined to be the same individual based on the clustering algorithm and time and GPS. 
    '''
    
    ibs = ibeis.opendb(database_name)
    #match_config = {"ratio_thresh": 0.65}
    extr = PairwiseFeatureExtractor(ibs)

    # Extract pairwise features for every requested pair of annotations
    matches = extr._exec_pairwise_match(all_required_edges)

    for match in matches:
        aid1 = match.annot1['aid']
        aid2 = match.annot2['aid']
        # Sum the fs (feature score) to get a scalar score for each pair
        score = match.fs.sum()
        if (score > 0) :
            lst_of_same_individual.append((aid1, aid2))
    
    return lst_of_same_individual


if __name__ == '__main__':
   workflow(database_name, photo_directory, stations_directory, images_summary_directory, csv_destination_dir, clustering_func, symlink_dir)






