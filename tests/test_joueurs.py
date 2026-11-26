from collections import Counter

from terrain_virtuel.config import FICHIER_JOUEURS
from terrain_virtuel.joueurs import EQUIPES_NBA, charger_joueurs, selectionner_joueurs


def test_fichier_joueurs_complet():
    joueurs = charger_joueurs(FICHIER_JOUEURS)
    par_equipe = Counter(j.equipe for j in joueurs)
    assert set(par_equipe) == set(EQUIPES_NBA.values())
    assert all(n >= 5 for n in par_equipe.values())
    assert len({j.id for j in joueurs}) == len(joueurs)


def test_fichier_joueurs_bien_encode():
    texte = FICHIER_JOUEURS.read_text(encoding="utf-8")
    assert "Ã" not in texte  # trace de double encodage UTF-8


def test_selection_cinq_joueurs_distincts():
    joueurs = charger_joueurs(FICHIER_JOUEURS)
    cinq = selectionner_joueurs(joueurs, "BOS", 5)
    assert len(set(cinq)) == 5 and all(j.equipe == "BOS" for j in cinq)
