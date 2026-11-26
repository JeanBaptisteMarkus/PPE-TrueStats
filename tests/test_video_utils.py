"""Utilitaires et dessins de l'analyse vidéo (les tests de dessin nécessitent OpenCV)."""
import os

import numpy as np
import pytest

from analyse_video.utils.stub_utils import read_stub, save_stub


def test_stub_aller_retour(tmp_path):
    chemin = tmp_path / "cache" / "tracks.pkl"
    save_stub(str(chemin), [{1: {"bbox": [0, 0, 1, 1]}}])
    assert read_stub(True, str(chemin)) == [{1: {"bbox": [0, 0, 1, 1]}}]


def test_stub_sans_chemin_ou_sans_dossier(tmp_path, monkeypatch):
    save_stub(None, [1, 2])  # ne doit pas planter
    monkeypatch.chdir(tmp_path)
    save_stub("tracks.pkl", [1, 2])
    assert os.path.exists(tmp_path / "tracks.pkl")


def frames(n=3):
    return [np.zeros((120, 160, 3), dtype=np.uint8) for _ in range(n)]


def test_rebound_drawer_garde_toutes_les_frames():
    pytest.importorskip("cv2")
    from analyse_video.affichage import ReboundDrawer
    entree = frames(4)
    assert len(ReboundDrawer().draw(entree, [False, 1, False, 2])) == 4


def test_ball_drawer_ne_modifie_pas_les_frames_d_entree():
    pytest.importorskip("cv2")
    from analyse_video.affichage import BallTracksDrawer
    entree = frames(1)
    sortie = BallTracksDrawer().draw(entree, [{1: {"bbox": [60, 60, 80, 80]}}])
    assert entree[0].sum() == 0 and sortie[0].sum() > 0


def test_video_de_sortie_garde_les_fps_de_la_source(tmp_path):
    cv2 = pytest.importorskip("cv2")
    from analyse_video.utils.video_utils import lire_fps, save_video
    chemin = str(tmp_path / "sortie" / "video.avi")
    save_video(frames(10), chemin, fps=60.0)
    assert lire_fps(chemin) == pytest.approx(60.0)
    assert lire_fps(str(tmp_path / "inexistante.mp4")) == 24.0


def test_aucun_ballon_detecte_ne_plante_pas():
    pytest.importorskip("ultralytics")
    pytest.importorskip("supervision")
    from analyse_video.detection.ball_tracker import BallTracker
    tracker = BallTracker.__new__(BallTracker)  # sans charger de modèle
    assert tracker.interpolate_ball_positions([{}, {}, {}]) == [{}, {}, {}]
    partiel = tracker.interpolate_ball_positions([{}, {1: {"bbox": [0, 0, 2, 2]}}, {}])
    assert all(f[1]["bbox"] == [0, 0, 2, 2] for f in partiel)
