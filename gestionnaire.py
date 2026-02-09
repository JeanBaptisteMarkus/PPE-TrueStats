import numpy as np
import matplotlib.pyplot as plt
from def_equipe_joueur import LONGUEUR_TERRAIN, LARGEUR_TERRAIN
from terrain import dessiner_terrain


class GestionnaireJoueurs:
    """
    Cette classe gère 
    l'affichage des joueurs sur le terrain, 
    la sélection d'un joueur, et le remplacement d'un joueur par un remplaçant disponible. 
    Elle utilise les événements de souris pour permettre à l'utilisateur de cliquer sur un joueur pour le sélectionner, 
    de faire glisser un joueur pour le déplacer sur le terrain, et de cliquer sur un remplaçant dans le panneau 
    de remplacement pour effectuer un remplacement.
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
        
    def obtenir_nom_complet(self, joueur):
        """Retourne le nom complet d'un joueur sous forme 'Prénom Nom'."""
        return f"{joueur.prenom} {joueur.nom}"
    
    def remplacer_joueur(self, joueur_a_remplacer, nouveau_joueur):
        """Remplace un joueur sur le terrain par un remplaçant."""
        # Si le joueur à remplacer est dans l'équipe 1
        if joueur_a_remplacer in self.joueurs_equipe1:
            idx = self.joueurs_equipe1.index(joueur_a_remplacer)
            self.joueurs_equipe1[idx] = nouveau_joueur
            nouveau_joueur.position = joueur_a_remplacer.position.copy()
            self.joueurs_restants1.append(joueur_a_remplacer)
            self.joueurs_restants1.remove(nouveau_joueur)
        else:
            # Si le joueur à remplacer est dans l'équipe 2
            idx = self.joueurs_equipe2.index(joueur_a_remplacer)
            self.joueurs_equipe2[idx] = nouveau_joueur
            nouveau_joueur.position = joueur_a_remplacer.position.copy()
            self.joueurs_restants2.append(joueur_a_remplacer)
            self.joueurs_restants2.remove(nouveau_joueur)
        
        self.joueur_selectionne = nouveau_joueur
    
    def draw_players(self):
        """Dessine les joueurs sur le terrain."""
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
        """Dessine le panneau de remplacements."""
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
        """Gère le clic de souris sur le terrain."""
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
        """Gère la sélection d'un remplaçant."""
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
        """Gère le glissement de souris pour déplacer un joueur."""
        if not self.dragging or self.joueur_selectionne is None or event.inaxes != self.ax_terrain:
            return
        x_new, y_new = event.xdata, event.ydata
        x_new = np.clip(x_new, 0, LONGUEUR_TERRAIN)
        y_new = np.clip(y_new, 0, LARGEUR_TERRAIN)
        self.joueur_selectionne.position = [x_new, y_new]
        self.draw_players()
    
    def on_release(self, event):
        """Gère le relâchement de la souris."""
        self.dragging = False
