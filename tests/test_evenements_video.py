"""Logique de jeu de l'analyse vidéo (ne nécessite ni YOLO ni OpenCV)."""
from analyse_video.evenements import BallAcquisitionDetector, PassAndInterceptionDetector, ReboundDetector


def test_passe_et_interception():
    possession = [7, 7, -1, 8, 8, -1, 3]
    equipes = [{7: 1, 8: 1, 3: 2}] * len(possession)
    d = PassAndInterceptionDetector()
    assert d.detect_passes(possession, equipes) == [-1, -1, -1, 1, -1, -1, -1]
    assert d.detect_interceptions(possession, equipes) == [-1, -1, -1, -1, -1, -1, 2]


def test_rebond_apres_tir_rate():
    # y augmente vers le bas de l'image : la balle monte (y diminue) puis redescend
    positions = [(100, 300), (100, 250), (100, 200), (100, 260), (100, 320)]
    possession = [5, -1, -1, -1, 9]
    d = ReboundDetector()
    rates = [d.detect_missed_shot(positions, (100, 150), t) for t in range(len(positions))]
    assert rates[3]  # changement de sens au sommet
    assert d.detect_rebound(rates, positions, possession, 4)
    # pas de rebond tant que personne ne récupère la balle
    assert not d.detect_rebound(rates, positions, possession, 3)


def test_possession_apres_nombre_minimal_de_frames():
    d = BallAcquisitionDetector()
    joueur = {4: {"bbox": [0, 0, 100, 200]}}
    ballon = {1: {"bbox": [40, 90, 60, 110]}}
    n = d.min_frames + 2
    possession = d.detect_ball_possession([joueur] * n, [ballon] * n)
    assert possession[: d.min_frames - 1] == [-1] * (d.min_frames - 1)
    assert possession[-1] == 4


def test_centre_panier_suit_la_camera_et_comble_les_trous():
    from analyse_video.evenements import centres_panier_par_frame
    panier = lambda x, y: {"bbox": [x - 10, y - 10, x + 10, y + 10], "center": [x, y]}
    ballon = [(100, 100), (None, None), (300, 100), (300, 100), (900, 100)]
    detections = [
        [],                                   # panier hors champ au début
        [panier(120, 50)],
        [],                                   # détection manquée
        [panier(350, 60)],                    # la caméra a bougé
        [panier(350, 60), panier(880, 60)],   # deux paniers : le plus proche du ballon
    ]
    assert centres_panier_par_frame(detections, ballon) == [
        (120, 50), (120, 50), (120, 50), (350, 60), (880, 60)]


def test_aucun_panier_dans_la_video():
    from analyse_video.evenements import centres_panier_par_frame
    assert centres_panier_par_frame([[], []], [(1, 1), (2, 2)]) == [None, None]
