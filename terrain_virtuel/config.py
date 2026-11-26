"""Constantes du terrain virtuel : dimensions, rayons d'analyse et chemins de fichiers."""
from pathlib import Path

# --- Chemins ---------------------------------------------------------------
RACINE_PROJET = Path(__file__).resolve().parent.parent
FICHIER_JOUEURS = RACINE_PROJET / "data" / "joueurs_nba.csv"
DOSSIER_SORTIE = RACINE_PROJET / "output"
FICHIER_EXPORT = DOSSIER_SORTIE / "donnees_rebonds.xlsx"

# --- Demi-terrain NBA (en mètres) -------------------------------------------
LONGUEUR_TERRAIN = 14.325
LARGEUR_TERRAIN = 15.24

# Centre du panier (à 1,6 m de la ligne de fond, au milieu de la largeur)
POSITION_PANIER = (1.6, LARGEUR_TERRAIN / 2)

# --- Analyse d'une situation de rebond ------------------------------------
RAYON_ADVERSAIRES_1M = 1.0  # adversaires « au contact »
RAYON_ADVERSAIRES_2M = 2.0  # adversaires proches (couronne 1 m – 2 m)
RAYON_RATIO = 3.0           # rayon pour le ratio adversaires / coéquipiers
MAX_ADVERSAIRES = 5         # nombre de colonnes d'adversaires dans l'export

# Bornes de la valeur d'un rebond
VALEUR_REBOND_MIN = 0.7
VALEUR_REBOND_MAX = 1.3

# --- Interface ---------------------------------------------------------------
RAYON_SELECTION_JOUEUR = 0.7  # distance max (m) entre le clic et un joueur
