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


equipes_NBA = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets",
    "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
    "Detroit Pistons", "Golden State Warriors", "Houston Rockets",
    "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers",
    "Memphis Grizzlies", "Miami Heat", "Milwaukee Bucks",
    "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
    "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers",
    "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings",
    "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"
]


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


# fonction pour choisir les équipes
def choix_equipes_console():

    print("Liste des équipes NBA disponibles :")
    for index, equipe in enumerate(equipes_NBA): # enumerate créer un index pour chaque équipe et le nom de l'équipe (equipe)
        print(f"{index + 1}. {equipe}") # Affiche la liste des équipes avec leur numéro, (index+1) car l'index commence à 0

    #Demande à l'utilisateur de taper un numéro pour la première équipe
    # int() transforme la saisie en nombre
    # On retire 1 pour obtenir l'index correct dans la liste (équipe 1  → index 0)
    choix1 = int(input("Choisissez le numéro de la première équipe : ")) - 1
    choix2 = int(input("Choisissez le numéro de la deuxième équipe : ")) - 1

    # Récupération des équipes choisies
    equipe1 = equipes_NBA[choix1]
    equipe2 = equipes_NBA[choix2]

    print(f"\n Match sélectionné : {equipe1} VS {equipe2}")

    return equipe1, equipe2 # retourne les deux équipes choisies

# Fonction pour le menu de choix des équipes (interface graphique)
def choix_equipe_tkinter():
    equipe1 = None
    equipe2 = None

    fenetre = tk.Tk()
    fenetre.title("Choix des équipes")
    fenetre.geometry("400x200")

    # Titre + menu déroulant pour la première équipe
    ttk.Label(fenetre, text="Choisissez la première équipe :").pack(pady=10) # permet d'afficher un texte
    menu_deroulant1 = ttk.Combobox(fenetre, values=equipes_NBA,state="readonly") # ttk.Combobox menu déroulant avec les équipes NBA, menu_deroulant1 est le nom du menu
    menu_deroulant1.pack() # place le menu en dessous du label

    # Titre + menu déroulant pour la deuxième équipe
    ttk.Label(fenetre, text="Choisissez la deuxième équipe :").pack(pady=10) # permet d'afficher un texte
    menu_deroulant2 = ttk.Combobox(fenetre, values=equipes_NBA,state="readonly") # ttk.Combobox menu déroulant avec les équipes NBA, menu_deroulant2 est le nom du menu
    menu_deroulant2.pack() # place le menu en dessous du label

    def valider_choix():
        nonlocal equipe1, equipe2
        equipe1 = menu_deroulant1.get() # Récupère l'équipe sélectionnée dans le menu déroulant 1
        equipe2 = menu_deroulant2.get() # Récupère l'équipe sélectionnée dans le menu déroulant 2
        fenetre.destroy()  # Ferme la fenêtre après la sélection 

    tk.Button(fenetre, text="Valider", command=valider_choix).pack(pady=20)     
    fenetre.mainloop()
    return equipe1, equipe2  


equipe1, equipe2=choix_equipe_tkinter() # Appel de la fonction pour choisir les équipes




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

fig = plt.figure(figsize=(12, 6)) #Taille de la fenêtre affichée
fig.suptitle(f"{equipe1}  —  {equipe2}", fontsize=16)
ax_terrain = fig.add_subplot(1, 2, 1) #Pour bien ajuster le terrain



dessiner_terrain(plt.gca())

plt.show()