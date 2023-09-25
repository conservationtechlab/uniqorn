import cv2
import matplotlib.pyplot as plt
import pickle
from tqdm import tqdm


def get_features(img_file_name):
    """ Get features of master images

        Args:
            img_file_name(list): Master image
        Returns:
            keypoints, descriptors, img
    """
    img = cv2.imread(img_file_name)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()

    kps, des = sift.detectAndCompute(img, None)

    features = [kps, des]

    return features


def plot_features(img_path):
    """ Plot features for a single image

        Args:
            img_path (str): path to image file
        Returns:
            None, plots matplotlib image
    """
    img1 = cv2.imread(img_path)
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()
    keypoints_1, descriptors_1 = sift.detectAndCompute(img1, None)

    img_1 = cv2.drawKeypoints(gray1, keypoints_1, img1)
    plt.imshow(img_1)


def compare(img_path1, img_path2, n=50):
    """ Plot matching features for a pair of images

        Args:
            img_path1 (str): path to first image file
            img_path2 (str): path to second image file
            n (int): plot first n matching features, default=50
        Returns:
            None, plots matplotlib image
    """
    img1 = cv2.imread(img_path1)
    img2 = cv2.imread(img_path2)

    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()

    keypoints_1, descriptors_1 = sift.detectAndCompute(img1, None)
    keypoints_2, descriptors_2 = sift.detectAndCompute(img2, None)

    # feature matching
    bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

    matches = bf.match(descriptors_1, descriptors_2)
    matches = sorted(matches, key=lambda x: x.distance)

    img3 = cv2.drawMatches(img1, keypoints_1, img2, keypoints_2,
                           matches[:n], img2, flags=2)
    plt.imshow(img3)
    plt.show()


def extract_sift(data, output_file=None):
    """ Get keypoints and descriptors for list of images

        Args:
            data (list): vector of image paths
            output_file (str): path to save outputs, default=None
        Returns:
            sources (dict): list of keypoints and descriptors for each image
    """
    sources = {}

    for i, row in tqdm(enumerate(data)):
        features = get_features(row)
        # list keypoint
        keypoints = []
        for p in features[0]:
            temp = (p.pt, p.size, p.angle, p.response, p.octave, p.class_id)
            keypoints.append(temp)

        # Convert keypoints to bytes
        map(bytes, keypoints)
        # Dictionary of feature point information
        sources[i] = {
            "src": row,
            "keypoint": keypoints,
            "descriptor": features[1],
        }

    # Write feature point information to a file
    if output_file:
        with open(output_file, mode="wb") as f:
            pickle.dump(sources, f)

    return sources
