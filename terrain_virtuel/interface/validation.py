"""Bouton « Valider » et case « Rebond Offensif » : analyse et export du rebond choisi."""
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons

from ..calcul_rebond import valeur_rebond
from ..config import FICHIER_EXPORT
from ..export import ajouter_ligne_excel, ligne_export
from ..situation import analyser_situation


def extraire_donnee(gestionnaire, fig, score_equipe1, score_equipe2, temps_restant,
                    fichier_export=FICHIER_EXPORT):
    """Affiche le terrain et attend que l'utilisateur valide un rebondeur.

    Au clic sur « Valider », la situation du joueur sélectionné est analysée,
    sa valeur de rebond est calculée et affichée, puis la ligne est ajoutée au
    fichier Excel. Retourne le rebondeur choisi (ou None si la fenêtre est fermée).
    """
    rebondeur = None

    def valider_rebondeur(event):
        nonlocal rebondeur

        if gestionnaire.joueur_selectionne is None:
            print("Aucun joueur sélectionné. Veuillez cliquer sur un joueur avant de valider.")
            return

        rebondeur = gestionnaire.joueur_selectionne

        # Équipe du rebondeur et équipe adverse
        if rebondeur in gestionnaire.joueurs_equipe1:
            coequipiers, adversaires = gestionnaire.joueurs_equipe1, gestionnaire.joueurs_equipe2
            score_equipe, score_adverse = score_equipe1, score_equipe2
        else:
            coequipiers, adversaires = gestionnaire.joueurs_equipe2, gestionnaire.joueurs_equipe1
            score_equipe, score_adverse = score_equipe2, score_equipe1

        offensif = checkbox.get_status()[0]
        situation = analyser_situation(rebondeur, coequipiers, adversaires,
                                       score_equipe, score_adverse, temps_restant, offensif)
        valeur = valeur_rebond(situation)
        print(f"Valeur du rebond : {valeur}")

        ajouter_ligne_excel(ligne_export(situation, valeur), fichier_export)
        plt.close(fig)

    ax_bouton = plt.axes([0.4, 0.02, 0.2, 0.05])
    bouton = Button(ax_bouton, 'Valider')
    bouton.on_clicked(valider_rebondeur)

    ax_checkbox = plt.axes([0.35, 0.08, 0.3, 0.04])
    checkbox = CheckButtons(ax_checkbox, ['Rebond Offensif'], [False])

    # Bloquant jusqu'à la fermeture de la fenêtre
    plt.show()
    return rebondeur
