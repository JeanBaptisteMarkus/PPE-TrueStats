import numpy as np
import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

LONGUEUR_TERRAIN = 14.325
LARGEUR_TERRAIN = 15.24

N_JOUEURS_PAR_EQUIPE = 10
TAILLE_MIN, TAILLE_MAX = 1.80, 2.20
REBOND_MIN, REBOND_MAX = 2, 12

equipe1Nom = "DallasMavericks"
equipe2Nom = "LosAngelesLakers"

class Joueur:
    def __init__(self, nom, taille, stat_rebond, equipe):
        self.nom = nom
        self.taille = taille
        self.stat_rebond = stat_rebond
        self.equipe = equipe
        self.position = [0.0, 0.0]

def generer_joueurs(equipe_nom, n):
    joueurs = []
    for i in range(n):
        joueurs.append(Joueur(
            nom=f"Joueur{i}",
            taille=random.uniform(TAILLE_MIN, TAILLE_MAX),
            stat_rebond=random.uniform(REBOND_MIN, REBOND_MAX),
            equipe=equipe_nom
        ))
    return joueurs

def generer_situation(equipe_A, equipe_B, n_adversaires_proches=None):
    equipe_A_terrain = random.sample(equipe_A, 5)
    equipe_B_terrain = random.sample(equipe_B, 5)
    tous_joueurs = equipe_A_terrain + equipe_B_terrain
    rebondeur = random.choice(tous_joueurs)
    diff_score = random.randint(-10, 10)
    temps_restant = random.randint(0, 48*60)

    if rebondeur.equipe == equipe1Nom:
        adversaires = equipe_B_terrain
    else:
        adversaires = equipe_A_terrain

    # --- position aléatoire ---
    for j in tous_joueurs:
        j.position = [random.uniform(0, LONGUEUR_TERRAIN), random.uniform(0, LARGEUR_TERRAIN)]

    # --- distances adversaires ---
    rayon_proche = 1.0
    dists = []
    for adv in adversaires:
        dx = adv.position[0] - rebondeur.position[0]
        dy = adv.position[1] - rebondeur.position[1]
        dist = np.hypot(dx, dy)
        dists.append((adv, dist))

    if n_adversaires_proches is not None:
        if n_adversaires_proches == 0:
            top3 = []
        else:
            # trier par distance et garder n_adversaires_proches les plus proches < 1m
            top3 = sorted(dists, key=lambda x: x[1])[:n_adversaires_proches]
            # s'assurer que les distances soient <1
            for i in range(len(top3)):
                top3[i] = (top3[i][0], random.uniform(0.1, 1.0))
    else:
        top3 = [d for d in dists if d[1] <= 1.0][:3]

    panier_position = [1.6, LARGEUR_TERRAIN / 2]
    dxp = rebondeur.position[0] - panier_position[0]
    dyp = rebondeur.position[1] - panier_position[1]
    distance_joueur_panier = np.hypot(dxp, dyp)

    data = {
        "height": rebondeur.taille,
        "reb_avg": rebondeur.stat_rebond,
        "temps_restant": temps_restant,
        "diff_score": diff_score,
        "distance_joueur_panier": distance_joueur_panier
    }

    for i in range(3):
        key_taille = f"tailleAdversaire{i+1}"
        key_rebond = f"rebAdv{i+1}"
        key_dist = f"distAdv{i+1}"
        if i < len(top3):
            adv, dist = top3[i]
            data[key_taille] = adv.taille
            data[key_rebond] = adv.stat_rebond
            data[key_dist] = dist
        else:
            data[key_taille] = np.nan
            data[key_rebond] = np.nan
            data[key_dist] = np.nan

    # --- calcul rebond ---
    alpha, beta = 0.6, 0.4
    w1, w2 = 0.7, 0.3
    min_rebond, max_rebond = 0.7, 1.3
    S = 10.0
    temps_match_basket = 48*60

    danger_total = 0
    for adv, dist in top3:
        avantage_physique = alpha * max(0, adv.taille - rebondeur.taille) + beta * max(0, adv.stat_rebond - rebondeur.stat_rebond)
        danger_total += avantage_physique / (1 + dist**2)
    pression_adverse = danger_total / (1 + danger_total)

    facteur_score = max(0, 1.0 - (abs(diff_score)/S)**2)
    facteur_importance = facteur_score * (temps_match_basket - temps_restant)/temps_match_basket

    score_brut = w1*pression_adverse + w2*facteur_importance
    score_centre = score_brut - 0.5
    rebond = min_rebond + (max_rebond - min_rebond)/(1 + np.exp(-5*score_centre))
    data["rebond"] = rebond

    return data

def generer_dataset_equilibre():
    equipe_A = generer_joueurs(equipe1Nom, N_JOUEURS_PAR_EQUIPE)
    equipe_B = generer_joueurs(equipe2Nom, N_JOUEURS_PAR_EQUIPE)
    rows = []

    # 0 adversaires proches
    for _ in range(200):
        rows.append(generer_situation(equipe_A, equipe_B, n_adversaires_proches=0))
    # 1 adversaire
    for _ in range(500):
        rows.append(generer_situation(equipe_A, equipe_B, n_adversaires_proches=1))
    # 2 adversaires
    for _ in range(1000):
        rows.append(generer_situation(equipe_A, equipe_B, n_adversaires_proches=2))
    # 3 adversaires
    for _ in range(2000):
        rows.append(generer_situation(equipe_A, equipe_B, n_adversaires_proches=3))

    df = pd.DataFrame(rows)
    df.to_csv("dataset_rebond_equilibre.csv", index=False, sep=";")
    print(f"Dataset généré : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    return df

def entrainer_et_tester_modele(df):
    # --- Remplacer NaN par 0 pour adversaires manquants ---
    cols_nan = [col for col in df.columns if "Adversaire" in col or "distAdv" in col]
    df[cols_nan] = df[cols_nan].fillna(0)

    X = df.drop(columns=["rebond"])
    y = df["rebond"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)

    print("\nPERFORMANCE RANDOM FOREST")
    print(f"R² : {r2:.4f}")
    print(f"RMSE : {rmse:.4f}")

    # --- Importance des variables ---
    importances = rf.feature_importances_
    feat_importance = pd.Series(importances, index=X.columns).sort_values(ascending=False)
    print("\n Importance des variables :")
    print(feat_importance)

    ex = X_test.iloc[0]
    pred = rf.predict([ex])[0]
    print(f"\n Exemple prédiction : {pred:.4f}")
    return rf

def tester_sur_nouvelles_situations(modele, n_samples=500):
    equipe_A = generer_joueurs(equipe1Nom, N_JOUEURS_PAR_EQUIPE)
    equipe_B = generer_joueurs(equipe2Nom, N_JOUEURS_PAR_EQUIPE)
    
    rows = []
    for _ in range(n_samples):
        n_adv = random.choice([0,1,2,3])
        rows.append(generer_situation(equipe_A, equipe_B, n_adversaires_proches=n_adv))
    
    df_test = pd.DataFrame(rows)
    
    cols_nan = [col for col in df_test.columns if "Adversaire" in col or "distAdv" in col]
    df_test[cols_nan] = df_test[cols_nan].fillna(0)
    
    X_test = df_test.drop(columns=["rebond"])
    y_test = df_test["rebond"]
    
    y_pred = modele.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print("\n PERFORMANCE SUR NOUVELLES SITUATIONS")
    print(f"R² : {r2:.4f}")
    print(f"RMSE : {rmse:.4f}")
    
    print("\n Exemples prédictions :")
    for i in range(5):
        print(f"Réel : {y_test.iloc[i]:.4f}, Prédit : {y_pred[i]:.4f}")

    return y_pred


if __name__ == "__main__":
    df = generer_dataset_equilibre()
    modele = entrainer_et_tester_modele(df)
    tester_sur_nouvelles_situations(modele, n_samples=500)
