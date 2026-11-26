import pytest

from terrain_virtuel.calcul_rebond import valeur_rebond_defensif, valeur_rebond_offensif


def params(**surcharges):
    """Situation neutre : rebondeur de 200 cm / 6 rebonds, seul, loin de la fin du match."""
    base = dict(
        TailleRebondeur=200, Moyenne_Rebond_rebondeur=6.0,
        Taille_adversaires_1m=[], Taille_adversaires_2m=[],
        Moyenne_Reb_adv_1m=[], Moyenne_Reb_adv_2m=[],
        DiffScore=10, TempsRestant=1000, DistBallePanier=2.0, Ratio=1.0,
    )
    base.update(surcharges)
    return base


@pytest.mark.parametrize("calcul", [valeur_rebond_defensif, valeur_rebond_offensif])
def test_valeur_toujours_dans_les_bornes(calcul):
    tres_dispute = params(Taille_adversaires_1m=[220] * 5, Moyenne_Reb_adv_1m=[15] * 5,
                          DiffScore=-1, TempsRestant=3)
    tres_facile = params(DistBallePanier=30, Ratio=0)
    assert calcul(**tres_dispute) == 1.3
    assert calcul(**tres_facile) == 0.7


def test_rebond_defensif_sans_adversaire_est_facile():
    # 1 - 0.20 (personne autour)
    assert valeur_rebond_defensif(**params()) == 0.8


def test_rebond_offensif_plus_dur_que_defensif():
    # Même situation : le rebond offensif a un malus structurel de 0.07
    assert valeur_rebond_offensif(**params()) == pytest.approx(valeur_rebond_defensif(**params()) + 0.07)


@pytest.mark.parametrize("calcul", [valeur_rebond_defensif, valeur_rebond_offensif])
def test_adversaire_au_contact_donne_au_moins_1(calcul):
    situation = params(TailleRebondeur=230, Moyenne_Rebond_rebondeur=15,
                       Taille_adversaires_1m=[180], Moyenne_Reb_adv_1m=[1.0])
    assert calcul(**situation) >= 1.0


@pytest.mark.parametrize("calcul", [valeur_rebond_defensif, valeur_rebond_offensif])
def test_fin_de_match_serree_donne_au_moins_1(calcul):
    assert calcul(**params(DiffScore=2, TempsRestant=30)) >= 1.0


def test_adversaires_plus_grands_augmentent_la_difficulte():
    petit = valeur_rebond_defensif(**params(Taille_adversaires_1m=[190], Moyenne_Reb_adv_1m=[6.0]))
    grand = valeur_rebond_defensif(**params(Taille_adversaires_1m=[215], Moyenne_Reb_adv_1m=[6.0]))
    assert grand > petit
