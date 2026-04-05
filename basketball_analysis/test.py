import os
import shutil
import random
from ultralytics import YOLO
import cv2

# ================================
# 1️⃣ Chemins à modifier
# ================================
dataset_folder = "Mk_panier"       # dossier avec images + .txt
dataset_dir = "dataset"             # dossier final YOLOv8
video_input = "video_1.mp4"      # vidéo sur laquelle tester
video_output = "output_video.mp4"   # vidéo résultat
epochs = 50                         # nombre d'époques pour l'entraînement

# ================================
# 2️⃣ Créer train/valid/test
# ================================
for d in ["train", "valid", "test"]:
    os.makedirs(os.path.join(dataset_dir, d, "images"), exist_ok=True)
    os.makedirs(os.path.join(dataset_dir, d, "labels"), exist_ok=True)

# Lister toutes les images
images = [f for f in os.listdir(dataset_folder) if f.endswith(".jpg")]
random.shuffle(images)

train_split = int(0.7 * len(images))
valid_split = int(0.9 * len(images))

for i, img in enumerate(images):
    name = os.path.splitext(img)[0]
    label = name + ".txt"

    if i < train_split:
        folder = "train"
    elif i < valid_split:
        folder = "valid"
    else:
        folder = "test"

    shutil.copy(os.path.join(dataset_folder, img), os.path.join(dataset_dir, folder, "images", img))
    shutil.copy(os.path.join(dataset_folder, label), os.path.join(dataset_dir, folder, "labels", label))

print("[+] Dataset organisé en train/valid/test")

# ================================
# 3️⃣ Créer data.yaml
# ================================
# ================================
# 3️⃣ Créer data.yaml corrigé
# ================================
yaml_path = os.path.join(dataset_dir, "data.yaml")
with open(yaml_path, "w") as f:
    f.write(f"train: train/images\n")
    f.write(f"val: valid/images\n")
    f.write(f"test: test/images\n")
    f.write("nc: 1\n")
    f.write("names: ['basket_hoop']\n")

print(f"[+] data.yaml créé : {yaml_path}")

# ================================
# 4️⃣ Entraîner YOLOv8
# ================================
model = YOLO("yolov8n.pt")  # modèle léger de base

print("[*] Début de l'entraînement...")
model.train(
    data=yaml_path,
    epochs=epochs,
    imgsz=640,
    batch=16
)
print("[+] Entraînement terminé. Le modèle se trouve dans runs/train/weights/best.pt")

# ================================
# 5️⃣ Détecter sur une vidéo et encadrer panier
# ================================
model_path = "runs/train/weights/best.pt"  # chemin vers ton modèle entraîné
model = YOLO(model_path)

cap = cv2.VideoCapture(video_input)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(video_output, fourcc, fps, (width, height))

print("[*] Début de la détection sur vidéo...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(frame)

    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()
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