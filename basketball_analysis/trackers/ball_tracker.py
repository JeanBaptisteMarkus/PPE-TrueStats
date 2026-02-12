from ultralytics import YOLO
import supervision as sv
import numpy as np
import pandas as pd
import sys
sys.path.append("../")
from utils import read_stub, save_stub

class BallTracker:
    def __init__(self, model_path):
        self.model=YOLO(model_path)
    
    def detect_frames(self, frames):
        betch_size = 20
        detections = []
        for i in range(0, len(frames), betch_size):
            batch_frames = frames[i:i + betch_size]
            batch_detections = self.model.predict(batch_frames, conf=0.5)
            detections+=batch_detections
        return detections

    def get_objects_tracks(self, frames, read_from_stub=False, stub_path=None):

        tracks = read_stub(read_from_stub, stub_path)
        if tracks is not None:
            if len(tracks) == len(frames):
                return tracks 
            
        detections = self.detect_frames(frames)
        tracks = []

        for frame_num,detection in enumerate(detections):
            cls_names = detection.names

            # on remplace la clé et la valeur des names ; par exemple, on a en sortie avec YOLO la liste :
            # names: {0: 'person', 1: 'bicycle', ...}
            # qui va devenir :
            # names: {'person': 0, 'bicycle': 1, ...}
            cls_names_inv = {v:k for k,v in cls_names.items()} 

            detection_supervision = sv.Detections.from_ultralytics(detection)
            tracks.append({})
            chosen_bbox=None
            max_confidence=0

            for frame_detection in detection_supervision:
                bbox=frame_detection[0].tolist()
                cls_id=frame_detection[3]
                confidence=frame_detection[2]

                if cls_id == cls_names_inv['Ball']:
                    if max_confidence < confidence:
                        chosen_bbox=bbox
                        max_confidence=confidence

            if chosen_bbox is not None:
                tracks[frame_num][1]={"bbox": chosen_bbox}
        

        save_stub(stub_path, tracks)
        return tracks
    
    def remove_wrong_detections(self, ball_positions):
        maximum_allowed_distance = 25
        last_good_frame_index = -1

        for i in range(len(ball_positions)):
            current_box = ball_positions[i].get(1,{}).get("bbox", [])

            if len(current_box) == 0:
                continue

            if last_good_frame_index == -1:
                last_good_frame_index = i
                continue
            last_good_box = ball_positions[last_good_frame_index].get(1,{}).get("bbox", [])
            frame_gap = i - last_good_frame_index
            adjusted_max_distance = maximum_allowed_distance * frame_gap

            # Calculate the distance between the last good bbxo and the current position
            if np.linalg.norm(np.array(last_good_box[:2]) - np.array(current_box[:2])) > adjusted_max_distance:
                ball_positions[i] = {}
            else:
                last_good_frame_index = i

        return ball_positions
    
    def interpolate_ball_positions(self, ball_positions):
        ball_positions = [x.get(1,{}).get("bbox", []) for x in ball_positions]
        df_ball_positions = pd.DataFrame(ball_positions, columns=["x1", "y1", "x2", "y2"])

        #Interpolate missing values
        df_ball_positions = df_ball_positions.interpolate()
        df_ball_positions = df_ball_positions.bfill()

        ball_positions = [{1:{"bbox":x}} for x in df_ball_positions.to_numpy().tolist()]

        return ball_positions