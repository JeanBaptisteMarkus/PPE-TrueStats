"""Affiche les classes d'un modèle YOLO.

Lancement : python entrainement/afficher_classes_modele.py [chemin/vers/modele.pt]
(par défaut : analyse_video/models/player_detector.pt)
"""
import sys
from pathlib import Path

from ultralytics import YOLO  # Nécessaire pour YOLOv8

MODELES = Path(__file__).resolve().parent.parent / "analyse_video" / "models"
model_path = sys.argv[1] if len(sys.argv) > 1 else str(MODELES / "player_detector.pt")

# Charger le modèle YOLO
model = YOLO(model_path)

# Afficher les classes
print("Classes du modèle :")
print(model.names)
