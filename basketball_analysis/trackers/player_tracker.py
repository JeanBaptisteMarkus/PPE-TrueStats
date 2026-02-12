from ultralytics import YOLO
import supervision as sv
import sys
sys.path.append("../")
from utils import read_stub, save_stub

class PlayerTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()

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

            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks.append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv["Player"]:
                    tracks[frame_num][track_id] = {"bbox": bbox}

        save_stub(stub_path, tracks)

        return tracks