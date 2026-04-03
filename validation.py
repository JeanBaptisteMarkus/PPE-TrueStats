# test_model.py
from ultralytics import YOLO

# Charger le modèle
model = YOLO("runs/detect/runs/train/celtics_vs_milwaukee/weights/best.pt")

# Tester sur une vidéo et sauvegarder avec un nom personnalisé
results = model("video7.mp4", save=True, project="output", name="resultat")

print("✅ Vidéo sauvegardée dans output/resultat/")