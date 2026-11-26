"""Attribution des équipes par la couleur des maillots, valable pour n'importe quel match.

Les joueurs de la vidéo sont répartis en deux groupes de couleurs de maillot
proches. Le regroupement est refait pour chaque vidéo : une couleur n'est
jamais associée durablement à une équipe (deux équipes différentes en rouge
dans deux matchs ne posent pas de problème).

Étapes :
1. pour chaque joueur suivi, couleur médiane du centre du torse (espace Lab),
   mesurée sur au plus OBSERVATIONS_PAR_JOUEUR images réparties sur sa présence ;
2. k-means à 2 groupes sur ces couleurs, pondéré par le temps de présence
   (un suivi parasite de quelques images pèse peu) ;
3. l'équipe 1 est celle au maillot le plus clair, l'équipe 2 la plus foncée.

Limites :
- si les deux équipes ont des maillots de couleurs proches, la séparation
  n'est pas fiable (un avertissement est affiché) ;
- les arbitres sont exclus par le détecteur de joueurs (classe « Player »). Un
  arbitre qui passerait quand même serait rattaché à l'équipe de couleur la
  plus proche.
"""
import cv2
import numpy as np

from ..utils.stub_utils import read_stub, save_stub

# Zone du maillot dans le cadre du joueur : (haut, bas, gauche, droite) en fraction
# de la hauteur / largeur. Le centre du torse évite la tête, les bras, le short et le fond.
ZONE_TORSE = (0.20, 0.45, 0.30, 0.70)
OBSERVATIONS_PAR_JOUEUR = 20
PIXELS_MIN = 30
# Écart minimal (Lab, échelle OpenCV 0-255) entre les deux couleurs d'équipe
# en dessous duquel l'attribution est jugée peu fiable.
ECART_MIN_COULEURS = 25.0


def kmeans_pondere(points, k, poids=None, iterations=30, essais=5, graine=0):
    """k-means pondéré (initialisation k-means++), meilleur de `essais` lancers.

    Retourne (labels, centres). Déterministe pour une graine donnée.
    """
    points = np.asarray(points, dtype=float)
    poids = np.ones(len(points)) if poids is None else np.asarray(poids, dtype=float)
    k = min(k, len(points))
    rng = np.random.default_rng(graine)
    meilleur = None
    for _ in range(essais):
        centres = [points[rng.choice(len(points), p=poids / poids.sum())]]
        for _ in range(1, k):
            d2 = np.min(((points[:, None] - np.array(centres)[None]) ** 2).sum(-1), axis=1) * poids
            if d2.sum() > 0:
                centres.append(points[rng.choice(len(points), p=d2 / d2.sum())])
            else:
                centres.append(points[rng.integers(len(points))])
        centres = np.array(centres, dtype=float)
        for _ in range(iterations):
            labels = np.argmin(((points[:, None] - centres[None]) ** 2).sum(-1), axis=1)
            for j in range(k):
                membres = labels == j
                if membres.any():
                    centres[j] = np.average(points[membres], axis=0, weights=poids[membres])
        inertie = (poids * ((points - centres[labels]) ** 2).sum(-1)).sum()
        if meilleur is None or inertie < meilleur[0]:
            meilleur = (inertie, labels, centres)
    return meilleur[1], meilleur[2]


def couleur_maillot(frame, bbox, zone=ZONE_TORSE):
    """Couleur médiane (Lab) du centre du torse d'un joueur, ou None si la zone est trop petite."""
    x1, y1, x2, y2 = bbox
    largeur, hauteur = x2 - x1, y2 - y1
    h_img, l_img = frame.shape[:2]
    haut, bas, gauche, droite = zone
    ya, yb = int(max(0, y1 + haut * hauteur)), int(min(h_img, y1 + bas * hauteur))
    xa, xb = int(max(0, x1 + gauche * largeur)), int(min(l_img, x1 + droite * largeur))
    if yb <= ya or xb <= xa or (yb - ya) * (xb - xa) < PIXELS_MIN:
        return None
    lab = cv2.cvtColor(frame[ya:yb, xa:xb], cv2.COLOR_BGR2LAB)
    return np.median(lab.reshape(-1, 3).astype(float), axis=0)


def lab_vers_bgr(lab):
    """Couleur Lab (échelle OpenCV) -> tuple BGR d'entiers, pour le dessin."""
    pixel = np.clip(np.round(lab), 0, 255).astype(np.uint8).reshape(1, 1, 3)
    return tuple(int(v) for v in cv2.cvtColor(pixel, cv2.COLOR_LAB2BGR)[0, 0])


class EquipesParCouleur:
    """Même interface que TeamAssigner : get_player_teams_across_frames / get_player_identity_map."""

    def __init__(self, observations_par_joueur=OBSERVATIONS_PAR_JOUEUR):
        self.observations_par_joueur = observations_par_joueur
        self.couleurs_equipes = {}   # id d'équipe (1, 2) -> couleur BGR du maillot
        self.ecart_couleurs = None   # distance Lab entre les deux couleurs d'équipe

    def couleurs_par_joueur(self, video_frames, player_tracks):
        """{track_id: (couleur Lab médiane, nombre d'images de présence)}."""
        apparitions = {}
        for numero, frame_tracks in enumerate(player_tracks):
            for track_id in frame_tracks:
                apparitions.setdefault(int(track_id), []).append(numero)

        resultat = {}
        for track_id, numeros in apparitions.items():
            choisis = np.linspace(0, len(numeros) - 1, min(self.observations_par_joueur, len(numeros)))
            couleurs = []
            for i in np.unique(choisis.astype(int)):
                numero = numeros[i]
                info = player_tracks[numero].get(track_id, player_tracks[numero].get(np.int64(track_id)))
                couleur = couleur_maillot(video_frames[numero], info["bbox"])
                if couleur is not None:
                    couleurs.append(couleur)
            if couleurs:
                resultat[track_id] = (np.median(couleurs, axis=0), len(numeros))
        return resultat

    def equipe_par_joueur(self, couleurs):
        """{track_id: 1 ou 2} à partir des couleurs ; met à jour couleurs_equipes."""
        if not couleurs:
            return {}
        ids = sorted(couleurs)
        points = np.array([couleurs[t][0] for t in ids])
        poids = np.array([couleurs[t][1] for t in ids], dtype=float)
        if len(ids) == 1:
            self.couleurs_equipes = {1: lab_vers_bgr(points[0])}
            return {ids[0]: 1}

        labels, centres = kmeans_pondere(points, 2, poids)
        # Équipe 1 = maillot le plus clair (canal L)
        clair = int(np.argmax(centres[:, 0]))
        numero_equipe = {clair: 1, 1 - clair: 2}
        self.couleurs_equipes = {numero_equipe[j]: lab_vers_bgr(centres[j]) for j in range(2)}
        self.ecart_couleurs = float(np.linalg.norm(centres[0] - centres[1]))
        return {t: numero_equipe[int(l)] for t, l in zip(ids, labels)}

    def get_player_teams_across_frames(self, video_frames, player_tracks, read_from_stub=False, stub_path=None):
        cache = read_stub(read_from_stub, stub_path)
        if isinstance(cache, dict) and len(cache.get("assignation", [])) == len(video_frames):
            self.couleurs_equipes = cache["couleurs_equipes"]
            self.ecart_couleurs = cache["ecart_couleurs"]
            return cache["assignation"]

        equipes = self.equipe_par_joueur(self.couleurs_par_joueur(video_frames, player_tracks))
        assignation = [{int(t): equipes[int(t)] for t in frame_tracks if int(t) in equipes}
                       for frame_tracks in player_tracks]
        save_stub(stub_path, {"assignation": assignation, "couleurs_equipes": self.couleurs_equipes,
                              "ecart_couleurs": self.ecart_couleurs})
        return assignation

    def attribution_fiable(self):
        """False si les deux couleurs d'équipe sont trop proches pour être séparées sûrement."""
        return self.ecart_couleurs is None or self.ecart_couleurs >= ECART_MIN_COULEURS

    def get_player_identity_map(self):
        # La couleur ne donne pas l'identité des joueurs (il faudrait lire les numéros).
        return {}
