from ibeis.algo.verif.pairfeat import PairwiseFeatureExtractor
from ibeis.control.manual_annot_funcs import *  
import ibeis
from utils import workflow, list_to_tuple
import itertools as it
from sklearn.cluster import DBSCAN


# Cluster with a precomputed dissimilarity matrix of the images

database_name = sys.argv[1] # IBEIS Database name to work on
photo_directory = sys.argv[2] #  File Path of the folder containing all the photos
stations_directory = sys.argv[3] # File path of the csv containing the coordinates of the stations
images_summary_directory = sys.argv[4] # File path of the csv containing all the metadata of the images, including station and survey number
csv_destination_dir = sys.argv[5] # File path of the csv generated 

def clustering_func(all_required_edges, lst_of_same_individual):
    '''
    Takes in all edges that needs a comparison/evaluation. 
    Returns a list of paired individuals.
    '''
    ibs = ibeis.opendb(database_name)
    #match_config = {"ratio_thresh": 0.65}
    extr = PairwiseFeatureExtractor(ibs)
    all_required_annots = list(set(it.chain.from_iterable(all_required_edges))) # Since a matrix is needed, must extract all pairwise scores 
    # Extract pairwise features for every requested pair of annotations


    dist_matrix = np.zeros((len(all_required_annots), len(all_required_annots)))

    # Fills the dissimilarity matrix
    for pair in list(it.combinations(all_required_annots, 2)):
        print(pair)
        match = extr._exec_pairwise_match([pair])[0]   
        score = 100 * (1 - (len(match.fs)/min(match.annot1['kpts'].shape[0],match.annot2['kpts'].shape[0] )))
        dist_matrix[all_required_annots.index(pair[0]), all_required_annots.index(pair[1])] = score
        dist_matrix[all_required_annots.index(pair[1]), all_required_annots.index(pair[0])] = score

    clustering = DBSCAN(metric = 'precomputed').fit(dist_matrix)
    labels = clustering.labels_

    # Put images with the same label into one list in the dictionary
    same_individual_lst = {}
    for i in range(len(labels)):
        if labels[i] not in same_individual_lst.keys():
            same_individual_lst[labels[i]] = [all_required_annots[i]]
        else:
            same_individual_lst[labels[i]].append(all_required_annots[i])
    
    # Add the tuples back into lst_of_same_individuals
    for same_individual in same_individual_lst.values():
        same_individual_tuple_lst = list_to_tuple(same_individual)
        for tuple in same_individual_tuple_lst:
            first_elem = tuple[0]
            second_elem = tuple[1]
            if ((first_elem, second_elem) not in lst_of_same_individual) & ((second_elem, first_elem) not in lst_of_same_individual) & (ibs.get_annot_viewpoint_code([first_elem]) == ibs.get_annot_viewpoint_code([second_elem])) :
                lst_of_same_individual.append((first_elem, second_elem))


    return lst_of_same_individual


if __name__ == '__main__':
   workflow(database_name, photo_directory, stations_directory, images_summary_directory, csv_destination_dir, clustering_func)






