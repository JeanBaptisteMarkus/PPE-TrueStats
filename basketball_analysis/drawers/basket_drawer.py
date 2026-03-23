import cv2

class BasketDrawer:

    def draw(self, frames, basket_detections):

        output_frames = []

        for frame, detections in zip(frames, basket_detections):

            frame = frame.copy()

            for det in detections:

                x1, y1, x2, y2 = det["bbox"]
                cx, cy = det["center"]

                # rectangle vert
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                # centre du panier
                cv2.circle(
                    frame,
                    (cx, cy),
                    5,
                    (0, 0, 255),
                    -1
                )

            output_frames.append(frame)

        return output_frames