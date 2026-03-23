from ultralytics import YOLO


class BasketDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_baskets(self, video_frames):
        """
        Detecte les paniers sur chaque frame
        retourne une liste de detections par frame
        """

        all_detections = []

        for frame in video_frames:

            results = self.model.predict(frame, verbose=False)

            frame_boxes = []

            for r in results:
                boxes = r.boxes.xyxy.cpu().numpy()

                for box in boxes:
                    x1, y1, x2, y2 = map(int, box)

                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    frame_boxes.append({
                        "bbox": [x1, y1, x2, y2],
                        "center": [cx, cy]
                    })

            all_detections.append(frame_boxes)

        return all_detections