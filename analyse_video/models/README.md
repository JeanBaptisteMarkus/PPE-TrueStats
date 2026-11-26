# Modèles YOLO

Les poids (`*.pt`) ne sont pas versionnés (ils sont trop lourds pour git). Placez-les ici :

| Fichier | Rôle | Utilisé par |
|---|---|---|
| `player_detector.pt` | Détection des joueurs (classe `Player`) | `detection/player_tracker.py` |
| `ball_detector.pt` | Détection du ballon (classe `Ball`) | `detection/ball_tracker.py` |
| `court_keypoint.pt` | Repères du terrain (coins, raquette) | `detection/court_keypoint_detector.py` |
| `panier.pt` | Détection du panier | `detection/basket_detector.py` |
| `team.pt` | Classification de l'équipe (Celtics / Bucks) | `detection/team_assigner.py` |
| `JoueurEquipe.pt` | Identification des 18 joueurs (maillots) | `detection/team_assigner.py` |

Les scripts et notebooks pour (ré)entraîner ces modèles sont dans [`entrainement/`](../../entrainement/).
