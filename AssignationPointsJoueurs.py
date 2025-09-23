import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import csv
from matplotlib.lines import Line2D
from matplotlib.patches import Arc


LONGUEUR_TERRAIN = 14.325
LARGEUR_TERRAIN = 15.24

# Equipes choisies
equipe1Nom = "DallasMavericks"
equipe2Nom = "LosAngelesLakers"

prefix_equipe = {
    "DallasMavericks": "DAL",
    "LosAngelesLakers": "LAL",
}


class Joueur:
    def __init__(self, joueur_id, nom, prenom, taille, stat_rebond, equipe):
        self.id = joueur_id
        self.nom = nom
        self.prenom = prenom
        self.taille = taille
        self.stat_rebond = stat_rebond
        self.equipe = equipe
        self.position = [0, 0]

class SituationBasket:
    def __init__(self, equipe1, equipe2):
        # Charger tous les joueurs disponibles pour chaque équipe
        self.tous_joueurs_A = self.charger_tous_joueurs(equipe1)
        self.tous_joueurs_B = self.charger_tous_joueurs(equipe2)

        # Choisir 5 joueurs "en jeu" aléatoirement
        self.equipe_A = random.sample(self.tous_joueurs_A, min(5, len(self.tous_joueurs_A)))
        self.equipe_B = random.sample(self.tous_joueurs_B, min(5, len(self.tous_joueurs_B)))

        # Initialiser position aléatoire pour ceux sur terrain
        for joueur in self.equipe_A + self.equipe_B:
            joueur.position = [
                random.uniform(0, LONGUEUR_TERRAIN),
                random.uniform(0, LARGEUR_TERRAIN)
            ]

        self.rebondeur = None
        self.diff_score = 0
        self.id_situation = 0
        self.df_situations = pd.DataFrame()

    def charger_tous_joueurs(self, equipe_nom):
        joueurs = []
        prefix = prefix_equipe.get(equipe_nom)
        if prefix is None:
            raise ValueError(f"Prefixe ID inconnu pour l'équipe {equipe_nom}")

        with open('InfosJoueurs', newline='', encoding='utf-8') as f:
            attributs = csv.DictReader(f, delimiter=',')
            for ligne in attributs:
                if ligne["ID"].startswith(prefix):
                    joueur = Joueur(
                        joueur_id=ligne["ID"],
                        nom=ligne["Nom"],
                        prenom=ligne["Prenom"],
                        taille=ligne["Taille"],
                        stat_rebond=ligne["AverageRebond"],
                        equipe=equipe_nom
                    )
                    joueurs.append(joueur)
        return joueurs

    def remplacer_joueur(self, joueur_a_remplacer, nouveau_joueur):
        if joueur_a_remplacer.equipe == equipe1Nom:
            idx = self.equipe_A.index(joueur_a_remplacer)
            self.equipe_A[idx] = nouveau_joueur
        else:
            idx = self.equipe_B.index(joueur_a_remplacer)
            self.equipe_B[idx] = nouveau_joueur

        nouveau_joueur.position = joueur_a_remplacer.position

    #Fonction pour ajouter la ligne correspondante à la situation de rebond (avec stats du rebondeur etc) dans le csv
    def enregistrer_situation(self):
        data = []
        data.append({
            "id": self.rebondeur.id,
            "surname": self.rebondeur.nom,
            "name": self.rebondeur.prenom,
            "height": self.rebondeur.taille,
            "reb_avg": self.rebondeur.stat_rebond
        })

        df = pd.DataFrame(data)
        #Ajouter au csv
        df.to_csv("situations.csv", mode="a", header=False, index=False)



class InterfaceBasket:
    def __init__(self, equipe1, equipe2):
        self.situation = SituationBasket(equipe1, equipe2)

        self.fig = plt.figure(figsize=(12, 6))
        self.ax_terrain = self.fig.add_subplot(1, 2, 1)
        self.ax_remplacement = self.fig.add_subplot(1, 2, 2)

        self.selected_joueur = None
        self.dragging = False

        dessiner_terrain(self.ax_terrain)
        self.draw_players()
        self.draw_remplacement_panel()

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick_remplacant)  # <== Connect pick_event

        self.fig.canvas.manager.set_window_title('Placement joueurs & remplacement')

    def draw_players(self):
        self.ax_terrain.clear()
        dessiner_terrain(self.ax_terrain)
        joueurs = self.situation.equipe_A + self.situation.equipe_B
        for joueur in joueurs:
            x, y = joueur.position
            couleur = 'blue' if joueur.equipe == equipe1Nom else 'green'
            taille = 150 if self.selected_joueur == joueur else 100
            bord = 'red' if self.selected_joueur == joueur else 'black'
            self.ax_terrain.scatter(x, y, s=taille, c=couleur, edgecolors=bord, linewidths=2, zorder=5)
            # Affiche prénom + nom au-dessus du cercle
            self.ax_terrain.text(x, y + 0.4, f"{joueur.prenom} {joueur.nom}", ha='center', fontsize=8, zorder=10)
        self.ax_terrain.set_xlim(-1, LONGUEUR_TERRAIN + 1)
        self.ax_terrain.set_ylim(-1, LARGEUR_TERRAIN + 1)
        self.ax_terrain.set_aspect('equal')
        self.ax_terrain.axis('off')
        self.fig.canvas.draw_idle()

    def draw_remplacement_panel(self):
        self.ax_remplacement.clear()
        self.ax_remplacement.axis('off')

        if self.selected_joueur is None:
            return

        if self.selected_joueur.equipe == equipe1Nom:
            tous = self.situation.tous_joueurs_A
            sur_terrain = self.situation.equipe_A
        else:
            tous = self.situation.tous_joueurs_B
            sur_terrain = self.situation.equipe_B

        remplaçants = [j for j in tous if j not in sur_terrain]

        if not remplaçants:
            self.ax_remplacement.text(0.5, 0.5, "Pas de remplaçants disponibles", ha='center', va='center', fontsize=12)
            self.fig.canvas.draw_idle()
            return

        self.ax_remplacement.set_title(f"Remplaçants pour {self.selected_joueur.prenom} {self.selected_joueur.nom}",
                                       fontsize=12)

        y = 0.9
        for joueur in remplaçants:
            self.ax_remplacement.text(0.1, y, f"{joueur.prenom} {joueur.nom}", fontsize=10, ha='left', va='center',
                                      picker=True, color='blue')
            y -= 0.1
            if y < 0:
                break

        self.fig.canvas.draw_idle()

    def on_click(self, event):
        if event.inaxes == self.ax_terrain:
            x_click, y_click = event.xdata, event.ydata
            for joueur in self.situation.equipe_A + self.situation.equipe_B:
                x, y = joueur.position
                dist = np.hypot(x - x_click, y - y_click)
                if dist < 0.7:
                    self.selected_joueur = joueur
                    self.situation.rebondeur = joueur
                    self.dragging = True
                    print(f"{joueur.prenom} {joueur.nom} sélectionné sur le terrain.")
                    self.draw_players()
                    self.draw_remplacement_panel()
                    return
            self.selected_joueur = None
            self.draw_players()
            self.draw_remplacement_panel()

    def on_pick_remplacant(self, event):
        if isinstance(event.artist, plt.Text):
            text = event.artist
            nom_prenom = text.get_text()
            if self.selected_joueur is None:
                return
            if self.selected_joueur.equipe == equipe1Nom:
                tous = self.situation.tous_joueurs_A
                sur_terrain = self.situation.equipe_A
            else:
                tous = self.situation.tous_joueurs_B
                sur_terrain = self.situation.equipe_B

            remplaçants = [j for j in tous if j not in sur_terrain]

            for joueur in remplaçants:
                if f"{joueur.prenom} {joueur.nom}" == nom_prenom:
                    print(f"Remplacement: {self.selected_joueur.prenom} {self.selected_joueur.nom} -> {joueur.prenom} {joueur.nom}")
                    self.situation.remplacer_joueur(self.selected_joueur, joueur)
                    self.selected_joueur = joueur
                    self.draw_players()
                    self.draw_remplacement_panel()
                    break

    def on_drag(self, event):
        if not self.dragging or self.selected_joueur is None or event.inaxes != self.ax_terrain:
            return
        x_new, y_new = event.xdata, event.ydata
        x_new = np.clip(x_new, 0, LONGUEUR_TERRAIN)
        y_new = np.clip(y_new, 0, LARGEUR_TERRAIN)
        self.selected_joueur.position = [x_new, y_new]
        self.draw_players()

    def on_release(self, event):
        self.dragging = False

    def run(self):
        plt.show()
        if not self.situation.rebondeur:
            print("Aucun rebondeur sélectionné, situation non enregistrée.")
        else:
            print("Enregistrement de la situation...")
            self.situation.enregistrer_situation()

def dessiner_terrain(ax):
    ax.plot([0, LONGUEUR_TERRAIN, LONGUEUR_TERRAIN, 0, 0],
            [0, 0, LARGEUR_TERRAIN, LARGEUR_TERRAIN, 0], 'black')
    rectangle_raquette = plt.Rectangle((0, 5.18), 5.8, 4.8, fill=False, edgecolor='black')
    ax.add_patch(rectangle_raquette)
    ligne_corner_bas = Line2D([0, 4.6], [14.214, 14.214], color='black', linewidth=1)
    ax.add_line(ligne_corner_bas)
    ligne_corner_bas = Line2D([0, 4.6], [1.026, 1.026], color='black', linewidth=1)
    ax.add_line(ligne_corner_bas)
    arc_trois_points = Arc((1.6, LARGEUR_TERRAIN / 2), 2*7.24, 2*7.24, theta1=-66, theta2=66, edgecolor='black')
    ax.add_patch(arc_trois_points)
    cercle_raquette = plt.Circle((5.8, LARGEUR_TERRAIN / 2), 1.8, fill=False, color='black')
    ax.add_patch(cercle_raquette)
    panier = plt.Circle((1.6, LARGEUR_TERRAIN / 2), 0.225, fill=False, color='orange')
    ax.add_patch(panier)

if __name__ == "__main__":
    interface = InterfaceBasket(equipe1Nom, equipe2Nom)
    interface.run()