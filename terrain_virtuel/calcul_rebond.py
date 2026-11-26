"""Algorithme de valeur d'un rebond.

La valeur d'un rebond est un coefficient compris entre 0,7 (rebond facile)
et 1,3 (rebond très disputé). Elle combine :
- la difficulté (adversaires proches, plus grands, meilleurs rebondeurs) ;
- la facilité (personne autour, avantage de taille ou de stats, rebond long,
  supériorité numérique) ;
- le contexte « clutch » (match serré dans la dernière minute).
"""
from .config import VALEUR_REBOND_MAX, VALEUR_REBOND_MIN


def clamp(x, a, b):
    """Force la valeur à rester dans l'intervalle [a, b]."""
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

    return round(clamp(value, VALEUR_REBOND_MIN, VALEUR_REBOND_MAX), 3)


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

    return round(clamp(value, VALEUR_REBOND_MIN, VALEUR_REBOND_MAX), 3)


def valeur_rebond(situation):
    """Calcule la valeur du rebond d'une `SituationRebond` (offensif ou défensif)."""
    calcul = valeur_rebond_offensif if situation.offensif else valeur_rebond_defensif
    return calcul(
        TailleRebondeur=situation.rebondeur.taille,
        Moyenne_Rebond_rebondeur=situation.rebondeur.stat_rebond,
        Taille_adversaires_1m=situation.tailles_adv_1m,
        Taille_adversaires_2m=situation.tailles_adv_2m,
        Moyenne_Reb_adv_1m=situation.rebonds_adv_1m,
        Moyenne_Reb_adv_2m=situation.rebonds_adv_2m,
        DiffScore=situation.diff_score,
        TempsRestant=situation.temps_restant,
        DistBallePanier=situation.distance_panier,
        Ratio=situation.ratio,
    )
