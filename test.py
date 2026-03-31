from ultralytics import YOLO
import cv2
import numpy as np
import math

# ======================
# CONFIG
# ======================
video_path = "video7.mp4"
detector_path = "basketball_analysis/models/player_detector.pt"
classifier_path = "runs/detect/train/weights/best.pt"
output_video = "resultat.mp4"

CONF_LOCK = 0.8
MAX_DISTANCE = 80
LOCKED_MAX_DISTANCE = 50
MAX_MISSING = 10
STABLE_FRAMES = 3

# ======================
# INIT
# ======================
detector = YOLO(detector_path)
classifier = YOLO(classifier_path)

cap = cv2.VideoCapture(video_path)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

out = cv2.VideoWriter(
    output_video,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

# ======================
# MEMORY
# ======================
players = {}
candidates = {}
used_labels = set()
next_id = 0

def center(box):
    x1, y1, x2, y2 = box
    return int((x1+x2)/2), int((y1+y2)/2)

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

frame_id = 0

# ======================
# LOOP
# ======================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1

    # ======================
    # DETECTION JOUEURS
    # ======================
    det_results = detector(frame, conf=0.3, verbose=False)
    boxes = det_results[0].boxes

    detections = []
    if boxes is not None:
        for box in boxes.xyxy.cpu().numpy():
            detections.append(box)

    updated_players = {}

    # ======================
    # MATCH TRACKING
    # ======================
    for box in detections:
        c = center(box)

        best_id = None
        min_d = 9999

        for pid, data in players.items():
            max_d = LOCKED_MAX_DISTANCE if data["locked"] else MAX_DISTANCE
            d = dist(c, data["center"])

            if d < min_d and d < max_d:
                min_d = d
                best_id = pid

        if best_id is not None:
            player = players[best_id]

            # ======================
            # CLASSIFICATION
            # ======================
            x1, y1, x2, y2 = map(int, box)
            crop = frame[y1:y2, x1:x2]

            cls_results = classifier(crop, verbose=False)

            if cls_results[0].boxes is not None:
                for cls, conf in zip(
                    cls_results[0].boxes.cls.cpu().numpy(),
                    cls_results[0].boxes.conf.cpu().numpy()
                ):
                    label = int(cls)

                    if label not in player["scores"]:
                        player["scores"][label] = 0

                    player["scores"][label] += conf

            # ======================
            # CHOISIR MEILLEUR LABEL
            # ======================
            if player["scores"]:
                best_label = max(player["scores"], key=player["scores"].get)

                # 🔒 éviter doublon
                if best_label not in used_labels:
                    player["label"] = best_label

                    # 🔥 LOCK
                    if player["scores"][best_label] >= CONF_LOCK:
                        player["locked"] = True
                        used_labels.add(best_label)

            updated_players[best_id] = {
                **player,
                "center": c,
                "last_seen": frame_id
            }

        else:
            # ======================
            # NOUVEAU JOUEUR (CANDIDAT)
            # ======================
            candidates[next_id] = {
                "center": c,
                "frames": 1,
                "scores": {},
                "label": None,
                "locked": False
            }
            next_id += 1

    # ======================
    # CLEAN MEMORY
    # ======================
    for pid, data in players.items():
        if frame_id - data["last_seen"] < MAX_MISSING:
            if pid not in updated_players:
                updated_players[pid] = data

    players = updated_players

    # ======================
    # DRAW (TON STYLE)
    # ======================
    annotated = frame.copy()

    for pid, p in players.items():
        x, y = p["center"]

        text = f"ID {pid}"
        if p["label"] is not None:
            text += f" | P{p['label']}"

        if p["locked"]:
            text += " 🔒"

        cv2.putText(annotated, text, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        cv2.circle(annotated, (x, y), 4, (0,255,0), -1)

    out.write(annotated)

cap.release()
out.release()
cv2.destroyAllWindows()

print("[+] Tracking + identification terminé")