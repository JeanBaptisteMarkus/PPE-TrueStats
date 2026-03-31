from ultralytics import YOLO
import sys
sys.path.append('../')
from utils import read_stub, save_stub

class CourtKeypointDetector:

    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def get_court_keypoints(self, frames, read_from_stub=False, stub_path=None, conf_threshold=0.1):

        # Stub
        court_keypoints = read_stub(read_from_stub, stub_path)
        if court_keypoints is not None and len(court_keypoints) == len(frames):
            print(f"✓ Keypoints chargés depuis stub: {len(court_keypoints)} frames")
            return court_keypoints

        court_keypoints = []
        print("🔍 Détection (mode detect -> bbox centers)...")

        for frame in frames:
            try:
                results = self.model(frame, conf=conf_threshold, verbose=False)
                r = results[0]

                frame_kps = []

                if r.boxes is not None:
                    boxes = r.boxes

                    for i in range(len(boxes)):
                        xyxy = boxes.xyxy[i].cpu().numpy()
                        conf = float(boxes.conf[i].cpu().numpy())
                        cls = int(boxes.cls[i].cpu().numpy())

                        x1, y1, x2, y2 = xyxy

                        # 👉 centre de la bbox = pseudo keypoint
                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2

                        frame_kps.append({
                            'x': float(cx),
                            'y': float(cy),
                            'confidence': conf,
                            'name': f"class_{cls}",
                            'estimated': False
                        })

                court_keypoints.append(frame_kps)

            except Exception as e:
                print("❌ Erreur:", e)
                court_keypoints.append([])

        if stub_path:
            save_stub(stub_path, court_keypoints)

        return court_keypoints