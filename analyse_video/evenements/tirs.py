"""Détection des tirs (réussis ou ratés) et des rebonds.

Règle, frame par frame (coordonnées image, y vers le bas) :

1. départ : le ballon quitte un joueur (possession -> personne), ou il est déjà
   en l'air au début de la vidéo (tireur inconnu) ;
2. tir : sans que personne ne le récupère, le ballon monte au-dessus du centre
   de la zone du panier, puis entre dans cette zone en moins de DUREE_VOL_MAX.
   Une passe est attrapée avant, ou ne monte pas assez ;
3. issue : le tir est réussi si le ballon ressort de la zone par le bas, dans sa
   partie centrale (il passe dans le cercle). Il est raté s'il en ressort par un
   autre côté, ou si un joueur le récupère dans la zone ;
4. rebond : première récupération du ballon après un tir raté, dans les
   DUREE_REBOND_MAX secondes. Offensif si le rebondeur est de l'équipe du tireur.

La zone du panier est le cadre détecté par le modèle (panneau + cercle pour
panier.pt), élargi d'une marge proportionnelle à sa largeur plus un diamètre de
ballon : la règle ne dépend ni de la résolution ni du zoom. Les durées sont en
secondes et converties avec les images/s de la vidéo.

Limites : vue 2D (un ballon qui passe devant ou derrière le cercle peut être
mal jugé) ; un « air ball » qui n'approche pas du panier n'est pas compté comme
un tir.
"""
from dataclasses import dataclass
from typing import Optional

DUREE_VOL_MAX = 3.0      # s entre le départ du ballon et son arrivée au panier
DUREE_ISSUE_MAX = 1.5    # s pour que le ballon ressorte de la zone du panier
DUREE_REBOND_MAX = 5.0   # s entre la sortie du ballon et la récupération
MARGE_ZONE = 0.25        # marge autour du cadre du panier, en largeurs de cadre
BANDE_CENTRALE = 0.30    # demi-largeur (en largeurs de cadre) de la sortie « dans le cercle »


@dataclass
class Tir:
    depart: int                 # frame où le ballon quitte le tireur
    tireur: Optional[int]       # id du suivi du tireur (None : tir commencé avant la vidéo)
    equipe: Optional[int]       # équipe du tireur (1, 2 ou None)
    arrivee: int                # première frame du ballon dans la zone du panier
    fin: int                    # frame où le ballon quitte la zone (ou est récupéré)
    reussi: bool


@dataclass
class Rebond:
    frame: int                  # frame où la possession est confirmée
    joueur: int                 # id du suivi du rebondeur
    equipe: Optional[int]
    offensif: Optional[bool]    # None si l'équipe du tireur ou du rebondeur est inconnue
    tir: Tir


def zone_panier(cadre, diametre_ballon=0.0, marge=MARGE_ZONE):
    """Cadre du panier élargi : (x1, y1, x2, y2)."""
    x1, y1, x2, y2 = cadre
    m = marge * (x2 - x1) + diametre_ballon
    return x1 - m, y1 - m, x2 + m, y2 + m


def _dans(point, zone):
    x, y = point
    return zone[0] <= x <= zone[2] and zone[1] <= y <= zone[3]


class DetecteurTirs:
    def __init__(self, fps, diametre_ballon=0.0, duree_vol_max=DUREE_VOL_MAX,
                 duree_issue_max=DUREE_ISSUE_MAX, duree_rebond_max=DUREE_REBOND_MAX):
        self.diametre_ballon = diametre_ballon
        self.frames_vol = max(1, round(duree_vol_max * fps))
        self.frames_issue = max(1, round(duree_issue_max * fps))
        self.frames_rebond = max(1, round(duree_rebond_max * fps))

    def detecter(self, ball_positions, possession, paniers, equipes=None):
        """Retourne (tirs, rebonds).

        ball_positions[t] : centre (x, y) du ballon ou (None, None)
        possession[t]     : id du porteur ou -1
        paniers[t]        : cadre (x1, y1, x2, y2) du panier ou None
        equipes[t]        : {id de suivi: équipe} (facultatif)
        """
        n = len(ball_positions)
        equipes = equipes or [{}] * n
        tirs, rebonds = [], []
        t = 0
        while t < n:
            depart = self._prochain_depart(possession, t)
            if depart is None:
                break
            tir = self._suivre_tir(ball_positions, possession, paniers, equipes, depart)
            if tir is None:
                t = depart + 1
                continue
            tirs.append(tir)
            if not tir.reussi:
                rebond = self._chercher_rebond(possession, equipes, tir)
                if rebond:
                    rebonds.append(rebond)
            t = tir.fin + 1
        return tirs, rebonds

    @staticmethod
    def _prochain_depart(possession, debut):
        for t in range(debut, len(possession)):
            if possession[t] == -1 and (t == 0 or possession[t - 1] != -1):
                return t
        return None

    def _suivre_tir(self, ball_positions, possession, paniers, equipes, depart):
        n = len(ball_positions)
        tireur = possession[depart - 1] if depart > 0 else None
        equipe = equipes[depart - 1].get(tireur) if tireur is not None else None

        # 1. le ballon monte au-dessus du centre de la zone, puis y entre, sans être récupéré
        monte = False
        arrivee = None
        for t in range(depart, min(n, depart + self.frames_vol + 1)):
            if possession[t] != -1:
                return None  # attrapé avant le panier : passe, pas un tir
            if ball_positions[t][0] is None or paniers[t] is None:
                continue
            zone = zone_panier(paniers[t], self.diametre_ballon)
            if ball_positions[t][1] < (zone[1] + zone[3]) / 2:
                monte = True
            if monte and _dans(ball_positions[t], zone):
                arrivee = t
                break
        if arrivee is None:
            return None

        # 2. issue : sortie de la zone par le bas au centre (réussi), sinon raté
        for t in range(arrivee + 1, min(n, arrivee + self.frames_issue + 1)):
            if possession[t] != -1:
                return Tir(depart, tireur, equipe, arrivee, t, reussi=False)
            if ball_positions[t][0] is None or paniers[t] is None:
                continue
            zone = zone_panier(paniers[t], self.diametre_ballon)
            if _dans(ball_positions[t], zone):
                continue
            x, y = ball_positions[t]
            x1, _, x2, _ = paniers[t]
            centre_x = (x1 + x2) / 2
            reussi = y > zone[3] and abs(x - centre_x) <= BANDE_CENTRALE * (x2 - x1)
            return Tir(depart, tireur, equipe, arrivee, t, reussi=reussi)
        return None  # issue inconnue (ballon perdu de vue) : on ne compte rien

    def _chercher_rebond(self, possession, equipes, tir):
        n = len(possession)
        for t in range(tir.arrivee, min(n, tir.fin + self.frames_rebond + 1)):
            if possession[t] != -1:
                joueur = possession[t]
                equipe = equipes[t].get(joueur)
                offensif = None if equipe is None or tir.equipe is None else equipe == tir.equipe
                return Rebond(t, joueur, equipe, offensif, tir)
        return None
