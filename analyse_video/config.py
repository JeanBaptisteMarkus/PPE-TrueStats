"""Chemins et paramètres du pipeline d'analyse vidéo."""
from pathlib import Path

DOSSIER_ANALYSE = Path(__file__).resolve().parent
RACINE_PROJET = DOSSIER_ANALYSE.parent

# --- Entrées / sorties (non versionnées, voir .gitignore) -------------------
DOSSIER_VIDEOS = DOSSIER_ANALYSE / "input_videos"
VIDEO_PAR_DEFAUT = DOSSIER_VIDEOS / "video9.mp4"
DOSSIER_SORTIE = DOSSIER_ANALYSE / "output_videos"  # un sous-dossier par vidéo analysée
DOSSIER_STUBS = DOSSIER_ANALYSE / "stubs"  # cache pickle des détections, un sous-dossier par vidéo

# --- Modèles YOLO (voir models/README.md) -----------------------------------
DOSSIER_MODELES = DOSSIER_ANALYSE / "models"
MODELE_JOUEURS = DOSSIER_MODELES / "player_detector.pt"
MODELE_BALLON = DOSSIER_MODELES / "ball_detector.pt"
MODELE_TERRAIN = DOSSIER_MODELES / "court_keypoint.pt"
MODELE_PANIER = DOSSIER_MODELES / "panier.pt"
MODELE_EQUIPES = DOSSIER_MODELES / "team.pt"
MODELE_IDENTITE_JOUEURS = DOSSIER_MODELES / "JoueurEquipe.pt"

# --- Données ---------------------------------------------------------------
FICHIER_JOUEURS = RACINE_PROJET / "data" / "joueurs_celtics_bucks.csv"

# --- Paramètres de détection ------------------------------------------------
SEUIL_CONFIANCE_TERRAIN = 0.2
# Les seuils des tirs et rebonds (durées, marges) sont dans evenements/tirs.py
