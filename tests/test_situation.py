import pytest

from terrain_virtuel.calcul_rebond import valeur_rebond
from terrain_virtuel.config import MAX_ADVERSAIRES, POSITION_PANIER
from terrain_virtuel.export import ajouter_ligne_excel, ligne_export
from terrain_virtuel.joueurs import Joueur
from terrain_virtuel.situation import analyser_situation


def joueur(nom, x, y, taille=200, rebonds=5.0, equipe="BOS"):
    j = Joueur(nom, nom, "J", taille, rebonds, equipe)
    j.position = [x, y]
    return j


@pytest.fixture
def scene():
    x0, y0 = POSITION_PANIER[0] + 2, POSITION_PANIER[1]
    rebondeur = joueur("reb", x0, y0)
    coequipier = joueur("coeq", x0 + 2.5, y0)        # dans le rayon de 3 m
    contact = joueur("contact", x0 + 0.5, y0, equipe="LAL")
    proche = joueur("proche", x0, y0 + 1.5, equipe="LAL")
    loin = joueur("loin", x0 + 8, y0, equipe="LAL")
    return rebondeur, [rebondeur, coequipier], [contact, proche, loin]


def test_adversaires_par_rayon(scene):
    rebondeur, coequipiers, adversaires = scene
    s = analyser_situation(rebondeur, coequipiers, adversaires, 80, 75, 600, offensif=False)
    assert [a.id for a in s.adversaires_1m] == ["contact"]
    assert [a.id for a in s.adversaires_2m] == ["proche"]
    assert s.distance_panier == pytest.approx(2.0)
    assert s.diff_score == 5


def test_ratio_compte_le_rebondeur_parmi_les_coequipiers(scene):
    rebondeur, coequipiers, adversaires = scene
    s = analyser_situation(rebondeur, coequipiers, adversaires, 80, 75, 600, offensif=False)
    # 2 adversaires à moins de 3 m / (rebondeur + 1 coéquipier)
    assert s.ratio == pytest.approx(1.0)


def test_ligne_export(scene, tmp_path):
    rebondeur, coequipiers, adversaires = scene
    s = analyser_situation(rebondeur, coequipiers, adversaires, 70, 75, 30, offensif=True)
    ligne = ligne_export(s, valeur_rebond(s))
    assert len(ligne) == 11 + 4 * MAX_ADVERSAIRES
    assert ligne["Rebond_Offensif"] == 1
    assert ligne["Adv_1_Taille_1M"] == 200 and ligne["Adv_2_Taille_1M"] == ""
    assert 0.7 <= ligne["Valeur_Rebond"] <= 1.3

    fichier = tmp_path / "sortie" / "rebonds.xlsx"
    ajouter_ligne_excel(ligne, fichier)
    ajouter_ligne_excel(ligne, fichier)
    import pandas as pd
    assert len(pd.read_excel(fichier)) == 2


def test_adversaire_a_exactement_1m_compte_une_seule_fois():
    rebondeur = joueur("reb", 5.0, 5.0)
    a_1m = joueur("a1", 6.0, 5.0, equipe="LAL")
    a_2m = joueur("a2", 5.0, 7.0, equipe="LAL")
    s = analyser_situation(rebondeur, [rebondeur], [a_1m, a_2m], 80, 80, 600, offensif=False)
    assert [a.id for a in s.adversaires_1m] == ["a1"]
    assert [a.id for a in s.adversaires_2m] == ["a2"]
