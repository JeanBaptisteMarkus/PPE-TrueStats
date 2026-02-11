import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons
from def_equipe_joueur import Joueur, LARGEUR_TERRAIN


def charger_joueurs(nom_fichier):
    # Charger les joueurs depuis un fichier CSV et créer des objets Joueur
    df = pd.read_csv(nom_fichier)
    joueurs = [Joueur(row['ID'], row['Nom'], row['Prenom'], row['Taille'], row['AverageRebond'], row['Equipe'])
               for _, row in df.iterrows()]
    return joueurs


def selectionner_joueurs(joueurs, equipe, nombre=5):
    # Sélectionner un nombre donné de joueurs aléatoires d'une équipe
    import random
    joueurs_equipe = [j for j in joueurs if j.equipe == equipe]
    return random.sample(joueurs_equipe, min(nombre, len(joueurs_equipe)))


def extraire_donnee(gestionnaire, fig, score_equipe1, score_equipe2, temps_restant):
    rebondeur = None
    RAYON_ADVERSAIRES_1M = 1.0
    RAYON_ADVERSAIRES_2M = 2.0

    def valider_rebondeur(event):
        nonlocal rebondeur
        if gestionnaire.joueur_selectionne is None:
            print("Aucun joueur sélectionné.")
            return

        rebondeur = gestionnaire.joueur_selectionne

        # Identifier les adversaires de l'équipe opposée
        adversaires = gestionnaire.joueurs_equipe2 if rebondeur in gestionnaire.joueurs_equipe1 else gestionnaire.joueurs_equipe1

        # Calculer la distance entre le joueur et les adversaires
        x_reb, y_reb = rebondeur.position
        adversaires_proches_1m, adversaires_proches_2m = [], []
        for adv in adversaires:
            x_adv, y_adv = adv.position
            distance = np.hypot(x_reb - x_adv, y_reb - y_adv)
            if distance <= RAYON_ADVERSAIRES_1M:
                adversaires_proches_1m.append(adv)
            elif distance <= RAYON_ADVERSAIRES_2M:
                adversaires_proches_2m.append(adv)

        # Statistiques du rebondeur
        nom_rebondeur = f"{rebondeur.prenom} {rebondeur.nom}"
        taille_rebondeur = rebondeur.taille
        stat_rebond_rebondeur = rebondeur.stat_rebond
        x_panier, y_panier = 1.6, LARGEUR_TERRAIN / 2
        distance_panier_rebondeur = np.hypot(x_panier - x_reb, y_panier - y_reb)

        # Différence de score entre les équipes
        diff_score = abs(score_equipe1 - score_equipe2)

        # Récupérer l'état de la checkbox "Rebond Offensif"
        rebond_offensif = 1 if checkbox.get_status()[0] else 0

        # Créer un dictionnaire avec les données du rebondeur
        donnees = {
            'Nom_Rebondeur': [nom_rebondeur],
            'Taille_Rebondeur': [taille_rebondeur],
            'Stat_Rebond_Rebondeur': [stat_rebond_rebondeur],
            'Distance_Panier_Rebondeur': [distance_panier_rebondeur],
            'Diff_Score': [diff_score],
            'Temps_Restant': [temps_restant],
            'Rebond_Offensif': [rebond_offensif],
        }

        # Fonction pour ajouter les adversaires pour un rayon donné
        def ajouter_adversaires(adversaires_liste, rayon_m):
            for i, adv in enumerate(adversaires_liste, start=1):
                donnees[f'rayon_{int(rayon_m)}M_adv{i}_taille'] = [adv.taille]
                donnees[f'rayon_{int(rayon_m)}M_adv{i}_reb_avg'] = [adv.stat_rebond]

        # Ajouter les adversaires proches
        ajouter_adversaires(adversaires_proches_1m, RAYON_ADVERSAIRES_1M)
        ajouter_adversaires(adversaires_proches_2m, RAYON_ADVERSAIRES_2M)

        df_nouvelle_ligne = pd.DataFrame(donnees)

        # Exporter ou ajouter au fichier Excel
        fichier_excel = 'donnees_rebonds.xlsx'
        if os.path.exists(fichier_excel):
            df_existant = pd.read_excel(fichier_excel)
            df_final = pd.concat([df_existant, df_nouvelle_ligne], ignore_index=True)
            print(f"Nouvelle ligne ajoutée au fichier '{fichier_excel}'")
        else:
            df_final = df_nouvelle_ligne
            print(f"Fichier '{fichier_excel}' créé avec les premières données")

        df_final.to_excel(fichier_excel, index=False)
        plt.close(fig)

    # Bouton "Valider" et checkbox "Rebond Offensif"
    ax_bouton = plt.axes([0.4, 0.02, 0.2, 0.05])
    bouton = Button(ax_bouton, 'Valider')
    bouton.on_clicked(valider_rebondeur)

    ax_checkbox = plt.axes([0.35, 0.08, 0.3, 0.04])
    checkbox = CheckButtons(ax_checkbox, ['Rebond Offensif'], [False])

    plt.show()
    return rebondeur
