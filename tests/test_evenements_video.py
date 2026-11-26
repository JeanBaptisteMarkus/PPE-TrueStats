"""Logique de jeu de l'analyse vidéo (ne nécessite ni YOLO ni OpenCV)."""
from analyse_video.evenements import BallAcquisitionDetector, PassAndInterceptionDetector


def test_passe_et_interception():
    possession = [7, 7, -1, 8, 8, -1, 3]
    equipes = [{7: 1, 8: 1, 3: 2}] * len(possession)
    d = PassAndInterceptionDetector()
    assert d.detect_passes(possession, equipes) == [-1, -1, -1, 1, -1, -1, -1]
    assert d.detect_interceptions(possession, equipes) == [-1, -1, -1, -1, -1, -1, 2]


def test_possession_apres_nombre_minimal_de_frames():
    d = BallAcquisitionDetector()
    joueur = {4: {"bbox": [0, 0, 100, 200]}}
    ballon = {1: {"bbox": [40, 90, 60, 110]}}
    n = d.min_frames + 2
    possession = d.detect_ball_possession([joueur] * n, [ballon] * n)
    assert possession[: d.min_frames - 1] == [-1] * (d.min_frames - 1)
    assert possession[-1] == 4
