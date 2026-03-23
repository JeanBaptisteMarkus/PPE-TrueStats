from ultralytics import YOLO
import cv2

# 🔹 Chemin vers ton modèle entraîné
model_path = "models/panier.pt"
model = YOLO(model_path)

# 🔹 Vidéo d'entrée et de sortie
video_input = "video_1.mp4"
video_output = "output_detected.mp4"

# 🔹 Ouvrir la vidéo
cap = cv2.VideoCapture(video_input)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(video_output, fourcc, fps, (width, height))

print("[*] Début de la détection...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 🔹 Prédiction YOLO sur la frame
    results = model.predict(frame)

    # 🔹 Dessiner uniquement si un panier est détecté
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()  # coordonnées des bounding boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            # rectangle vert
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # cercle rouge au centre
            cx, cy = (x1 + x2)//2, (y1 + y2)//2
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    out.write(frame)

cap.release()
out.release()
print(f"[+] Vidéo finale enregistrée : {video_output}")