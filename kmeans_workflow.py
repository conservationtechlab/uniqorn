from inspect import classify_class_attrs
from ibeis.algo.verif.pairfeat import PairwiseFeatureExtractor
from ibeis.control.manual_annot_funcs import *  
import ibeis
import pandas as pd
import itertools as it
from utils import workflow
import itertools as it
from sklearn.cluster import KMeans

# Cluster all the features with the number of clusters based on dendrogram    

database_name = sys.argv[1] # IBEIS Database name to work on
photo_directory = sys.argv[2] #  File Path of the folder containing all the photos
stations_directory = sys.argv[3] # File path of the csv containing the coordinates of the stations
images_summary_directory = sys.argv[4] # File path of the csv containing all the metadata of the images, including station and survey number
csv_destination_dir = sys.argv[5] # File path of the csv generated 


# database_name = "tinyDB" # IBEIS Database name to work on
# photo_directory = "/home/yuerou/tiny/" #  File Path of the folder containing all the photos
# stations_directory = "~/code/station_data_peru.csv" # File path of the csv containing the coordinates of the stations
# images_summary_directory = "~/code/JaguarImagesSummary.csv" # File path of the csv containing all the metadata of the images, including station and survey number
# csv_destination_dir = "/home/yuerou/500.csv " # File path of the csv generated 


def clustering_func(all_required_edges, lst_of_same_individual):
    '''
    Takes in all edges that needs a comparison/evaluation and the list of same individuals already determined.
    Returns a complete list of individuals based on the clsutering algorithm. 
    KMeans takes in an stacked array of all feature vectors, cluster them based on a pre-determined number of clusters. 
    '''
    ibs = ibeis.opendb(database_name)

    # The matrix that will contain all the stacked vectors. 
    matrix = np.array([])

    # DF that contains the aid of the vectors.
    feat_df = pd.DataFrame({"aid":[]})

    for aid in ibs.get_valid_aids():
        feat = ibs.get_annot_vecs(aid)
        if (matrix.size == 0):
            matrix = feat
        else:
            matrix = np.vstack([matrix, feat])
        print(aid)
        for i in range(len(feat)):
            feat_df.loc[len(feat_df.index)] = [aid]

    clustering = KMeans(n_clusters=30).fit(matrix)
    feat_df["Label"] = clustering.labels_
    feat_df.to_csv("feat_df.csv")

    all_edges_need_inspection = []
    comb = list(it.combinations(list(ibs.annots()), 2))

    for edge in comb:
        if (ibs.get_annot_name_texts(edge[0]) != ibs.get_annot_name_texts(edge[1])) & ((ibs.get_annot_viewpoint_code([edge[0]]) == ibs.get_annot_viewpoint_code([edge[1]]))):
            all_edges_need_inspection.append(edge)
        

    for edge in all_edges_need_inspection:
        aid1 = edge[0]
        aid2 = edge[1]
        aid1_feats = np.unique(feat_df[feat_df["aid"] == aid1]["Label"].tolist()) # All labels that aid1 has 
        aid2_feats = np.unique(feat_df[feat_df["aid"] == aid2]["Label"].tolist())
        common_feat_count = 0 # if >=10 --> group!
        for i in aid1_feats:
            for j in aid2_feats:
                if i == j:
                    common_feat_count += 1
        if (common_feat_count >=10) & ((aid1, aid2) not in lst_of_same_individual) & ((aid2, aid1) not in lst_of_same_individual): # They are the same! 
            lst_of_same_individual.append((edge))

    return lst_of_same_individual


if __name__ == '__main__':
    workflow(database_name, photo_directory, stations_directory, images_summary_directory, csv_destination_dir, clustering_func)






