from ultralytics import YOLO
import sys
import numpy as np
import cv2
import pickle
sys.path.append('../')
from utils import read_stub, save_stub

class CourtKeypointDetector:
    """
    Detect court keypoints using a YOLO model with enhanced detection and augmentation.
    """
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def _convert_detection_to_keypoints(self, detection, conf_threshold=0.2):
        """
        Convert YOLO detection to list of keypoints, using uniform conf_threshold.
        """
        keypoints_list = []

        try:
            if not hasattr(detection, 'keypoints') or detection.keypoints is None:
                return keypoints_list

            kp_data = detection.keypoints

            # Format Ultralytics
            if hasattr(kp_data, 'xy') and kp_data.xy is not None:
                xy = kp_data.xy
                conf = kp_data.conf if hasattr(kp_data, 'conf') else None

                if len(xy) > 0 and len(xy[0]) > 0:
                    for i in range(len(xy[0])):
                        x = float(xy[0][i][0].cpu().numpy()) if hasattr(xy[0][i][0], 'cpu') else float(xy[0][i][0])
                        y = float(xy[0][i][1].cpu().numpy()) if hasattr(xy[0][i][1], 'cpu') else float(xy[0][i][1])

                        confidence = 0.0
                        if conf is not None and len(conf) > 0 and len(conf[0]) > i:
                            confidence = float(conf[0][i].cpu().numpy()) if hasattr(conf[0][i], 'cpu') else float(conf[0][i])

                        if confidence < conf_threshold:
                            continue

                        keypoints_list.append({
                            'x': x,
                            'y': y,
                            'confidence': confidence,
                            'name': f"kp_{i}",
                            'estimated': False
                        })

            elif hasattr(kp_data, 'data') and kp_data.data is not None:
                data = kp_data.data
                if len(data.shape) >= 2:
                    if len(data.shape) == 3:
                        data = data[0]

                    for i in range(len(data)):
                        x = float(data[i][0].cpu().numpy()) if hasattr(data[i][0], 'cpu') else float(data[i][0])
                        y = float(data[i][1].cpu().numpy()) if hasattr(data[i][1], 'cpu') else float(data[i][1])
                        confidence = float(data[i][2].cpu().numpy()) if hasattr(data[i][2], 'cpu') else float(data[i][2])

                        if confidence < conf_threshold:
                            continue

                        keypoints_list.append({
                            'x': x,
                            'y': y,
                            'confidence': confidence,
                            'name': f"kp_{i}",
                            'estimated': False
                        })

        except Exception as e:
            print("Erreur conversion keypoints:", e)

        # Trier par confiance
        keypoints_list = sorted(keypoints_list, key=lambda x: x["confidence"], reverse=True)
        return keypoints_list

    def get_court_keypoints(self, frames, read_from_stub=False, stub_path=None, conf_threshold=0.2):
        """
        Detect court keypoints for a batch of frames with augmentation and frame enhancement.
        """
        # Lire depuis stub
        court_keypoints = read_stub(read_from_stub, stub_path)
        if court_keypoints is not None and len(court_keypoints) == len(frames):
            print(f"✓ Keypoints chargés depuis stub: {len(court_keypoints)} frames")
            return court_keypoints

        # Détection
        court_keypoints = []
        batch_size = 20
        print("🔍 Détection des keypoints du terrain...")

        for i in range(0, len(frames), batch_size):
            batch_frames = frames[i:i+batch_size]

            # Prétraitement des frames
            batch_frames_enh = [self._enhance_frame(f) for f in batch_frames]

            try:
                results = self.model.predict(
                    batch_frames_enh,
                    conf=conf_threshold,
                    iou=0.5,
                    verbose=False,
                    device='cpu'
                )

                for j, result in enumerate(results):
                    frame_keypoints = self._convert_detection_to_keypoints(result, conf_threshold)
                    court_keypoints.append(frame_keypoints)

            except Exception as e:
                print(f"  ❌ Erreur batch: {e}")
                for _ in range(len(batch_frames)):
                    court_keypoints.append([])

        # Forward-fill keypoints manquants
        last_kp = None
        for idx, frame_kp in enumerate(court_keypoints):
            if not frame_kp and last_kp:
                # Reprendre la dernière frame valide
                court_keypoints[idx] = [{'x': kp['x'], 'y': kp['y'], 'confidence': kp['confidence'],
                                         'name': kp['name'], 'estimated': True} for kp in last_kp]
            elif frame_kp:
                last_kp = frame_kp

        # Statistiques
        non_empty = sum(1 for kp in court_keypoints if len(kp) > 0)
        total_keypoints = sum(len(kp) for kp in court_keypoints)
        print(f"\n📊 Statistiques de détection:")
        print(f"  - Frames traitées: {len(court_keypoints)}")
        print(f"  - Frames avec keypoints: {non_empty}")
        print(f"  - Total keypoints détectés: {total_keypoints}")
        if non_empty > 0:
            print(f"  - Moyenne par frame: {total_keypoints/non_empty:.1f}")

        if stub_path:
            save_stub(stub_path, court_keypoints)
            print(f"✓ Keypoints sauvegardés dans: {stub_path}")

        return court_keypoints

    @staticmethod
    def _enhance_frame(frame):
        """
        Convert frame to gray + CLAHE for better keypoint detection.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)