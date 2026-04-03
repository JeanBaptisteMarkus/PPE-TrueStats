import torch
from ultralytics import YOLO  # Nécessaire pour YOLOv8

model_path = "basketball_analysis/models/player_detector.pt"

# Charger le modèle YOLO
model = YOLO(model_path)

# Afficher les classes
print("Classes du modèle :")
print(model.names)