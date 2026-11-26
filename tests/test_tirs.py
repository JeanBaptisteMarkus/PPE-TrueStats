"""Détection des tirs et des rebonds sur des trajectoires synthétiques (numpy seulement)."""
import numpy as np
import pytest

from analyse_video.evenements import DetecteurTirs, paniers_par_frame

FPS = 30
PANIER = (580, 100, 640, 160)   # cadre détecté (panneau + cercle), centre x = 610
CERCLE = (610, 140)             # le cercle est vers le bas du cadre
EQUIPES = {7: 1, 8: 1, 9: 2}    # 7 et 8 : équipe 1, 9 : équipe 2


def vol(depart, arrivee, n, sommet=-80):
    """Arc de parabole de `depart` à `arrivee` en n frames (sommet au-dessus des deux points)."""
    s = np.linspace(0, 1, n)
    x = depart[0] + (arrivee[0] - depart[0]) * s
    y = depart[1] + (arrivee[1] - depart[1]) * s + 4 * (sommet - min(depart[1], arrivee[1])) * s * (1 - s)
    return list(zip(x, y))


def scenario(segments):
    """segments : [(porteur, positions)] mis bout à bout -> (positions, possession)."""
    positions, possession = [], []
    for porteur, pts in segments:
        positions += pts
        possession += [porteur] * len(pts)
    return positions, possession


def detecter(positions, possession, panier=PANIER):
    n = len(positions)
    return DetecteurTirs(FPS, diametre_ballon=12).detecter(
        positions, possession, [panier] * n, [EQUIPES] * n)


def tenu(position, n=20):
    return [position] * n


def test_tir_rate_puis_rebond_defensif():
    rebond_rate = vol(CERCLE, (450, 300), 20, sommet=60)       # le ballon rebondit sur le cercle et repart
    positions, possession = scenario([
        (7, tenu((300, 350))),
        (-1, vol((300, 330), CERCLE, 30)),
        (-1, rebond_rate),
        (9, tenu((450, 300))),
    ])
    tirs, rebonds = detecter(positions, possession)
    assert len(tirs) == 1 and tirs[0].tireur == 7 and tirs[0].equipe == 1 and not tirs[0].reussi
    assert len(rebonds) == 1
    r = rebonds[0]
    assert (r.joueur, r.equipe, r.offensif, r.frame) == (9, 2, False, 70)


def test_rebond_offensif():
    positions, possession = scenario([
        (7, tenu((300, 350))),
        (-1, vol((300, 330), CERCLE, 30)),
        (-1, vol(CERCLE, (700, 320), 20, sommet=60)),
        (8, tenu((700, 320))),
    ])
    _, rebonds = detecter(positions, possession)
    assert rebonds[0].joueur == 8 and rebonds[0].offensif is True


def test_tir_reussi_pas_de_rebond():
    dans_le_filet = [(610, 140 + 6 * k) for k in range(1, 15)]  # descend tout droit dans le cercle
    positions, possession = scenario([
        (7, tenu((300, 350))),
        (-1, vol((300, 330), CERCLE, 30)),
        (-1, dans_le_filet),
        (9, tenu((610, 400))),   # remise en jeu : pas un rebond
    ])
    tirs, rebonds = detecter(positions, possession)
    assert len(tirs) == 1 and tirs[0].reussi
    assert rebonds == []


def test_passe_n_est_pas_un_tir():
    positions, possession = scenario([
        (7, tenu((300, 350))),
        (-1, vol((300, 340), (500, 340), 15, sommet=300)),   # passe tendue, ne monte pas
        (8, tenu((500, 340))),
    ])
    assert detecter(positions, possession) == ([], [])


def test_passe_lobee_attrapee_avant_le_panier():
    # La trajectoire visait le panier, mais un joueur attrape le ballon avant qu'il y arrive
    trajectoire = vol((300, 330), CERCLE, 30)
    positions, possession = scenario([
        (7, tenu((300, 350))),
        (-1, trajectoire[:20]),
        (8, tenu(trajectoire[19])),
    ])
    assert detecter(positions, possession) == ([], [])


def test_tir_deja_en_l_air_au_debut_de_la_video():
    positions, possession = scenario([
        (-1, vol((450, 200), CERCLE, 15)[5:]),
        (-1, vol(CERCLE, (450, 300), 20, sommet=60)),
        (9, tenu((450, 300))),
    ])
    tirs, rebonds = detecter(positions, possession)
    assert len(tirs) == 1 and tirs[0].tireur is None and not tirs[0].reussi
    assert rebonds[0].joueur == 9 and rebonds[0].offensif is None


def test_sans_panier_rien_n_est_detecte():
    positions, possession = scenario([(7, tenu((300, 350))), (-1, vol((300, 330), CERCLE, 30)), (9, tenu((450, 300)))])
    n = len(positions)
    assert DetecteurTirs(FPS).detecter(positions, possession, [None] * n) == ([], [])


@pytest.mark.parametrize("fps", [24, 30, 60])
def test_independant_des_images_par_seconde(fps):
    """Même action filmée à différentes cadences : même résultat."""
    k = fps / 30
    def echantillonner(pts):
        idx = np.linspace(0, len(pts) - 1, max(2, round(len(pts) * k))).round().astype(int)
        return [pts[i] for i in idx]
    positions, possession = scenario([
        (7, echantillonner(tenu((300, 350)))),
        (-1, echantillonner(vol((300, 330), CERCLE, 30))),
        (-1, echantillonner(vol(CERCLE, (450, 300), 20, sommet=60))),
        (9, echantillonner(tenu((450, 300)))),
    ])
    n = len(positions)
    tirs, rebonds = DetecteurTirs(fps, 12).detecter(positions, possession, [PANIER] * n, [EQUIPES] * n)
    assert len(tirs) == 1 and not tirs[0].reussi and rebonds[0].offensif is False


def test_panier_suit_la_camera_et_comble_les_trous():
    def det(x, y):
        return {"bbox": [x - 10, y - 10, x + 10, y + 10], "center": [x, y]}
    ballon = [(100, 100), (None, None), (300, 100), (300, 100), (900, 100)]
    detections = [[], [det(120, 50)], [], [det(350, 60)], [det(350, 60), det(880, 60)]]
    cadres = paniers_par_frame(detections, ballon)
    assert cadres == [(110, 40, 130, 60), (110, 40, 130, 60), (110, 40, 130, 60),
                      (340, 50, 360, 70), (870, 50, 890, 70)]
    assert paniers_par_frame([[], []], [(1, 1), (2, 2)]) == [None, None]


def test_ballon_qui_traverse_la_zone_sans_monter():
    """Passe à rebond sous le panier : elle passe dans la zone du panier sans être un tir."""
    positions, possession = scenario([
        (7, tenu((500, 180))),
        (-1, [(500 + 15 * k, 180) for k in range(1, 15)]),   # traverse la zone, sous le centre
        (8, tenu((720, 180))),
    ])
    assert detecter(positions, possession) == ([], [])


def test_alley_oop_n_est_pas_un_rebond():
    """Passe lobée attrapée près du panier puis smashée par le receveur."""
    lob = vol((300, 330), CERCLE, 30)[:25]
    smash = [tuple(np.add(lob[-1], (np.subtract(CERCLE, lob[-1])) * k / 10)) for k in range(1, 11)]
    positions, possession = scenario([
        (7, tenu((300, 350))),
        (-1, lob),
        (8, smash),                      # le receveur garde le ballon jusqu'au cercle
        (-1, [(610, 140 + 8 * k) for k in range(1, 10)]),
        (9, tenu((610, 400))),
    ])
    tirs, rebonds = detecter(positions, possession)
    assert rebonds == []
