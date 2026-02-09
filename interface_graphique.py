import tkinter as tk
from tkinter import ttk
import random
from def_equipe_joueur import equipes_NBA


def choix_contexte_tkinter():
    """Fonction pour le menu de choix du contexte du match (interface graphique)"""

    equipe1 = None
    equipe2 = None
    score_equipe1 = None
    score_equipe2 = None
    temps_restant = None

    fenetre = tk.Tk()
    fenetre.title("Choix du contexte du match")
    fenetre.geometry("500x500")

    # ***choix de la première équipe***
    ttk.Label(fenetre, text="Équipe 1 :").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    menu_deroulant1 = ttk.Combobox(fenetre, values=list(equipes_NBA.keys()), state="readonly")
    menu_deroulant1.grid(row=0, column=1, padx=10)
    # ***entrée pour le score de la première équipe***
    ttk.Label(fenetre, text="Score équipe 1 :").grid(row=0, column=2, padx=10, sticky="w")
    choix_score_equipe1 = tk.Entry(fenetre, width=5)
    choix_score_equipe1.grid(row=0, column=3)

    # ***choix de la deuxième équipe***
    ttk.Label(fenetre, text="Équipe 2 :").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    menu_deroulant2 = ttk.Combobox(fenetre, values=list(equipes_NBA.keys()), state="readonly")
    menu_deroulant2.grid(row=1, column=1, padx=10)
    # ***entrée pour le score de la deuxième équipe***
    ttk.Label(fenetre, text="Score équipe 2 :").grid(row=1, column=2, padx=10)
    choix_score_equipe2 = tk.Entry(fenetre, width=5)
    choix_score_equipe2.grid(row=1, column=3)

    # ***Choix du temps restant***
    ttk.Label(fenetre, text="Temps restant (en secondes) :").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    choix_temps_restant = tk.Entry(fenetre, width=5)
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
