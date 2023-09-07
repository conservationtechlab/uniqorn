import matplotlib.pyplot as plt
import numpy as np
import torch
import os
import cv2
from segment_anything import sam_model_registry
from segment_anything import SamPredictor


def convert_MD_to_SAM(row):
    """ Convert relative bbox coords to absolute

        Args:
            row (list): row from dataframe assuming bbox, h and w
        Returns:
            list of absolute px coordinates [left,top,right,bottom]
    """
    left = row['bbox1'] * row['width']
    top = row['bbox2'] * row['height']
    right = left + (row['bbox3'] * row['width'])
    bottom = top + (row['bbox4'] * row['height'])
    return [int(left), int(top), int(right), int(bottom)]


def load_SAM(model, GPU='cuda:0', MODEL_TYPE="vit_h"):
    """ Load SAM onto gpu

        Args:
            model (str): path to model checkpoint
        Returns:
            SamPredictor
    """
    DEVICE = torch.device(GPU if torch.cuda.is_available() else 'cpu')
    print(DEVICE)

    sam = sam_model_registry[MODEL_TYPE](checkpoint=model)
    sam.to(device=DEVICE)

    return SamPredictor(sam)


def segment_data(data, mask_dir, sam_predictor):
    """ Segment crops and save as .png

        Args:
            data (DataFrame): assumes file_path, md bbox, h, w
            mask_dir (str): path to save segmented images
            sam_predictor (SamPredictor object)
        Returns:
            None, saves segmented images
    """
    for i, row in data.iterrows():
        path = row['file_path']
        box = convert_MD_to_SAM(row)

        mask_path = mask_dir + os.path.splitext(os.path.basename(path))[0] + '.png'
        data.loc[i, 'mask_path'] = mask_path

        image_bgr = cv2.imread(path)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        sam_predictor.set_image(image_rgb)

        masks, scores, logits = sam_predictor.predict(
                box=np.array(box),
                multimask_output=False)

        m = masks.astype(np.uint8)[0]
        combined = cv2.bitwise_and(image_bgr, image_bgr, mask=m)
        crop = combined[box[1]:box[3], box[0]:box[2]]
        # create image
        plt.axis('off')
        plt.imshow(crop)
        plt.savefig(mask_path, bbox_inches='tight', pad_inches=0.0)

    return data
