import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import random
import csv
from matplotlib.lines import Line2D
from matplotlib.patches import Arc
import os
import matplotlib.animation as animation
from matplotlib.widgets import TextBox, Button

LONGUEUR_TERRAIN = 14.325
LARGEUR_TERRAIN = 15.24

# Dictionnaire des équipes NBA avec leurs abréviations
equipes_NBA = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
}


# Classe Joueur pour stocker les informations des joueurs
class Joueur:
    def __init__(self, joueur_id, nom, prenom, taille, stat_rebond, equipe):
        self.id = joueur_id
        self.nom = nom
        self.prenom = prenom
        self.taille = float(taille)
        self.stat_rebond = float(stat_rebond)
        self.equipe = equipe
        self.position = [0.0, 0.0]


 
# Fonction pour le menu de choix du contexte du match (interface graphique)
def choix_contexte_tkinter():

    equipe1=None
    equipe2=None
    score_equipe1=None
    score_equipe2=None
    temps_restant=None

    fenetre = tk.Tk()
    fenetre.title("Choix du contexte du match")
    fenetre.geometry("500x500")


    # ***choix de la première équipe***
    ttk.Label(fenetre, text="Équipe 1 :").grid(row=0, column=0, padx=10, pady=10, sticky="w") # permet d'afficher un texte
    menu_deroulant1 = ttk.Combobox(fenetre, values=list(equipes_NBA.keys()),state="readonly") # ttk.Combobox menu déroulant avec les équipes NBA, menu_deroulant1 est le nom du menu
    menu_deroulant1.grid(row=0, column=1, padx=10) # place le menu a côté du label
    # ***entrée pour le score de la première équipe***
    ttk.Label(fenetre, text="Score équipe 1 :").grid(row=0, column=2, padx=10,sticky="w")
    choix_score_equipe1 = tk.Entry(fenetre,width=5)
    choix_score_equipe1.grid(row=0, column=3)


    # ***choix de la deuxième équipe***
    ttk.Label(fenetre, text="Équipe 2 :").grid(row=1, column=0, padx=10, pady=10, sticky="w") # permet d'afficher un texte
    menu_deroulant2 = ttk.Combobox(fenetre, values=list(equipes_NBA.keys()),state="readonly") # ttk.Combobox menu déroulant avec les équipes NBA, menu_deroulant2 est le nom du menu
    menu_deroulant2.grid(row=1, column=1, padx=10) # place le menu a côté du label
    # ***entrée pour le score de la deuxième équipe***
    ttk.Label(fenetre, text="Score équipe 2 :").grid(row=1, column=2, padx=10)
    choix_score_equipe2 = tk.Entry(fenetre,width=5)
    choix_score_equipe2.grid(row=1, column=3)


    # ***Choix du temps restant***
    ttk.Label(fenetre, text="Temps restant (en secondes) :").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    choix_temps_restant = tk.Entry(fenetre,width=5)
    choix_temps_restant.grid(row=2, column=1, padx=10)

    # ***Bouton de validation du contexte***
    def valider_choix():
        nonlocal equipe1, equipe2, score_equipe1, score_equipe2, temps_restant
        equipe1 = equipes_NBA[menu_deroulant1.get()] # Récupère l'abréviation de l'équipe 1
        equipe2 = equipes_NBA[menu_deroulant2.get()] # Récupère l'abréviation de l'équipe 2
        score_equipe1 = int(choix_score_equipe1.get()) # Récupère le score de l'équipe 1
        score_equipe2 = int(choix_score_equipe2.get()) # Récupère le score de l'équipe 2
        temps_restant = int(choix_temps_restant.get()) # Récupère le temps restant
        fenetre.destroy()  # Ferme la fenêtre après la sélection

    tk.Button(fenetre, text="Valider", command=valider_choix).grid(row=3, column=0, columnspan=4, pady=20)    
    fenetre.mainloop()
    return equipe1, equipe2, score_equipe1, score_equipe2, temps_restant    

equipe1,equipe2,score_equipe1, score_equipe2, temps_restant  =choix_contexte_tkinter() # Appel de la fonction pour choisir le contexte du match


# Fonction pour charger les joueurs depuis un fichier CSV
def charger_joueurs(nom_fichier):
    df = pd.read_csv(nom_fichier) # lit le fichier CSV et le stocke dans un DataFrame pandas
    joueurs = []
    for index, row in df.iterrows(): # itère sur chaque ligne du DataFrame
        joueur = Joueur(row['ID'], row['Nom'], row['Prenom'], row['Taille'], row['AverageRebond'], row['Equipe']) # Crée un objet Joueur pour chaque ligne du fichier CSV
        joueurs.append(joueur) # Ajoute le joueur à la liste des joueurs
    return joueurs # Retourne la liste des joueurs chargés depuis le fichier CSV


# Fonction pour sélectionner 5 joueurs aléatoires d'une équipe
def selectionner_joueurs(joueurs, equipe, nombre=5):
    joueurs_equipe = [j for j in joueurs if j.equipe == equipe]
    return random.sample(joueurs_equipe, min(nombre, len(joueurs_equipe)))


# Classe pour gérer l'interaction avec les joueurs
class GestionnaireJoueurs:
    """
    Cette classe gère 
    l'affichage des joueurs sur le terrain, 
    la sélection d'un joueur, et le remplacement d'un joueur par un remplaçant disponible. 
    Elle utilise les événements de souris pour permettre à l'utilisateur de cliquer sur un joueur pour le sélectionner, de faire glisser un joueur pour le déplacer sur le terrain, et de cliquer sur un remplaçant dans le panneau de remplacement pour effectuer un remplacement.
    """
    def __init__(self, fig, ax_terrain, ax_remplacements, joueurs_equipe1, joueurs_equipe2, joueurs_restants1, joueurs_restants2):
        """ 
        Constructeur de la classe.
        - fig : la figure matplotlib principale.
        - ax_terrain : l'axe où le terrain et les joueurs sont affichés.
        - ax_remplacements : l'axe où le panneau de remplacements est affiché.
        - joueurs_equipe1 : liste des joueurs sur le terrain pour l'équipe 1.
        - joueurs_equipe2 : liste des joueurs sur le terrain pour l'équipe 2.
        - joueurs_restants1 : liste des remplaçants pour l'équipe 1.
        - joueurs_restants2 : liste des remplaçants pour l'équipe 2.
        """
        self.fig = fig
        self.ax_terrain = ax_terrain
        self.ax_remplacements = ax_remplacements
        self.joueurs_equipe1 = joueurs_equipe1
        self.joueurs_equipe2 = joueurs_equipe2
        self.joueurs_restants1 = joueurs_restants1
        self.joueurs_restants2 = joueurs_restants2
        self.joueur_selectionne = None
        self.dragging = False
        
    # Retourne le nom complet d'un joueur sous forme 'Prénom Nom'.    
    def obtenir_nom_complet(self, joueur):
        return f"{joueur.prenom} {joueur.nom}"
    
    def remplacer_joueur(self, joueur_a_remplacer, nouveau_joueur):
        # Si le joueur à remplacer est dans l'équipe 1
        if joueur_a_remplacer in self.joueurs_equipe1:
            idx = self.joueurs_equipe1.index(joueur_a_remplacer) # on recupère son index dans la liste des joueurs sur le terrain
            self.joueurs_equipe1[idx] = nouveau_joueur # on remplace ce joueur par le nouveau joueur
            nouveau_joueur.position = joueur_a_remplacer.position.copy() # le remplaçant prend la position du joueur remplacé
            self.joueurs_restants1.append(joueur_a_remplacer) # on ajoute le joueur remplacé à la liste des remplaçants
            self.joueurs_restants1.remove(nouveau_joueur) # on retire le nouveau joueur de la liste des remplaçants
        else:
            # Si le joueur à remplacer est dans l'équipe 2
            idx = self.joueurs_equipe2.index(joueur_a_remplacer) # on recupère son index dans la liste des joueurs sur le terrain
            self.joueurs_equipe2[idx] = nouveau_joueur # on remplace ce joueur par le nouveau joueur
            nouveau_joueur.position = joueur_a_remplacer.position.copy() # le remplaçant prend la position du joueur remplacé
            self.joueurs_restants2.append(joueur_a_remplacer) # on ajoute le joueur remplacé à la liste des remplaçants
            self.joueurs_restants2.remove(nouveau_joueur) # on retire le nouveau joueur de la liste des remplaçants
        
        self.joueur_selectionne = nouveau_joueur # le nouveau joueur devient le joueur sélectionné après le remplacement
    
    def draw_players(self):
        self.ax_terrain.clear()
        dessiner_terrain(self.ax_terrain)
        
        joueurs = self.joueurs_equipe1 + self.joueurs_equipe2
        for joueur in joueurs:
            x, y = joueur.position
            couleur = 'blue' if joueur in self.joueurs_equipe1 else 'red'
            taille = 150 if self.joueur_selectionne == joueur else 100
            bord = 'yellow' if self.joueur_selectionne == joueur else 'black'
            self.ax_terrain.scatter(x, y, s=taille, c=couleur, edgecolors=bord, linewidths=2, zorder=5)
            self.ax_terrain.text(x, y + 0.4, self.obtenir_nom_complet(joueur), ha='center', fontsize=8, zorder=10)
        
        self.ax_terrain.set_xlim(-1, LONGUEUR_TERRAIN + 1)
        self.ax_terrain.set_ylim(-1, LARGEUR_TERRAIN + 1)
        self.ax_terrain.set_aspect('equal')
        self.ax_terrain.axis('off')
        self.fig.canvas.draw_idle()
    
    def draw_remplacement_panel(self):
        self.ax_remplacements.clear()
        self.ax_remplacements.axis('off')
        
        if self.joueur_selectionne is None:
            self.ax_remplacements.text(0.5, 0.5, 'Cliquez sur un joueur\npour le remplacer', 
                                     ha='center', va='center', fontsize=12, transform=self.ax_remplacements.transAxes)
            self.fig.canvas.draw_idle()
            return
        
        if self.joueur_selectionne in self.joueurs_equipe1:
            tous = [j for j in self.joueurs_equipe1 + self.joueurs_restants1 if j.equipe == self.joueur_selectionne.equipe]
            sur_terrain = self.joueurs_equipe1
        else:
            tous = [j for j in self.joueurs_equipe2 + self.joueurs_restants2 if j.equipe == self.joueur_selectionne.equipe]
            sur_terrain = self.joueurs_equipe2
        
        remplaçants = [j for j in tous if j not in sur_terrain]
        
        if not remplaçants:
            self.ax_remplacements.text(0.5, 0.5, "Pas de remplaçants disponibles", 
                                     ha='center', va='center', fontsize=12, transform=self.ax_remplacements.transAxes)
            self.fig.canvas.draw_idle()
            return
        
        title_text = f"Remplaçants pour\n{self.obtenir_nom_complet(self.joueur_selectionne)}"
        self.ax_remplacements.text(0.5, 0.95, title_text, fontsize=11, weight='bold', 
                                 ha='center', va='top', transform=self.ax_remplacements.transAxes)
        
        y = 0.85
        for idx, joueur in enumerate(remplaçants):
            text_obj = self.ax_remplacements.text(0.1, y, f"{idx + 1}. {self.obtenir_nom_complet(joueur)}", 
                                                fontsize=10, ha='left', va='center',
                                                picker=True, color='blue', transform=self.ax_remplacements.transAxes)
            y -= 0.10
            if y < 0:
                break
        
        self.fig.canvas.draw_idle()
    
    def on_click(self, event):
        if event.inaxes == self.ax_terrain:
            x_click, y_click = event.xdata, event.ydata
            for joueur in self.joueurs_equipe1 + self.joueurs_equipe2:
                x, y = joueur.position
                dist = np.hypot(x - x_click, y - y_click)
                if dist < 0.7:
                    self.joueur_selectionne = joueur
                    self.dragging = True
                    self.draw_players()
                    self.draw_remplacement_panel()
                    return
            
            self.joueur_selectionne = None
            self.dragging = False
            self.draw_players()
            self.draw_remplacement_panel()
    
    def on_pick_remplacant(self, event):
        if isinstance(event.artist, plt.Text) and self.joueur_selectionne:
            nom_prenom = event.artist.get_text()
            # Extraire le nom du texte (enlever le numéro)
            if '. ' in nom_prenom:
                nom_prenom = nom_prenom.split('. ', 1)[1]
            
            # Récupérer les remplaçants disponibles
            if self.joueur_selectionne in self.joueurs_equipe1:
                tous = [j for j in self.joueurs_equipe1 + self.joueurs_restants1 if j.equipe == self.joueur_selectionne.equipe]
                sur_terrain = self.joueurs_equipe1
            else:
                tous = [j for j in self.joueurs_equipe2 + self.joueurs_restants2 if j.equipe == self.joueur_selectionne.equipe]
                sur_terrain = self.joueurs_equipe2
            
            remplaçants = [j for j in tous if j not in sur_terrain]
            
            # Trouver le joueur correspondant
            for joueur in remplaçants:
                if self.obtenir_nom_complet(joueur) == nom_prenom:
                    self.remplacer_joueur(self.joueur_selectionne, joueur)
                    self.draw_players()
                    self.draw_remplacement_panel()
                    break
    
    def on_drag(self, event):
        if not self.dragging or self.joueur_selectionne is None or event.inaxes != self.ax_terrain:
            return
        x_new, y_new = event.xdata, event.ydata
        x_new = np.clip(x_new, 0, LONGUEUR_TERRAIN)
        y_new = np.clip(y_new, 0, LARGEUR_TERRAIN)
        self.joueur_selectionne.position = [x_new, y_new]
        self.draw_players()
    
    def on_release(self, event):
        self.dragging = False


# Charger les joueurs depuis le fichier
joueurs = charger_joueurs('InfosJoueurs')

# Sélectionner 5 joueurs de chaque équipe
joueurs_equipe1 = selectionner_joueurs(joueurs, equipe1, 5)
joueurs_equipe2 = selectionner_joueurs(joueurs, equipe2, 5)

# Récupérer les joueurs restants (non placés)
tous_joueurs_equipe1 = [j for j in joueurs if j.equipe == equipe1]
tous_joueurs_equipe2 = [j for j in joueurs if j.equipe == equipe2]
joueurs_restants1 = [j for j in tous_joueurs_equipe1 if j not in joueurs_equipe1]
joueurs_restants2 = [j for j in tous_joueurs_equipe2 if j not in joueurs_equipe2]

# Placer les joueurs sur le terrain avec positions aléatoires
for joueur in joueurs_equipe1:
    joueur.position = [random.uniform(0.5, LONGUEUR_TERRAIN / 2), random.uniform(0.5, LARGEUR_TERRAIN - 0.5)]
for joueur in joueurs_equipe2:
    joueur.position = [random.uniform(LONGUEUR_TERRAIN / 2, LONGUEUR_TERRAIN - 0.5), random.uniform(0.5, LARGEUR_TERRAIN - 0.5)]


# Fonction qui trace le terrain de basket
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

fig = plt.figure(figsize=(16, 6)) #Taille de la fenêtre affichée
fig.suptitle(f"{equipe1}:{score_equipe1}  —  {equipe2}:{score_equipe2}     temps restant : {temps_restant}", fontsize=16) # affiche le nom des équipes, le score et le temps restant en haut de la fenêtre

ax_terrain = fig.add_subplot(1, 2, 1) #Pour bien ajuster le terrain
ax_remplacements = fig.add_subplot(1, 2, 2) #Panel pour les remplacements

# Créer le gestionnaire de joueurs
gestionnaire = GestionnaireJoueurs(fig, ax_terrain, ax_remplacements, joueurs_equipe1, joueurs_equipe2, joueurs_restants1, joueurs_restants2)

# Dessiner les joueurs
gestionnaire.draw_players()
gestionnaire.draw_remplacement_panel()

# Connecter les événements de souris
fig.canvas.mpl_connect('button_press_event', gestionnaire.on_click)
fig.canvas.mpl_connect('motion_notify_event', gestionnaire.on_drag)
fig.canvas.mpl_connect('button_release_event', gestionnaire.on_release)
fig.canvas.mpl_connect('pick_event', gestionnaire.on_pick_remplacant)

plt.show()