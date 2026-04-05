
import cv2

class CourtKeypointDrawer:
    """
    Drawer for court keypoints - rectangles + labels
    """

    def draw(self, frames, court_keypoints):
        output_frames = frames.copy()

        box_size = 40  # 🔥 taille augmentée

        # mapping des classes
        class_names = {
            "class_0": "ball",
            "class_1": "player",
            "class_2": "hoop",
            "class_3": "terrain_corner",
            "class_4": "raquette_corner"
        }

        for i, frame in enumerate(output_frames):

            if i >= len(court_keypoints):
                continue

            keypoints = court_keypoints[i]

            for kp in keypoints:

                if not isinstance(kp, dict):
                    continue

                x = int(kp.get('x', 0))
                y = int(kp.get('y', 0))
                conf = kp.get('confidence', 0)
                name = kp.get('name', 'kp')

                # conversion nom classe lisible
                label_name = class_names.get(name, name)

                # centre -> rectangle
                x1 = x - box_size // 2
                y1 = y - box_size // 2
                x2 = x + box_size // 2
                y2 = y + box_size // 2

                # sécurité (éviter hors image)
                h, w = frame.shape[:2]
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w - 1, x2)
                y2 = min(h - 1, y2)

                # 🔵 couleur bleue
                color = (255, 0, 0)

                # rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # label
                label = f"{label_name}"

                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

                # confidence
                cv2.putText(
                    frame,
                    f"{conf:.2f}",
                    (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1
                )


        return output_frames