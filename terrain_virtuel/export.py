"""Export des situations de rebond dans un fichier Excel (une ligne par situation)."""
import os

import pandas as pd

from .config import MAX_ADVERSAIRES


def _completer(valeurs, longueur=MAX_ADVERSAIRES):
    """Complète une liste avec des chaînes vides jusqu'à `longueur` éléments."""
    return list(valeurs) + [""] * (longueur - len(valeurs))


def ligne_export(situation, valeur_rebond):
    """Construit la ligne (dictionnaire colonne -> valeur) d'une situation analysée."""
    rebondeur = situation.rebondeur
    ligne = {
        'Nom_Rebondeur': rebondeur.nom_complet,
        'Taille_Rebondeur': rebondeur.taille,
        'Nb_Adversaires_1M': len(situation.adversaires_1m),
        'Nb_Adversaires_2M': len(situation.adversaires_2m),
        'Stat_Rebond_Rebondeur': rebondeur.stat_rebond,
        'Distance_Panier_Rebondeur': situation.distance_panier,
        'Ratio_Adversaires_Coequipiers': situation.ratio,
        'Diff_Score': situation.diff_score,
        'Temps_Restant': situation.temps_restant,
        'Rebond_Offensif': 1 if situation.offensif else 0,
        'Valeur_Rebond': valeur_rebond,
    }

    # Une colonne par adversaire (taille et moyenne de rebonds), pour chaque rayon
    for rayon, tailles, rebonds in (
        ("1M", situation.tailles_adv_1m, situation.rebonds_adv_1m),
        ("2M", situation.tailles_adv_2m, situation.rebonds_adv_2m),
    ):
        tailles, rebonds = _completer(tailles), _completer(rebonds)
        for i in range(MAX_ADVERSAIRES):
            ligne[f'Adv_{i+1}_Taille_{rayon}'] = tailles[i]
            ligne[f'Adv_{i+1}_Rebond_{rayon}'] = rebonds[i]
    return ligne


def ajouter_ligne_excel(ligne, chemin):
    """Ajoute une ligne à la fin du fichier Excel `chemin` (créé s'il n'existe pas)."""
    df_nouvelle_ligne = pd.DataFrame({cle: [valeur] for cle, valeur in ligne.items()})
    os.makedirs(os.path.dirname(chemin), exist_ok=True)

    if os.path.exists(chemin):
        df_existant = pd.read_excel(chemin)
        df_final = pd.concat([df_existant, df_nouvelle_ligne], ignore_index=True)
        print(f"Nouvelle ligne ajoutée au fichier '{chemin}'")
    else:
        df_final = df_nouvelle_ligne
        print(f"Fichier '{chemin}' créé avec les premières données")

    df_final.to_excel(chemin, index=False)
