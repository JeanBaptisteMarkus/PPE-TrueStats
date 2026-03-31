from ultralytics import YOLO
import cv2
import numpy as np
import math

# ======================
# CONFIG
# ======================
video_path = "video7.mp4"
model_path = "runs/detect/train/weights/best.pt"
output_video = "resultat.mp4"

CONF_THRESHOLD = 0.8
MAX_DISTANCE = 80
LOCKED_MAX_DISTANCE = 50  # 🔥 plus strict pour ID verrouillés
MAX_MISSING = 10
STABLE_FRAMES = 3

# ======================
# INIT
# ======================
model = YOLO(model_path)

cap = cv2.VideoCapture(video_path)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# ======================
# MEMOIRE
# ======================
players_memory = {}
candidates = {}
next_id = 0

def get_center(box):
    x1, y1, x2, y2 = box
    return int((x1 + x2) / 2), int((y1 + y2) / 2)

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

frame_id = 0

# ======================
# LOOP
# ======================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1

    results = model.track(
        source=frame,
        persist=True,
        conf=0.3,
        iou=0.5
    )

    boxes = results[0].boxes

    detections = []
    if boxes is not None:
        for box, conf in zip(boxes.xyxy.cpu().numpy(), boxes.conf.cpu().numpy()):
            center = get_center(box)
            detections.append((center, conf, box))

    updated_memory = {}

    # ======================
    # MATCH AVEC JOUEURS VALIDÉS
    # ======================
    for center, conf, box in detections:
        best_id = None
        min_dist = 9999

        for pid, data in players_memory.items():
            dist = distance(center, data["center"])

            # 🔒 SI LOCK → distance plus stricte
            max_dist = LOCKED_MAX_DISTANCE if data.get("locked", False) else MAX_DISTANCE

            if dist < min_dist and dist < max_dist:
                min_dist = dist
                best_id = pid

        if best_id is not None:
            updated_memory[best_id] = {
                "center": center,
                "last_seen": frame_id,
                "locked": players_memory[best_id].get("locked", False)
            }

        else:
            # ======================
            # CANDIDATS
            # ======================
            added = False

            for cid, data in candidates.items():
                dist = distance(center, data["center"])
                if dist < MAX_DISTANCE:
                    data["center"] = center
                    data["frames"] += 1
                    data["conf"] = max(data["conf"], conf)

                    # 🔥 VALIDATION
                    if data["frames"] >= STABLE_FRAMES and data["conf"] >= CONF_THRESHOLD:
                        players_memory[next_id] = {
                            "center": center,
                            "last_seen": frame_id,
                            "locked": True  # 🔒 verrouillé direct
                        }
                        next_id += 1
                        del candidates[cid]
                    added = True
                    break

            if not added:
                candidates[len(candidates)] = {
                    "center": center,
                    "frames": 1,
                    "conf": conf
                }

    # ======================
    # GARDER MEMOIRE
    # ======================
    for pid, data in players_memory.items():
        if frame_id - data["last_seen"] < MAX_MISSING:
            if pid not in updated_memory:
                updated_memory[pid] = data

    players_memory = updated_memory

    # ======================
    # DRAW ORIGINAL
    # ======================
    annotated_frame = results[0].plot()
    out.write(annotated_frame)

cap.release()
out.release()
cv2.destroyAllWindows()

print("[+] Tracking avec ID verrouillés terminé :", output_video)