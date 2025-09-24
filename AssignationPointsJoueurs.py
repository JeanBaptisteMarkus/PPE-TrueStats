import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import csv
from matplotlib.lines import Line2D
from matplotlib.patches import Arc
import os
import matplotlib.animation as animation

LONGUEUR_TERRAIN = 14.325
LARGEUR_TERRAIN = 15.24

# Équipes choisies
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
        self.taille = float(taille)
        self.stat_rebond = float(stat_rebond)
        self.equipe = equipe
        self.position = [0.0, 0.0]


class SituationBasket:
    def __init__(self, equipe1, equipe2):
        self.tous_joueurs_A = self.charger_tous_joueurs(equipe1)
        self.tous_joueurs_B = self.charger_tous_joueurs(equipe2)

        self.equipe_A = random.sample(self.tous_joueurs_A, min(5, len(self.tous_joueurs_A)))
        self.equipe_B = random.sample(self.tous_joueurs_B, min(5, len(self.tous_joueurs_B)))

        for joueur in self.equipe_A + self.equipe_B:
            joueur.position = [
                random.uniform(0, LONGUEUR_TERRAIN),
                random.uniform(0, LARGEUR_TERRAIN)
            ]

        self.rebondeur = None

    def charger_tous_joueurs(self, equipe_nom):
        joueurs = []
        prefix = prefix_equipe.get(equipe_nom)
        if prefix is None:
            raise ValueError(f"Préfixe inconnu pour l'équipe {equipe_nom}")

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

    def format_temps(self, secondes):
        m = secondes // 60
        s = secondes % 60
        return f"{m:02d}:{s:02d}"

    def enregistrer_situation(self, temps_restant, diff_score):
        if self.rebondeur is None:
            return

        if self.rebondeur.equipe == equipe1Nom:
            adversaires = self.equipe_B
        else:
            adversaires = self.equipe_A

        dists = []
        for adv in adversaires:
            dx = adv.position[0] - self.rebondeur.position[0]
            dy = adv.position[1] - self.rebondeur.position[1]
            d = np.hypot(dx, dy)
            dists.append((adv, d))

        dists_sorted = sorted(dists, key=lambda x: x[1])

        top3 = dists_sorted[:3]

        data = {
            "id": self.rebondeur.id,
            "surname": self.rebondeur.nom,
            "name": self.rebondeur.prenom,
            "height": self.rebondeur.taille,
            "reb_avg": self.rebondeur.stat_rebond,
            "Temps_restant": self.format_temps(temps_restant),
            "DiffScore": diff_score
        }

        for i in range(3):
            key_taille = f"tailleAdversaire{i+1}"
            key_rebond = f"AvgRebondAdversaire{i+1}"
            key_dist = f"DistanceAdversaire{i+1}Joueur"
            if i < len(top3):
                adv, dist = top3[i]
                data[key_taille] = adv.taille
                data[key_rebond] = adv.stat_rebond
                data[key_dist] = dist
            else:
                data[key_taille] = ""
                data[key_rebond] = ""
                data[key_dist] = ""

        data["Label"] = self.rebondeur.taille * self.rebondeur.stat_rebond

        df = pd.DataFrame([data])

        filename = 'situations.csv'
        file_exists = os.path.exists(filename)
        file_empty = (not file_exists) or (os.path.getsize(filename) == 0)

        df.to_csv(filename, mode='a', index=False, header=file_empty, sep=';')

class InterfaceBasket:
    def __init__(self, equipe1, equipe2):
        self.situation = SituationBasket(equipe1, equipe2)

        self.fig = plt.figure(figsize=(12, 6))
        self.ax_terrain = self.fig.add_subplot(1, 2, 1)
        self.ax_remplacement = self.fig.add_subplot(1, 2, 2)

        self.selected_joueur = None
        self.dragging = False

        # Scores aléatoires pour les deux équipes
        self.score_equipe1 = random.randint(60, 100)
        self.score_equipe2 = random.randint(60, 100)

        dessiner_terrain(self.ax_terrain)

        # Timer
        self.temps_restant = 90
        self.texte_timer = self.ax_terrain.text(LONGUEUR_TERRAIN/2, LARGEUR_TERRAIN + 0.6,
                                                self.situation.format_temps(self.temps_restant),
                                                ha='center', fontsize=16, color='red', fontweight='bold')

        # Afficher score dans le titre
        self.fig.suptitle(f"{equipe1} {self.score_equipe1}  —  {self.score_equipe2} {equipe2}", fontsize=16)

        self.draw_players()
        self.draw_remplacement_panel()

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick_remplacant)

        self.fig.canvas.manager.set_window_title('Placement joueurs & remplacement')

        self.ani = animation.FuncAnimation(self.fig, self.update_timer, interval=1000, cache_frame_data=False)

    def update_timer(self, frame):
        if self.temps_restant <= 0:
            diff = self.score_equipe1 - self.score_equipe2
            print(f"Temps écoulé ! Score final : {equipe1Nom} {self.score_equipe1} — {self.score_equipe2} {equipe2Nom}")
            # Enregistrer la situation à la toute fin
            self.situation.enregistrer_situation(self.temps_restant, diff)
            plt.close(self.fig)
            return

        # Décrémenter
        self.temps_restant -= 1
        self.texte_timer.set_text(self.situation.format_temps(self.temps_restant))
        self.fig.canvas.draw_idle()

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
            self.ax_terrain.text(x, y + 0.4, f"{joueur.prenom} {joueur.nom}", ha='center', fontsize=8, zorder=10)

        # Réécrire le texte timer après le clear
        self.texte_timer = self.ax_terrain.text(LONGUEUR_TERRAIN/2, LARGEUR_TERRAIN + 0.6,
                                                self.situation.format_temps(self.temps_restant),
                                                ha='center', fontsize=16, color='red', fontweight='bold')

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
        self.ax_remplacement.set_title(f"Remplaçants pour {self.selected_joueur.prenom} {self.selected_joueur.nom}", fontsize=12)
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
                    print(f"{joueur.prenom} {joueur.nom} sélectionné.")
                    self.draw_players()
                    self.draw_remplacement_panel()
                    return
            self.selected_joueur = None
            self.draw_players()
            self.draw_remplacement_panel()

    def on_pick_remplacant(self, event):
        if isinstance(event.artist, plt.Text):
            nom_prenom = event.artist.get_text()
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
                    print(f"Remplacement : {self.selected_joueur.prenom} {self.selected_joueur.nom} -> {joueur.prenom} {joueur.nom}")
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
        # À la fermeture manuelle, on peut décider d’enregistrer aussi :
        diff = self.score_equipe1 - self.score_equipe2
        self.situation.enregistrer_situation(self.temps_restant, diff)


def dessiner_terrain(ax):
    ax.plot([0, LONGUEUR_TERRAIN, LONGUEUR_TERRAIN, 0, 0],
            [0, 0, LARGEUR_TERRAIN, LARGEUR_TERRAIN, 0], 'black')
    rectangle_raquette = plt.Rectangle((0, 5.18), 5.8, 4.8, fill=False, edgecolor='black')
    ax.add_patch(rectangle_raquette)
    ligne_corner_bas = Line2D([0, 4.6], [14.214, 14.214], color='black', linewidth=1)
    ax.add_line(ligne_corner_bas)
    ligne_corner_bas2 = Line2D([0, 4.6], [1.026, 1.026], color='black', linewidth=1)
    ax.add_line(ligne_corner_bas2)
    arc_trois_points = Arc((1.6, LARGEUR_TERRAIN / 2), 2*7.24, 2*7.24, theta1=-66, theta2=66, edgecolor='black')
    ax.add_patch(arc_trois_points)
    cercle_raquette = plt.Circle((5.8, LARGEUR_TERRAIN / 2), 1.8, fill=False, color='black')
    ax.add_patch(cercle_raquette)
    panier = plt.Circle((1.6, LARGEUR_TERRAIN / 2), 0.225, fill=False, color='orange')
    ax.add_patch(panier)


if __name__ == "__main__":
    interface = InterfaceBasket(equipe1Nom, equipe2Nom)
    interface.run()
