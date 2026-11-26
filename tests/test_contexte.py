import random

from terrain_virtuel.interface.contexte import completer_equipes


def test_tirage_aleatoire_jamais_la_meme_equipe():
    rng = random.Random(0)
    for _ in range(500):
        e1, e2 = completer_equipes("", "", rng)
        assert e1 != e2
        assert completer_equipes("", "Boston Celtics", rng)[0] != "Boston Celtics"
        assert completer_equipes("Boston Celtics", "", rng)[1] != "Boston Celtics"


def test_choix_utilisateur_conserves():
    assert completer_equipes("Miami Heat", "Utah Jazz") == ("Miami Heat", "Utah Jazz")
