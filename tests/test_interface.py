"""Test de fumée de l'interface matplotlib (backend sans affichage)."""
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from terrain_virtuel.config import FICHIER_JOUEURS  # noqa: E402
from terrain_virtuel.interface.gestionnaire import GestionnaireJoueurs  # noqa: E402
from terrain_virtuel.joueurs import charger_joueurs  # noqa: E402


def test_selection_deplacement_remplacement():
    joueurs = charger_joueurs(FICHIER_JOUEURS)
    bos = [j for j in joueurs if j.equipe == "BOS"]
    lal = [j for j in joueurs if j.equipe == "LAL"]
    eq1, banc1, eq2, banc2 = bos[:5], bos[5:], lal[:5], lal[5:]
    for i, j in enumerate(eq1 + eq2):
        j.position = [1.0 + i, 2.0 + i]

    fig = plt.figure()
    ax_terrain, ax_remp = fig.add_subplot(1, 2, 1), fig.add_subplot(1, 2, 2)
    g = GestionnaireJoueurs(fig, ax_terrain, ax_remp, eq1, eq2, banc1, banc2)
    g.draw_players()
    g.draw_remplacement_panel()

    cible = eq1[0]
    g.on_click(SimpleNamespace(inaxes=ax_terrain, xdata=cible.position[0], ydata=cible.position[1]))
    assert g.joueur_selectionne is cible

    g.on_drag(SimpleNamespace(inaxes=ax_terrain, xdata=3.0, ydata=4.0))
    g.on_release(None)
    assert cible.position == [3.0, 4.0]

    remplacant = banc1[0]
    texte = plt.Text(0, 0, f"1. {remplacant.nom_complet}")
    g.on_pick_remplacant(SimpleNamespace(artist=texte))
    assert eq1[0] is remplacant and cible in banc1
    assert remplacant.position == [3.0, 4.0]
    plt.close(fig)
