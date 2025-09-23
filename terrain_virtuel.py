import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

LONGUEUR_TERRAIN = 14.325 #Un terrain fait 28,65m de longueur, donc ici un demi-terrain fait 14,325m
LARGEUR_TERRAIN = 15.24


class Joueur:
    def __init__(self, joueur_id, nom, prenom, taille, stat_rebond, equipe):
        self.id = joueur_id
        self.nom = nom
        self.prenom = prenom
        self.taille = taille
        self.stat_rebond = stat_rebond
        self.equipe = equipe  # "A" ou "B"
        self.position = [0, 0]


class SituationBasket:
    def __init__(self):
        self.equipe_A = self.creer_joueurs("A", 5)
        self.equipe_B = self.creer_joueurs("B", 5)

        # Position aléatoire des joueurs -> à améliorer dans une position de 5v5 typique (joueurs en arc de cercle autour des 3 points)
        for joueur in self.equipe_A + self.equipe_B:
            joueur.position = [
                random.uniform(0, LONGUEUR_TERRAIN),
                random.uniform(0, LARGEUR_TERRAIN)
            ]

        self.rebondeur = None  # objet Joueur
        self.diff_score = 0
        self.id_situation = 0
        self.df_situations = pd.DataFrame()

    def creer_joueurs(self, equipe_nom, n):
        joueurs = []
        for i in range(n):
            joueur = Joueur(
                joueur_id=f"E{equipe_nom}_J{i + 1}",
                nom=f"Nom{i + 1}",
                prenom=f"Prenom{i + 1}",
                taille=round(random.uniform(1.80, 2.20), 2),
                stat_rebond=round(random.uniform(0.5, 1.0), 2),
                equipe=equipe_nom
            )
            joueurs.append(joueur)
        return joueurs

    def enregistrer_situation(self):
        if not self.rebondeur:
            print("Aucun rebondeur défini, situation non enregistrée.")
            return

        # Déterminer l'équipe adverse
        if self.rebondeur.equipe == "A":
            equipe_rebondeur = self.equipe_A
            equipe_adverse = self.equipe_B
        else:
            equipe_rebondeur = self.equipe_B
            equipe_adverse = self.equipe_A

        print("Equipe rebondeur: ", self.rebondeur.equipe)

        data = {
            'id_situation': self.id_situation,
            'diff_score': self.diff_score,
            'valeur_reelle': getattr(self, 'valeur_reelle', None),
            'rebondisseur_id': self.rebondeur.id,
            'equipe_rebondeur': self.rebondeur.equipe,
            'equipe_adverse_ids': [j.id for j in equipe_adverse]
        }

        joueurs = self.equipe_A + self.equipe_B
        for i, joueur in enumerate(joueurs):
            data[f'joueur_{i + 1}_id'] = joueur.id
            data[f'joueur_{i + 1}_x'] = joueur.position[0]
            data[f'joueur_{i + 1}_y'] = joueur.position[1]
            data[f'joueur_{i + 1}_equipe'] = joueur.equipe
            data[f'joueur_{i + 1}_taille'] = joueur.taille
            data[f'joueur_{i + 1}_stat_rebond'] = joueur.stat_rebond

        self.df_situations = pd.concat(
            [self.df_situations, pd.DataFrame([data])],
            ignore_index=True
        )

        self.id_situation += 1
        print(f"Situation {self.id_situation} enregistrée.")

    def afficher_dataframe(self):
        if self.df_situations.empty:
            print("Aucune situation enregistrée pour le moment.")
        else:
            print(self.df_situations)


def dessiner_terrain(ax):
    ax.plot([0, LONGUEUR_TERRAIN, LONGUEUR_TERRAIN, 0, 0],
            [0, 0, LARGEUR_TERRAIN, LARGEUR_TERRAIN, 0], 'black')
    rectangle_raquette = plt.Rectangle((0, 5.1), 5.8, 4.8, fill=False, edgecolor='black')
    ax.add_patch(rectangle_raquette)
    arc_trois_points = plt.Circle((0))
    cercle_raquette = plt.Circle((5.8, LARGEUR_TERRAIN / 2), 1.8, fill=False, color='black')
    ax.add_patch(cercle_raquette)
    panier = plt.Circle((1.6, LARGEUR_TERRAIN / 2), 0.225, fill=False, color='orange')
    ax.add_patch(panier)


class InterfaceBasket:
    def __init__(self):
        self.situation = SituationBasket()
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        dessiner_terrain(self.ax)

        self.selected_joueur = None
        self.dragging = False

        self.draw_players()

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

        self.fig.canvas.manager.set_window_title('Placement joueurs & rebondeur')
        print("Instructions:\n- Clique sur joueur pour sélectionner comme rebondeur.\n"
              "- Clique+glisse pour déplacer joueur sélectionné.\n- Ferme la fenêtre pour terminer.\n")

    def draw_players(self):
        self.ax.clear()
        dessiner_terrain(self.ax)
        joueurs = self.situation.equipe_A + self.situation.equipe_B
        for joueur in joueurs:
            x, y = joueur.position
            couleur = 'blue' if joueur.equipe == "A" else 'green'
            taille = 150 if self.situation.rebondeur == joueur else 100
            bord = 'red' if self.situation.rebondeur == joueur else 'black'
            self.ax.scatter(x, y, s=taille, c=couleur, edgecolors=bord, linewidths=2, zorder=5)
            self.ax.text(x, y + 0.3, joueur.id, ha='center', fontsize=9, zorder=10)
        self.ax.set_xlim(-1, LONGUEUR_TERRAIN + 1)
        self.ax.set_ylim(-1, LARGEUR_TERRAIN + 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.fig.canvas.draw_idle()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        x_click, y_click = event.xdata, event.ydata
        for joueur in self.situation.equipe_A + self.situation.equipe_B:
            x, y = joueur.position
            dist = np.hypot(x - x_click, y - y_click)
            if dist < 0.7:
                self.situation.rebondeur = joueur
                self.selected_joueur = joueur
                self.dragging = True
                print(f"{joueur.id} sélectionné comme rebondeur (équipe {joueur.equipe}).")
                self.draw_players()
                return
        self.selected_joueur = None

    def on_drag(self, event):
        if not self.dragging or self.selected_joueur is None or event.inaxes != self.ax:
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
            self.situation.afficher_dataframe()


if __name__ == "__main__":
    interface = InterfaceBasket()
    interface.run()
