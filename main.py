import random
import matplotlib.pyplot as plt
from def_equipe_joueur import equipes_NBA, LONGUEUR_TERRAIN, LARGEUR_TERRAIN
from interface_graphique import choix_contexte_tkinter
from gestion_donnees import charger_joueurs, selectionner_joueurs, extraire_donnee
from gestionnaire import GestionnaireJoueurs
from terrain import dessiner_terrain


def main():
    """Fonction principale du programme"""
    
    # Afficher le menu de choix du contexte du match
    equipe1, equipe2, score_equipe1, score_equipe2, temps_restant = choix_contexte_tkinter()

    # Charger les joueurs depuis le fichier
    joueurs = charger_joueurs('InfosJoueurs')

    # Sélectionner 5 joueurs de chaque équipe
    joueurs_equipe1 = selectionner_joueurs(joueurs, equipe1, 5)
    joueurs_equipe2 = selectionner_joueurs(joueurs, equipe2, 5)

    # Récupérer les joueurs restants (non placés)
    tous_joueurs_equipe1 = [j for j in joueurs if j.equipe == equipe1]
    tous_joueurs_equipe2 = [j for j in joueurs if j.equipe == equipe2]
    joueurs_restants1 = [j for j in tous_joueurs_equipe1 if j not in joueurs_equipe1]
    joueurs_restants2 = [j for j in tous_joueurs_equipe2 if j not in joueurs_equipe2]

    # Placer les joueurs sur le terrain avec positions aléatoires
    for joueur in joueurs_equipe1:
        joueur.position = [random.uniform(0.5, LONGUEUR_TERRAIN / 2), random.uniform(0.5, LARGEUR_TERRAIN - 0.5)]
    for joueur in joueurs_equipe2:
        joueur.position = [random.uniform(LONGUEUR_TERRAIN / 2, LONGUEUR_TERRAIN - 0.5), random.uniform(0.5, LARGEUR_TERRAIN - 0.5)]

    # Créer la figure avec le terrain et le panneau de remplacements
    fig = plt.figure(figsize=(16, 6))
    fig.suptitle(f"{equipe1}:{score_equipe1}  —  {equipe2}:{score_equipe2}     temps restant : {temps_restant}", fontsize=16)

    ax_terrain = fig.add_subplot(1, 2, 1)
    ax_remplacements = fig.add_subplot(1, 2, 2)

    # Créer le gestionnaire de joueurs
    gestionnaire = GestionnaireJoueurs(fig, ax_terrain, ax_remplacements, joueurs_equipe1, joueurs_equipe2, joueurs_restants1, joueurs_restants2)

    # Dessiner les joueurs
    gestionnaire.draw_players()
    gestionnaire.draw_remplacement_panel()

    # Connecter les événements de souris
    fig.canvas.mpl_connect('button_press_event', gestionnaire.on_click)
    fig.canvas.mpl_connect('motion_notify_event', gestionnaire.on_drag)
    fig.canvas.mpl_connect('button_release_event', gestionnaire.on_release)
    fig.canvas.mpl_connect('pick_event', gestionnaire.on_pick_remplacant)

    # Appeler la fonction pour extraire les données
    rebondeur = extraire_donnee(gestionnaire, fig, score_equipe1, score_equipe2, temps_restant)


if __name__ == "__main__":
    main()
