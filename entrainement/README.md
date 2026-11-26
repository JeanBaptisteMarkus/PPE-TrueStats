# Entraînement des modèles YOLO

Les datasets ne sont pas versionnés sur `main` : ils sont sur la branche `dev_analyse_vidéo`
(`basketball_analysis/Mk_panier`, `frames/`, `dataset/`) ou téléchargés via Roboflow.

| Fichier | Produit | Modèle dans `analyse_video/models/` |
|---|---|---|
| `notebooks/entrainer_joueurs.ipynb` | Détection des joueurs (YOLOv5l6u) | `player_detector.pt` |
| `notebooks/entrainer_ballon.ipynb` | Détection du ballon (YOLOv5l6u) | `ball_detector.pt` |
| `notebooks/entrainer_reperes_terrain.ipynb` | Repères du terrain (YOLOv8x-pose) | `court_keypoint.pt` |
| `entrainer_detection_panier.py` | Détection du panier (YOLOv8n) | `panier.pt` |
| `entrainer_identification_joueurs.py` | Identification des 18 joueurs (YOLOv8n) | `JoueurEquipe.pt` |
| `tester_detection_panier.py` | Applique `panier.pt` sur une vidéo | — |
| `tester_modele_video.py` | Applique un modèle entraîné sur une vidéo | — |
| `afficher_classes_modele.py` | Liste les classes d'un `.pt` | — |

Les notebooks lisent la clé Roboflow dans la variable d'environnement `ROBOFLOW_API_KEY` :

```bash
export ROBOFLOW_API_KEY=...
```

Les scripts lisent et écrivent leurs fichiers (datasets, `runs/`, vidéos) dans le répertoire courant.
