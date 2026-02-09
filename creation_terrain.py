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
import openpyxl

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
        
        # Récupérer les valeurs ou utiliser des valeurs aléatoires
        equipe1_choix = menu_deroulant1.get()
        if not equipe1_choix:
            equipe1_choix = random.choice(list(equipes_NBA.keys()))
        equipe1 = equipes_NBA[equipe1_choix]
        
        equipe2_choix = menu_deroulant2.get()
        if not equipe2_choix:
            equipe2_choix = random.choice(list(equipes_NBA.keys()))
        equipe2 = equipes_NBA[equipe2_choix]
        
        try:
            score_equipe1 = int(choix_score_equipe1.get()) if choix_score_equipe1.get() else random.randint(60, 120)
        except ValueError:
            score_equipe1 = random.randint(60, 120)
        
        try:
            score_equipe2 = int(choix_score_equipe2.get()) if choix_score_equipe2.get() else random.randint(60, 120)
        except ValueError:
            score_equipe2 = random.randint(60, 120)
        
        try:
            temps_restant = int(choix_temps_restant.get()) if choix_temps_restant.get() else random.randint(1, 2880)
        except ValueError:
            temps_restant = random.randint(1, 2880)
        
        fenetre.destroy()  # Ferme la fenêtre après la sélection

    tk.Button(fenetre, text="Valider", command=valider_choix).grid(row=3, column=0, columnspan=4, pady=20)    
    fenetre.mainloop()
    return equipe1, equipe2, score_equipe1, score_equipe2, temps_restant    

equipe1,equipe2,score_equipe1, score_equipe2, temps_restant  =choix_contexte_tkinter() # Appel de la fonction pour choisir le contexte du match


# Fonction pour extraire les données de la situations et du rebondeur et les exporter dans un fichier Excel
def extraire_donnee(gestionnaire, fig, score_equipe1, score_equipe2, temps_restant):
    """
    Cette fonction permet à l'utilisateur de sélectionner un rebondeur,
    puis d'extraire et d'exporter ses statistiques ainsi que celles de ses adversaires proches
    dans un fichier Excel.

    Paramètres de la fonction:
    - gestionnaire : Instance de la classe GestionnaireJoueurs qui gère les joueurs sur le terrain
    - fig : Figure matplotlib contenant le terrain (nécessaire pour afficher le bouton et fermer la fenêtre)
    - score_equipe1 : Score de l'équipe 1 (utilisé pour calculer la différence de score)
    - score_equipe2 : Score de l'équipe 2 (utilisé pour calculer la différence de score)
    - temps_restant : Temps restant dans le match en secondes

    Retourne:
    - rebondeur : Le joueur sélectionné par l'utilisateur (objet Joueur)
    """

    rebondeur = None  # Variable qui stockera le joueur sélectionné (initialement vide)
    RAYON_ADVERSAIRES = 2.0  # Rayon en mètres autour du rebondeur pour détecter les adversaires proches

    def valider_rebondeur(event):
        """
        Fonction callback appelée automatiquement lorsque l'utilisateur clique sur le bouton "Valider".
        Elle extrait toutes les données nécessaires et les enregistre dans un fichier Excel.

        Paramètre:
        - event : Événement du clic sur le bouton (fourni automatiquement par matplotlib)
        """
        nonlocal rebondeur  # Permet de modifier la variable rebondeur de la fonction parente

        # Vérifier qu'un joueur a bien été sélectionné sur le terrain
        if gestionnaire.joueur_selectionne is not None:
            rebondeur = gestionnaire.joueur_selectionne  # Récupérer le joueur sélectionné

            # ÉTAPE 1 : Identifier l'équipe adverse 
            # Déterminer si le rebondeur est dans l'équipe 1 ou 2, afin de savoir qui sont ses adversaires
            if rebondeur in gestionnaire.joueurs_equipe1:
                adversaires = gestionnaire.joueurs_equipe2  # Si équipe 1, alors adversaires = équipe 2
            else:
                adversaires = gestionnaire.joueurs_equipe1  # Sinon, adversaires = équipe 1

            # ÉTAPE 2 : Trouver les adversaires proches du rebondeur 
            # On cherche tous les adversaires situés dans un rayon de 2 mètres autour du rebondeur
            adversaires_proches = []  # Liste vide pour stocker les adversaires dans le rayon
            x_reb, y_reb = rebondeur.position  # Récupérer les coordonnées (x, y) du rebondeur sur le terrain

            # Parcourir chaque adversaire pour calculer sa distance par rapport au rebondeur
            for adv in adversaires:
                x_adv, y_adv = adv.position  # Récupérer les coordonnées (x, y) de l'adversaire
                # Calculer la distance euclidienne entre le rebondeur et l'adversaire
                distance = np.hypot(x_reb - x_adv, y_reb - y_adv)

                # Si la distance est inférieure ou égale au rayon, l'adversaire est "proche"
                if distance <= RAYON_ADVERSAIRES:
                    adversaires_proches.append(adv)  # Ajouter cet adversaire à la liste

            # ÉTAPE 3 : Extraire les statistiques du rebondeur
            nb_adversaires = len(adversaires_proches)  # Compter combien d'adversaires sont dans le rayon
            nom_rebondeur = f"{rebondeur.prenom} {rebondeur.nom}"  # Créer le nom complet
            taille_rebondeur = rebondeur.taille  # Taille du rebondeur en cm (provient du fichier InfosJoueurs)
            stat_rebond_rebondeur = rebondeur.stat_rebond  # Moyenne de rebonds du joueur (AverageRebond)

            # ÉTAPE 4 : Calculer les moyennes des adversaires proches 
            if nb_adversaires > 0:
                # S'il y a au moins un adversaire proche, calculer les moyennes de leurs statistiques
                # np.mean() calcule la moyenne arithmétique d'une liste de nombres
                moyenne_taille_adv = np.mean([adv.taille for adv in adversaires_proches])
                moyenne_rebond_adv = np.mean([adv.stat_rebond for adv in adversaires_proches])
            else:
                # S'il n'y a aucun adversaire proche, on met les moyennes à 0
                moyenne_taille_adv = 0
                moyenne_rebond_adv = 0

            # ÉTAPE 5 : Calculer la différence de score 
            # abs() retourne la valeur absolue (toujours positive) de la différence entre les deux scores
            diff_score = abs(score_equipe1 - score_equipe2)

            # ÉTAPE 6 : Créer un dictionnaire avec toutes les données à exporter 
            # Chaque clé sera le nom de la colonne dans Excel, chaque valeur est une liste (pour pandas)
            donnees = {
                'Nom_Rebondeur': [nom_rebondeur],  # Nom complet du joueur
                'Taille_Rebondeur': [taille_rebondeur],  # Taille en cm
                'Nb_Adversaires_Rayon': [nb_adversaires],  # Nombre d'adversaires dans 2m
                'Moyenne_Taille_Adversaires': [moyenne_taille_adv],  # Moyenne des tailles des adversaires proches
                'Stat_Rebond_Rebondeur': [stat_rebond_rebondeur],  # Moyenne rebonds du rebondeur
                'Moyenne_Rebond_Adversaires': [moyenne_rebond_adv],  # Moyenne rebonds des adversaires proches
                'Diff_Score': [diff_score],  # Différence absolue de score entre les équipes
                'Temps_Restant': [temps_restant]  # Temps restant dans le match en secondes
            }

            # ÉTAPE 7 : Créer un DataFrame pandas avec la nouvelle ligne de données
            # pd.DataFrame() transforme le dictionnaire en tableau structuré (comme une table Excel)
            df_nouvelle_ligne = pd.DataFrame(donnees)

            # ÉTAPE 8 : Enregistrer dans un fichier Excel (ajouter à la suite si le fichier existe déjà)
            # Vérifier si le fichier Excel existe déjà
            if os.path.exists('donnees_rebonds.xlsx'):
                # Si le fichier existe, le charger pour ajouter les nouvelles données à la suite
                df_existant = pd.read_excel('donnees_rebonds.xlsx')  # Lire le fichier Excel existant
                # pd.concat() combine les deux DataFrames (ancien + nouveau) en un seul
                # ignore_index=True réinitialise les numéros de lignes de manière continue
                df_final = pd.concat([df_existant, df_nouvelle_ligne], ignore_index=True)
                print(f"Nouvelle ligne ajoutée au fichier 'donnees_rebonds.xlsx'")
            else:
                # Si le fichier n'existe pas, utiliser directement la nouvelle ligne
                df_final = df_nouvelle_ligne
                print(f"Fichier 'donnees_rebonds.xlsx' créé avec les premières données")

            # to_excel() exporte le DataFrame final dans le fichier .xlsx
            # index=False permet de ne pas ajouter une colonne d'index (numéros de lignes)
            df_final.to_excel('donnees_rebonds.xlsx', index=False)

            # ÉTAPE 9 : Fermer la fenêtre du terrain 
            plt.close(fig)  # Ferme la figure matplotlib (le terrain disparaît)
        else:
            # Si aucun joueur n'a été sélectionné avant de cliquer sur "Valider"
            print("Aucun joueur sélectionné. Veuillez cliquer sur un joueur avant de valider.")

    # CRÉATION DU BOUTON "VALIDER"
    ax_bouton = plt.axes([0.4, 0.02, 0.2, 0.05])

    # Button() crée un bouton matplotlib avec le texte "Valider"
    bouton = Button(ax_bouton, 'Valider')

    # on_clicked() connecte la fonction valider_rebondeur au bouton
    # Quand l'utilisateur clique sur le bouton, valider_rebondeur() sera automatiquement appelée
    bouton.on_clicked(valider_rebondeur)

    # AFFICHAGE DE LA FENÊTRE 
    # plt.show() affiche la fenêtre matplotlib avec le terrain et le bouton
    # Cette fonction BLOQUE l'exécution du code jusqu'à ce que la fenêtre soit fermée
    # L'utilisateur peut alors interagir avec le terrain (sélectionner un joueur, cliquer sur "Valider")
    plt.show()

    # RETOUR DE LA FONCTION 
    # Une fois que la fenêtre est fermée (après le clic sur "Valider"), on retourne le joueur sélectionné
    return rebondeur


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

# Appeler la fonction pour extraire les données
rebondeur = extraire_donnee(gestionnaire, fig, score_equipe1, score_equipe2, temps_restant)