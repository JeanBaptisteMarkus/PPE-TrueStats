"""Joueurs et équipes NBA : modèle de données et chargement depuis le CSV."""
import random

import pandas as pd

# Dictionnaire des équipes NBA avec leurs abréviations
EQUIPES_NBA = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
}


class Joueur:
    """Un joueur : identité, taille (cm), moyenne de rebonds et position (m) sur le terrain."""
    def __init__(self, joueur_id, nom, prenom, taille, stat_rebond, equipe):
        self.id = joueur_id
        self.nom = nom
        self.prenom = prenom
        self.taille = float(taille)
        self.stat_rebond = float(stat_rebond)
        self.equipe = equipe
        self.position = [0.0, 0.0]

    @property
    def nom_complet(self):
        """Nom affiché : « Prénom Nom »."""
        return f"{self.prenom} {self.nom}"

    def __repr__(self):
        return f"Joueur({self.id!r}, {self.nom_complet!r})"


def charger_joueurs(nom_fichier):
    """Charge la liste des joueurs depuis le fichier CSV (colonnes ID, Equipe, Nom, Prenom, Taille, AverageRebond)."""
    df = pd.read_csv(nom_fichier)
    joueurs = []
    for _, row in df.iterrows():
        joueur = Joueur(row['ID'], row['Nom'], row['Prenom'], row['Taille'], row['AverageRebond'], row['Equipe'])
        joueurs.append(joueur)
    return joueurs


def selectionner_joueurs(joueurs, equipe, nombre=5):
    """Sélectionne aléatoirement `nombre` joueurs d'une équipe."""
    joueurs_equipe = [j for j in joueurs if j.equipe == equipe]
    return random.sample(joueurs_equipe, min(nombre, len(joueurs_equipe)))
