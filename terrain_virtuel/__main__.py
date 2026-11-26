"""Point d'entrée du terrain virtuel : `python -m terrain_virtuel`."""
import random

import matplotlib.pyplot as plt

from .config import FICHIER_JOUEURS, LARGEUR_TERRAIN, LONGUEUR_TERRAIN
from .interface.contexte import choix_contexte_tkinter
from .interface.gestionnaire import GestionnaireJoueurs
from .interface.validation import extraire_donnee
from .joueurs import charger_joueurs, selectionner_joueurs


def main():
    """Lance le terrain virtuel : choix du contexte, placement des joueurs, validation du rebond."""

    # Choix du contexte du match
    equipe1, equipe2, score_equipe1, score_equipe2, temps_restant = choix_contexte_tkinter()

    # Chargement des joueurs et sélection de 5 joueurs par équipe
    joueurs = charger_joueurs(FICHIER_JOUEURS)
    joueurs_equipe1 = selectionner_joueurs(joueurs, equipe1, 5)
    joueurs_equipe2 = selectionner_joueurs(joueurs, equipe2, 5)

    # Les autres joueurs de chaque équipe sont sur le banc
    joueurs_restants1 = [j for j in joueurs if j.equipe == equipe1 and j not in joueurs_equipe1]
    joueurs_restants2 = [j for j in joueurs if j.equipe == equipe2 and j not in joueurs_equipe2]

    # Positions de départ aléatoires (équipe 1 à gauche, équipe 2 à droite)
    for joueur in joueurs_equipe1:
        joueur.position = [random.uniform(0.5, LONGUEUR_TERRAIN / 2), random.uniform(0.5, LARGEUR_TERRAIN - 0.5)]
    for joueur in joueurs_equipe2:
        joueur.position = [random.uniform(LONGUEUR_TERRAIN / 2, LONGUEUR_TERRAIN - 0.5), random.uniform(0.5, LARGEUR_TERRAIN - 0.5)]

    # Figure : terrain à gauche, panneau des remplaçants à droite
    fig = plt.figure(figsize=(16, 6))
    fig.suptitle(f"{equipe1}:{score_equipe1}  —  {equipe2}:{score_equipe2}     temps restant : {temps_restant}", fontsize=16)
    ax_terrain = fig.add_subplot(1, 2, 1)
    ax_remplacements = fig.add_subplot(1, 2, 2)

    gestionnaire = GestionnaireJoueurs(fig, ax_terrain, ax_remplacements, joueurs_equipe1, joueurs_equipe2,
                                       joueurs_restants1, joueurs_restants2)
    gestionnaire.draw_players()
    gestionnaire.draw_remplacement_panel()

    fig.canvas.mpl_connect('button_press_event', gestionnaire.on_click)
    fig.canvas.mpl_connect('motion_notify_event', gestionnaire.on_drag)
    fig.canvas.mpl_connect('button_release_event', gestionnaire.on_release)
    fig.canvas.mpl_connect('pick_event', gestionnaire.on_pick_remplacant)

    # Attente de la validation du rebondeur, puis export
    return extraire_donnee(gestionnaire, fig, score_equipe1, score_equipe2, temps_restant)


if __name__ == "__main__":
    main()
