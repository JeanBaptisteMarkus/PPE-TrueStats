"""Analyse géométrique d'une situation de rebond (sans interface graphique).

À partir des positions des joueurs, on calcule les grandeurs utilisées par
l'algorithme de valeur du rebond : adversaires proches, ratio
adversaires/coéquipiers, distance au panier, écart au score.
"""
from dataclasses import dataclass, field

import numpy as np

from .config import (
    POSITION_PANIER,
    RAYON_ADVERSAIRES_1M,
    RAYON_ADVERSAIRES_2M,
    RAYON_RATIO,
)


@dataclass
class SituationRebond:
    """Grandeurs décrivant le rebondeur et son environnement au moment du rebond."""
    rebondeur: object
    adversaires_1m: list = field(default_factory=list)  # adversaires à moins de 1 m
    adversaires_2m: list = field(default_factory=list)  # adversaires entre 1 m et 2 m
    ratio: float = 0.0              # adversaires / coéquipiers dans un rayon de 3 m
    distance_panier: float = 0.0    # distance rebondeur - panier (m)
    diff_score: int = 0             # > 0 si l'équipe du rebondeur mène
    temps_restant: int = 0          # secondes
    offensif: bool = False

    @property
    def tailles_adv_1m(self):
        return [adv.taille for adv in self.adversaires_1m]

    @property
    def tailles_adv_2m(self):
        return [adv.taille for adv in self.adversaires_2m]

    @property
    def rebonds_adv_1m(self):
        return [adv.stat_rebond for adv in self.adversaires_1m]

    @property
    def rebonds_adv_2m(self):
        return [adv.stat_rebond for adv in self.adversaires_2m]


def distance(joueur_a, joueur_b):
    """Distance euclidienne (m) entre deux joueurs."""
    (xa, ya), (xb, yb) = joueur_a.position, joueur_b.position
    return np.hypot(xa - xb, ya - yb)


def analyser_situation(rebondeur, coequipiers, adversaires, score_equipe, score_adverse,
                       temps_restant, offensif):
    """Construit la `SituationRebond` du rebondeur.

    - coequipiers : joueurs de l'équipe du rebondeur sur le terrain (rebondeur inclus)
    - adversaires : joueurs de l'équipe adverse sur le terrain
    """
    adversaires_1m = []
    adversaires_2m = []
    for adv in adversaires:
        d = distance(rebondeur, adv)
        if d <= RAYON_ADVERSAIRES_1M:
            adversaires_1m.append(adv)
        if RAYON_ADVERSAIRES_1M <= d <= RAYON_ADVERSAIRES_2M:
            adversaires_2m.append(adv)

    # Ratio adversaires / coéquipiers dans un rayon de 3 m
    # (le rebondeur est compté parmi ses coéquipiers car il est à distance 0)
    nb_adv_ratio = sum(1 for adv in adversaires if distance(rebondeur, adv) <= RAYON_RATIO)
    nb_coeq_ratio = sum(1 for coeq in coequipiers if distance(rebondeur, coeq) <= RAYON_RATIO)
    ratio = nb_adv_ratio / max(nb_coeq_ratio, 1)

    x_reb, y_reb = rebondeur.position
    x_panier, y_panier = POSITION_PANIER
    distance_panier = np.hypot(x_panier - x_reb, y_panier - y_reb)

    return SituationRebond(
        rebondeur=rebondeur,
        adversaires_1m=adversaires_1m,
        adversaires_2m=adversaires_2m,
        ratio=ratio,
        distance_panier=distance_panier,
        diff_score=score_equipe - score_adverse,
        temps_restant=temps_restant,
        offensif=bool(offensif),
    )
