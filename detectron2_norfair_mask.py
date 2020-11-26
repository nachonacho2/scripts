import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()
# import some common libraries
import numpy as np
import tqdm
import cv2
import os

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.video_visualizer import VideoVisualizer
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2.data import MetadataCatalog
import time
import pickle

# import norfair
from norfair import Detection, Tracker, Video, draw_tracked_objects, draw_masks

# Set up Detectron2 object detector
cfg = get_cfg()
cfg.merge_from_file("./detectron2_config.yaml")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.WEIGHTS = "detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl"
detector = DefaultPredictor(cfg)

# Distance function
def centroid_distance(detection, tracked_object):
    return np.linalg.norm(detection.points - tracked_object.estimate)

# Norfair
video = Video(input_path="./video.mp4")
tracker = Tracker(distance_function=centroid_distance, distance_threshold=20)

for frame in video:
    detections = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # Wrap Detectron2 detections in Norfair's Detection objects
    detections = [
        Detection(p)
        for p, c in
        zip(detections["instances"].pred_boxes.get_centers().cpu().numpy(),
            detections["instances"].pred_classes)
        if c == 2
    ]
    tracked_objects = tracker.update(detections=detections)
    draw_tracked_objects(frame, tracked_objects)
    draw_masks(frame, detections)
    video.write(frame)