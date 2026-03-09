import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Button , TextBox, CheckButtons
from def_equipe_joueur import Joueur
from def_equipe_joueur import LARGEUR_TERRAIN


def clamp(x, a, b): #Force la valeur du rebond à rester dans l'intervalle
    return max(a, min(b, x))


def valeur_rebond_defensif(
    TailleRebondeur,
    Moyenne_Rebond_rebondeur,
    Taille_adversaires_1m,
    Taille_adversaires_2m,
    Moyenne_Reb_adv_1m,
    Moyenne_Reb_adv_2m,
    DiffScore,
    TempsRestant,
    DistBallePanier,
    Ratio
):

    difficulty = 0
    ease = 0
    clutch = 0

    nb1 = len(Taille_adversaires_1m)
    nb2 = len(Taille_adversaires_2m)

    # -------------------
    # DIFFICULTÉ
    # -------------------

    difficulty += nb1 * 0.12
    difficulty += nb2 * 0.04

    for adv in Taille_adversaires_1m:
        diff = adv - TailleRebondeur
        if diff > 0:
            difficulty += diff * 0.002

    for adv in Moyenne_Reb_adv_1m:
        diff = adv - Moyenne_Rebond_rebondeur
        if diff > 0:
            difficulty += diff * 0.015

    # -------------------
    # FACILITÉ
    # -------------------

    # aucun adversaire proche
    if nb1 == 0 and nb2 == 0:
        ease += 0.20

    # avantage taille
    for adv in Taille_adversaires_1m + Taille_adversaires_2m:
        diff = TailleRebondeur - adv
        if diff > 0:
            ease += diff * 0.0015

    # avantage stats
    for adv in Moyenne_Reb_adv_1m + Moyenne_Reb_adv_2m:
        diff = Moyenne_Rebond_rebondeur - adv
        if diff > 0:
            ease += diff * 0.02

    # rebond long (plus chanceux)
    if DistBallePanier > 4:
        ease += (DistBallePanier - 4) * 0.015

    # ratio favorable (beaucoup de coéquipiers)
    if Ratio < 1:
        ease += (1 - Ratio) * 0.03

    # -------------------
    # CLUTCH
    # -------------------

    clutch_flag = False

    if abs(DiffScore) <= 6 and TempsRestant <= 60:
        clutch_flag = True

        if DiffScore > 0:
            clutch += 0.10
        elif DiffScore < 0 and TempsRestant <= 5:
            clutch += 0.02
        else:
            clutch += 0.05

    # -------------------
    # CALCUL FINAL
    # -------------------

    value = 1 + difficulty + clutch - ease

    if clutch_flag:
        value = max(value, 1.0)

    if nb1 >= 1:
        value = max(value, 1.0)

    return round(clamp(value, 0.7, 1.3), 3)


def valeur_rebond_offensif(
    TailleRebondeur,
    Moyenne_Rebond_rebondeur,
    Taille_adversaires_1m,
    Taille_adversaires_2m,
    Moyenne_Reb_adv_1m,
    Moyenne_Reb_adv_2m,
    DiffScore,
    TempsRestant,
    DistBallePanier,
    Ratio
):

    difficulty = 0
    ease = 0
    clutch = 0

    nb1 = len(Taille_adversaires_1m)
    nb2 = len(Taille_adversaires_2m)

    # -------------------
    # DIFFICULTÉ
    # -------------------

    difficulty += nb1 * 0.12
    difficulty += nb2 * 0.04

    for adv in Taille_adversaires_1m:
        diff = adv - TailleRebondeur
        if diff > 0:
            difficulty += diff * 0.002

    for adv in Taille_adversaires_2m:
        diff = adv - TailleRebondeur
        if diff > 0:
            difficulty += diff * 0.001

    for adv in Moyenne_Reb_adv_1m:
        diff = adv - Moyenne_Rebond_rebondeur
        if diff > 0:
            difficulty += diff * 0.015

    for adv in Moyenne_Reb_adv_2m:
        diff = adv - Moyenne_Rebond_rebondeur
        if diff > 0:
            difficulty += diff * 0.008

    # -------------------
    # FACILITÉ
    # -------------------

    if nb1 == 0 and nb2 == 0:
        ease += 0.20

    for adv in Taille_adversaires_1m + Taille_adversaires_2m:
        diff = TailleRebondeur - adv
        if diff > 0:
            ease += diff * 0.0015

    for adv in Moyenne_Reb_adv_1m + Moyenne_Reb_adv_2m:
        diff = Moyenne_Rebond_rebondeur - adv
        if diff > 0:
            ease += diff * 0.02

    if DistBallePanier > 4:
        ease += (DistBallePanier - 4) * 0.015

    if Ratio < 1:
        ease += (1 - Ratio) * 0.03

    # -------------------
    # BONUS OFFENSIF STRUCTUREL
    # -------------------

    difficulty += 0.07

    # -------------------
    # CLUTCH
    # -------------------

    clutch_flag = False

    if abs(DiffScore) <= 6 and TempsRestant <= 60:
        clutch_flag = True

        if DiffScore < 0 and TempsRestant <= 5:
            clutch += 0.18
        elif DiffScore < 0:
            clutch += 0.12
        else:
            clutch += 0.08

    # -------------------
    # CALCUL FINAL
    # -------------------

    value = 1 + difficulty + clutch - ease

    if clutch_flag:
        value = max(value, 1.0)

    if nb1 >= 1:
        value = max(value, 1.0)

    return round(clamp(value, 0.7, 1.3), 3)


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
    RAYON_ADVERSAIRES_2M = 2.0  # Rayon en mètres autour du rebondeur pour détecter les adversaires proches
    RAYON_ADVERSAIRES_1M=1.0 # Rayon en mètres autour du rebondeur pour détecter les adversaires très proches
    RAYON_RATIO = 3.0 # Rayon pour calculer le ratio adversaires/coequipiers

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
                coequipiers = gestionnaire.joueurs_equipe1  # Coéquipiers = équipe 1
            else:
                adversaires = gestionnaire.joueurs_equipe1  # Sinon, adversaires = équipe 1
                coequipiers = gestionnaire.joueurs_equipe2  # Coéquipiers = équipe 2

            # ÉTAPE 2 : Trouver les adversaires proches du rebondeur
            # On cherche tous les adversaires situés dans un rayon de 1m et 2 mètres autour du rebondeur
            adversaires_proches_1m = []  # Liste vide pour stocker les adversaires dans le rayon de 1 mètre
            adversaires_proches_2m = []  # Liste vide pour stocker les adversaires dans le rayon de 2 mètres
            adversaires_ratio = [] # Liste pour stocker les adversaires dans le rayon de 3 mètres (pour calcul du ratio)
            coequipiers_ratio = [] # Liste pour stocker les coéquipiers dans le rayon de 3 mètres (pour calcul du ratio)
            x_reb, y_reb = rebondeur.position  # Récupérer les coordonnées (x, y) du rebondeur sur le terrain

            # Parcourir chaque adversaire pour calculer sa distance par rapport au rebondeur
            for adv in adversaires:
                x_adv, y_adv = adv.position  # Récupérer les coordonnées (x, y) de l'adversaire
                # Calculer la distance euclidienne entre le rebondeur et l'adversaire
                distance = np.hypot(x_reb - x_adv, y_reb - y_adv)

                # Ajouter à la liste 1m si distance <= 1m
                if distance <= RAYON_ADVERSAIRES_1M:
                    adversaires_proches_1m.append(adv)

                # Ajouter à la liste 2m si 1m <=distance <= 2m
                if RAYON_ADVERSAIRES_1M <= distance <= RAYON_ADVERSAIRES_2M:
                    adversaires_proches_2m.append(adv)

                
            for adv in adversaires:
                x_adv, y_adv = adv.position  # Récupérer les coordonnées (x, y) de l'adversaire
                distance = np.hypot(x_reb - x_adv, y_reb - y_adv)  # Calculer la distance euclidienne

                if distance <= RAYON_RATIO:
                    adversaires_ratio.append(adv)

            for coeq in coequipiers:
                x_coeq, y_coeq = coeq.position  # Récupérer les coordonnées (x, y) du coéquipier
                distance = np.hypot(x_reb - x_coeq, y_reb - y_coeq)  # Calculer la distance euclidienne

                if distance <= RAYON_RATIO:
                    coequipiers_ratio.append(coeq)

            # Calcul ratio :
            ratio = len(adversaires_ratio) / max(len(coequipiers_ratio), 1)  # Éviter division par zéro

            # ÉTAPE 3 : Extraire les statistiques du rebondeur
            nb_adversaires_1m = len(adversaires_proches_1m)  # Compter combien d'adversaires sont dans le rayon de 1m
            nb_adversaires_2m = len(adversaires_proches_2m)  # Compter combien d'adversaires sont dans le rayon de 2m
            nom_rebondeur = f"{rebondeur.prenom} {rebondeur.nom}"  # Créer le nom complet
            taille_rebondeur = rebondeur.taille  # Taille du rebondeur en cm (provient du fichier InfosJoueurs)
            stat_rebond_rebondeur = rebondeur.stat_rebond  # Moyenne de rebonds du joueur (AverageRebond)

            #position du panier
            x_panier=1.6
            y_panier=LARGEUR_TERRAIN/2
            # calcul de la distance du rebondeur au panier
            distance_panier_rebondeur = np.hypot(x_panier - x_reb, y_panier - y_reb)

            # ÉTAPE 4 : Extraire toutes les tailles et stats de rebond des adversaires proches
            # Chaque adversaire aura sa propre colonne (max 5 adversaires par rayon)
            MAX_ADVERSAIRES = 5

            # Extraire les tailles et rebonds pour le rayon 1m
            tailles_adv_1m = [adv.taille for adv in adversaires_proches_1m]
            rebonds_adv_1m = [adv.stat_rebond for adv in adversaires_proches_1m]

            # Extraire les tailles et rebonds pour le rayon 2m (entre 1m et 2m)
            tailles_adv_2m = [adv.taille for adv in adversaires_proches_2m]
            rebonds_adv_2m = [adv.stat_rebond for adv in adversaires_proches_2m]

            # Compléter avec des valeurs vides si moins de MAX_ADVERSAIRES
            while len(tailles_adv_1m) < MAX_ADVERSAIRES:
                tailles_adv_1m.append("")
                rebonds_adv_1m.append("")

            while len(tailles_adv_2m) < MAX_ADVERSAIRES:
                tailles_adv_2m.append("")
                rebonds_adv_2m.append("")

            # ÉTAPE 5 : Calculer la différence de score 
            # DiffScore signé : positif si l'équipe du rebondeur mène, négatif si elle est menée
            if rebondeur in gestionnaire.joueurs_equipe1:
                DiffScore = score_equipe1 - score_equipe2
            else:
                DiffScore = score_equipe2 - score_equipe1

            # Récupérer l'état de la checkbox "Rebond Offensif"
            checkbox_status = checkbox.get_status()  # Retourne [True] ou [False]
            rebond_offensif = 1 if checkbox_status[0] else 0  # Convertit le statut de la checkbox en 1 (si coché) ou 0 (si non coché)

            # Filtrer les listes pour enlever les valeurs vides
            Taille_adversaires_1m = [t for t in tailles_adv_1m if t != ""]
            Taille_adversaires_2m = [t for t in tailles_adv_2m if t != ""]
            Moyenne_Reb_adv_1m = [r for r in rebonds_adv_1m if r != ""]
            Moyenne_Reb_adv_2m = [r for r in rebonds_adv_2m if r != ""]

            # Calculer la valeur du rebond
            if rebond_offensif:
                valeur_rebond = valeur_rebond_offensif(
                    TailleRebondeur=taille_rebondeur,
                    Moyenne_Rebond_rebondeur=stat_rebond_rebondeur,
                    Taille_adversaires_1m=Taille_adversaires_1m,
                    Taille_adversaires_2m=Taille_adversaires_2m,
                    Moyenne_Reb_adv_1m=Moyenne_Reb_adv_1m,
                    Moyenne_Reb_adv_2m=Moyenne_Reb_adv_2m,
                    DiffScore=DiffScore,
                    TempsRestant=temps_restant,
                    DistBallePanier=distance_panier_rebondeur,
                    Ratio=ratio
                )
            else:
                valeur_rebond = valeur_rebond_defensif(
                    TailleRebondeur=taille_rebondeur,
                    Moyenne_Rebond_rebondeur=stat_rebond_rebondeur,
                    Taille_adversaires_1m=Taille_adversaires_1m,
                    Taille_adversaires_2m=Taille_adversaires_2m,
                    Moyenne_Reb_adv_1m=Moyenne_Reb_adv_1m,
                    Moyenne_Reb_adv_2m=Moyenne_Reb_adv_2m,
                    DiffScore=DiffScore,
                    TempsRestant=temps_restant,
                    DistBallePanier=distance_panier_rebondeur,
                    Ratio=ratio
                )

            # ÉTAPE 6 : Créer un dictionnaire avec toutes les données à exporter
            # Chaque adversaire aura sa propre colonne séparée
            donnees = {
                'Nom_Rebondeur': [nom_rebondeur],
                'Taille_Rebondeur': [taille_rebondeur],
                'Nb_Adversaires_1M': [nb_adversaires_1m],
                'Nb_Adversaires_2M': [nb_adversaires_2m],
                'Stat_Rebond_Rebondeur': [stat_rebond_rebondeur],
                'Distance_Panier_Rebondeur': [distance_panier_rebondeur],
                'Ratio_Adversaires_Coequipiers': [ratio],
                'Diff_Score': [DiffScore],
                'Temps_Restant': [temps_restant],
                'Rebond_Offensif': [rebond_offensif],
                'Valeur_Rebond': [valeur_rebond]
            }

            # Ajouter les colonnes pour chaque adversaire dans le rayon 1m
            for i in range(MAX_ADVERSAIRES):
                donnees[f'Adv_{i+1}_Taille_1M'] = [tailles_adv_1m[i]]
                donnees[f'Adv_{i+1}_Rebond_1M'] = [rebonds_adv_1m[i]]

            # Ajouter les colonnes pour chaque adversaire dans le rayon 2m
            for i in range(MAX_ADVERSAIRES):
                donnees[f'Adv_{i+1}_Taille_2M'] = [tailles_adv_2m[i]]
                donnees[f'Adv_{i+1}_Rebond_2M'] = [rebonds_adv_2m[i]]

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
