"""Attribution des équipes par couleur de maillot (nécessite OpenCV)."""
import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from analyse_video.equipes import EquipesParCouleur, couleur_maillot, kmeans_pondere  # noqa: E402

PARQUET = (90, 160, 210)  # BGR, bois clair


def joueur(frame, x, y, maillot, peau=(60, 90, 140), short=None):
    """Dessine un joueur de 40x100 px : tête, maillot, short, jambes."""
    cv2.rectangle(frame, (x + 12, y), (x + 28, y + 15), peau, -1)
    cv2.rectangle(frame, (x, y + 15), (x + 40, y + 50), maillot, -1)
    cv2.rectangle(frame, (x, y + 50), (x + 40, y + 65), short or maillot, -1)
    cv2.rectangle(frame, (x + 8, y + 65), (x + 32, y + 100), peau, -1)
    return [x, y, x + 40, y + 100]


def match(couleur_a, couleur_b, n_frames=6, bruit=0):
    rng = np.random.default_rng(1)
    frames, tracks = [], []
    for i in range(n_frames):
        frame = np.zeros((300, 700, 3), np.uint8)
        frame[:] = PARQUET
        pistes = {}
        for k in range(5):
            pistes[k] = {"bbox": joueur(frame, 20 + 60 * k + i, 30, couleur_a)}
            pistes[10 + k] = {"bbox": joueur(frame, 20 + 60 * k + i, 170, couleur_b)}
        if bruit:
            frame[:] = np.clip(frame.astype(int) + rng.integers(-bruit, bruit, frame.shape), 0, 255)
        frames.append(frame)
        tracks.append(pistes)
    return frames, tracks


@pytest.mark.parametrize("clair,fonce", [
    ((235, 235, 235), (40, 120, 30)),   # blanc / vert
    ((60, 60, 220), (40, 120, 30)),     # rouge / vert
    ((60, 60, 220), (20, 20, 20)),      # rouge / noir
])
def test_deux_equipes_separees_equipe_1_la_plus_claire(clair, fonce):
    frames, tracks = match(clair, fonce, bruit=15)
    e = EquipesParCouleur()
    assignation = e.get_player_teams_across_frames(frames, tracks)
    clair_est_1 = np.mean(clair) > np.mean(fonce)
    attendu_a, attendu_b = (1, 2) if clair_est_1 else (2, 1)
    for frame in assignation:
        assert all(frame[k] == attendu_a for k in range(5))
        assert all(frame[10 + k] == attendu_b for k in range(5))
    assert e.attribution_fiable()


def test_meme_couleur_dans_deux_matchs_differents():
    """Équipe A (rouge) / B (vert) puis C (rouge) / B (vert) : chaque vidéo est traitée seule."""
    rouge, vert, rouge_c = (60, 60, 220), (40, 120, 30), (50, 70, 200)
    for couleur_rouge in (rouge, rouge_c):
        frames, tracks = match(couleur_rouge, vert)
        assignation = EquipesParCouleur().get_player_teams_across_frames(frames, tracks)
        assert {assignation[0][k] for k in range(5)} != {assignation[0][10 + k] for k in range(5)}


def test_couleurs_trop_proches_signalees():
    frames, tracks = match((40, 120, 30), (45, 125, 35))
    e = EquipesParCouleur()
    e.get_player_teams_across_frames(frames, tracks)
    assert not e.attribution_fiable()


def test_cas_limites():
    frame = np.zeros((100, 100, 3), np.uint8)
    e = EquipesParCouleur()
    assert e.get_player_teams_across_frames([frame, frame], [{}, {}]) == [{}, {}]
    assert couleur_maillot(frame, [10, 10, 12, 12]) is None  # joueur trop petit
    seul = e.get_player_teams_across_frames([frame], [{7: {"bbox": [10, 10, 60, 90]}}])
    assert seul == [{7: 1}]


def test_cache_reutilise(tmp_path):
    frames, tracks = match((235, 235, 235), (40, 120, 30))
    chemin = str(tmp_path / "equipes.pkl")
    premier = EquipesParCouleur()
    attendu = premier.get_player_teams_across_frames(frames, tracks, stub_path=chemin)
    second = EquipesParCouleur()
    assert second.get_player_teams_across_frames(frames, [{}] * len(frames), read_from_stub=True,
                                                 stub_path=chemin) == attendu
    assert second.couleurs_equipes == premier.couleurs_equipes


def test_kmeans_pondere_deterministe():
    points = np.array([[0, 0], [1, 0], [10, 10], [11, 10]], float)
    l1, _ = kmeans_pondere(points, 2)
    l2, _ = kmeans_pondere(points, 2)
    assert (l1 == l2).all() and l1[0] == l1[1] != l1[2] == l1[3]
