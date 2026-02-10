import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Button , TextBox, CheckButtons
from def_equipe_joueur import Joueur
from def_equipe_joueur import LARGEUR_TERRAIN


def charger_joueurs(nom_fichier):
    """Fonction pour charger les joueurs depuis un fichier CSV"""
    df = pd.read_csv(nom_fichier)
    joueurs = []
    for index, row in df.iterrows():
        joueur = Joueur(row['ID'], row['Nom'], row['Prenom'], row['Taille'], row['AverageRebond'], row['Equipe'])
        joueurs.append(joueur)
    return joueurs


def selectionner_joueurs(joueurs, equipe, nombre=5):
    """Fonction pour sélectionner 5 joueurs aléatoires d'une équipe"""
    import random
    joueurs_equipe = [j for j in joueurs if j.equipe == equipe]
    return random.sample(joueurs_equipe, min(nombre, len(joueurs_equipe)))


# Fonction pour extraire les données de la situations et du rebondeur et les exporter dans un fichier Excel
def extraire_donnee(gestionnaire, fig, score_equipe1, score_equipe2, temps_restant):
    """
    Cette fonction permet à l'utilisateur de sélectionner un rebondeur,
    puis d'extraire et d'exporter ses statistiques ainsi que celles de ses adversaires proches
    dans un fichier Excel.

    Paramètres de la fonction:
    - gestionnaire : Instance de la classe GestionnaireJoueurs qui gère les joueurs sur le terrain
    - fig : Figure matplotlib contenant le terrain (nécessaire pour afficher le bouton et fermer la fenêtre)
    - score_equipe1 : Score de l'équipe 1 (utilisé pour calculer la différence de score)
    - score_equipe2 : Score de l'équipe 2 (utilisé pour calculer la différence de score)
    - temps_restant : Temps restant dans le match en secondes

    Retourne:
    - rebondeur : Le joueur sélectionné par l'utilisateur (objet Joueur)
    """

    rebondeur = None  # Variable qui stockera le joueur sélectionné (initialement vide)
    RAYON_ADVERSAIRES = 2.0  # Rayon en mètres autour du rebondeur pour détecter les adversaires proches


    def valider_rebondeur(event):
        """
        Fonction callback appelée automatiquement lorsque l'utilisateur clique sur le bouton "Valider".
        Elle extrait toutes les données nécessaires et les enregistre dans un fichier Excel.

        Paramètre:
        - event : Événement du clic sur le bouton (fourni automatiquement par matplotlib)
        """
        nonlocal rebondeur  # Permet de modifier la variable rebondeur de la fonction parente

        # Vérifier qu'un joueur a bien été sélectionné sur le terrain
        if gestionnaire.joueur_selectionne is not None:
            rebondeur = gestionnaire.joueur_selectionne  # Récupérer le joueur sélectionné

            # ÉTAPE 1 : Identifier l'équipe adverse 
            # Déterminer si le rebondeur est dans l'équipe 1 ou 2, afin de savoir qui sont ses adversaires
            if rebondeur in gestionnaire.joueurs_equipe1:
                adversaires = gestionnaire.joueurs_equipe2  # Si équipe 1, alors adversaires = équipe 2
            else:
                adversaires = gestionnaire.joueurs_equipe1  # Sinon, adversaires = équipe 1

            # ÉTAPE 2 : Trouver les adversaires proches du rebondeur 
            # On cherche tous les adversaires situés dans un rayon de 2 mètres autour du rebondeur
            adversaires_proches = []  # Liste vide pour stocker les adversaires dans le rayon
            x_reb, y_reb = rebondeur.position  # Récupérer les coordonnées (x, y) du rebondeur sur le terrain

            # Parcourir chaque adversaire pour calculer sa distance par rapport au rebondeur
            for adv in adversaires:
                x_adv, y_adv = adv.position  # Récupérer les coordonnées (x, y) de l'adversaire
                # Calculer la distance euclidienne entre le rebondeur et l'adversaire
                distance = np.hypot(x_reb - x_adv, y_reb - y_adv)

                # Si la distance est inférieure ou égale au rayon, l'adversaire est "proche"
                if distance <= RAYON_ADVERSAIRES:
                    adversaires_proches.append(adv)  # Ajouter cet adversaire à la liste

            # ÉTAPE 3 : Extraire les statistiques du rebondeur
            nb_adversaires = len(adversaires_proches)  # Compter combien d'adversaires sont dans le rayon
            nom_rebondeur = f"{rebondeur.prenom} {rebondeur.nom}"  # Créer le nom complet
            taille_rebondeur = rebondeur.taille  # Taille du rebondeur en cm (provient du fichier InfosJoueurs)
            stat_rebond_rebondeur = rebondeur.stat_rebond  # Moyenne de rebonds du joueur (AverageRebond)

            #position du panier
            x_panier=1.6
            y_panier=LARGEUR_TERRAIN/2
            # calcul de la distance du rebondeur au panier
            distance_panier_rebondeur = np.hypot(x_panier - x_reb, y_panier - y_reb)

            # ÉTAPE 4 : Calculer les moyennes des adversaires proches 
            if nb_adversaires > 0:
                # S'il y a au moins un adversaire proche, calculer les moyennes de leurs statistiques
                # np.mean() calcule la moyenne arithmétique d'une liste de nombres
                moyenne_taille_adv = np.mean([adv.taille for adv in adversaires_proches])
                moyenne_rebond_adv = np.mean([adv.stat_rebond for adv in adversaires_proches])
            else:
                # S'il n'y a aucun adversaire proche, on met les moyennes à 0
                moyenne_taille_adv = 0
                moyenne_rebond_adv = 0

            # ÉTAPE 5 : Calculer la différence de score 
            # abs() retourne la valeur absolue (toujours positive) de la différence entre les deux scores
            diff_score = abs(score_equipe1 - score_equipe2)

            # Récupérer l'état de la checkbox "Rebond Offensif"
            checkbox_status = checkbox.get_status()  # Retourne [True] ou [False]
            rebond_offensif = 1 if checkbox_status[0] else 0  # Convertit le statut de la checkbox en 1 (si coché) ou 0 (si non coché)

            # ÉTAPE 6 : Créer un dictionnaire avec toutes les données à exporter 
            # Chaque clé sera le nom de la colonne dans Excel, chaque valeur est une liste (pour pandas)
            donnees = {
                'Nom_Rebondeur': [nom_rebondeur],  # Nom complet du joueur
                'Taille_Rebondeur': [taille_rebondeur],  # Taille en cm
                'Nb_Adversaires_Rayon': [nb_adversaires],  # Nombre d'adversaires dans 2m
                'Moyenne_Taille_Adversaires': [moyenne_taille_adv],  # Moyenne des tailles des adversaires proches
                'Stat_Rebond_Rebondeur': [stat_rebond_rebondeur],  # Moyenne rebonds du rebondeur
                'Moyenne_Rebond_Adversaires': [moyenne_rebond_adv],  # Moyenne rebonds des adversaires proches
                'Distance_Panier_Rebondeur': [distance_panier_rebondeur],  # Distance du rebondeur au panier
                'Diff_Score': [diff_score],  # Différence absolue de score entre les équipes
                'Temps_Restant': [temps_restant], # Temps restant dans le match en secondes
                'Rebond_Offensif': [rebond_offensif] # Indique si le rebond est offensif (1) ou défensif (0)
                
            }

            # ÉTAPE 7 : Créer un DataFrame pandas avec la nouvelle ligne de données
            # pd.DataFrame() transforme le dictionnaire en tableau structuré (comme une table Excel)
            df_nouvelle_ligne = pd.DataFrame(donnees)

            # ÉTAPE 8 : Enregistrer dans un fichier Excel (ajouter à la suite si le fichier existe déjà)
            # Vérifier si le fichier Excel existe déjà
            if os.path.exists('donnees_rebonds.xlsx'):
                # Si le fichier existe, le charger pour ajouter les nouvelles données à la suite
                df_existant = pd.read_excel('donnees_rebonds.xlsx')  # Lire le fichier Excel existant
                # pd.concat() combine les deux DataFrames (ancien + nouveau) en un seul
                # ignore_index=True réinitialise les numéros de lignes de manière continue
                df_final = pd.concat([df_existant, df_nouvelle_ligne], ignore_index=True)
                print(f"Nouvelle ligne ajoutée au fichier 'donnees_rebonds.xlsx'")
            else:
                # Si le fichier n'existe pas, utiliser directement la nouvelle ligne
                df_final = df_nouvelle_ligne
                print(f"Fichier 'donnees_rebonds.xlsx' créé avec les premières données")

            # to_excel() exporte le DataFrame final dans le fichier .xlsx
            # index=False permet de ne pas ajouter une colonne d'index (numéros de lignes)
            df_final.to_excel('donnees_rebonds.xlsx', index=False)

            # ÉTAPE 9 : Fermer la fenêtre du terrain 
            plt.close(fig)  # Ferme la figure matplotlib (le terrain disparaît)
        else:
            # Si aucun joueur n'a été sélectionné avant de cliquer sur "Valider"
            print("Aucun joueur sélectionné. Veuillez cliquer sur un joueur avant de valider.")


    # CRÉATION DU BOUTON "VALIDER"
    ax_bouton = plt.axes([0.4, 0.02, 0.2, 0.05])

    # Button() crée un bouton matplotlib avec le texte "Valider"
    bouton = Button(ax_bouton, 'Valider')

    # on_clicked() connecte la fonction valider_rebondeur au bouton
    bouton.on_clicked(valider_rebondeur) 

    # CRÉATION DE LA CHECKBOX "Rebond Offensif"
    ax_checkbox = plt.axes([0.35, 0.08, 0.3, 0.04])
    checkbox = CheckButtons(ax_checkbox, ['Rebond Offensif'], [False])

    
    # plt.show() affiche la fenêtre matplotlib avec le terrain et le bouton
    # Cette fonction BLOQUE l'exécution du code jusqu'à ce que la fenêtre soit fermée
    # L'utilisateur peut alors interagir avec le terrain (sélectionner un joueur, cliquer sur "Valider")
    plt.show()

    
    # Une fois que la fenêtre est fermée (après le clic sur "Valider"), on retourne le joueur sélectionné
    return rebondeur
