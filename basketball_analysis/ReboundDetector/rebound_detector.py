import numpy as np

class ReboundDetector:
    def __init__(self, basket_threshold=50):
        """
        basket_threshold : distance en pixels pour considérer la balle proche du panier
        """
        self.basket_threshold = basket_threshold

    def detect_shot_attempt(self, ball_positions, possession_list, frame_idx):
        if frame_idx == 0:
            return False

        prev_poss = possession_list[frame_idx - 1]
        curr_poss = possession_list[frame_idx]

        # Tir si joueur avait la balle et la perd + balle monte
        if prev_poss != -1 and curr_poss == -1:
            if ball_positions[frame_idx][1] < ball_positions[frame_idx - 1][1]:
                return True
        return False

    def detect_made_shot(self, ball_positions, basket_center, frame_idx):
        ball_x, ball_y = ball_positions[frame_idx]
        basket_x, basket_y = basket_center
        distance = np.sqrt((ball_x - basket_x) ** 2 + (ball_y - basket_y) ** 2)

        # Balle rentrée si proche du panier et sous le cercle
        return distance < self.basket_threshold and ball_y > basket_y

    def detect_missed_shot(self, ball_positions, basket_center, frame_idx):
        if frame_idx < 2:
            return False

        y_prev2 = ball_positions[frame_idx - 2][1]
        y_prev1 = ball_positions[frame_idx - 1][1]
        y_curr = ball_positions[frame_idx][1]

        ball_x, ball_y = ball_positions[frame_idx]
        basket_x, basket_y = basket_center
        distance = np.sqrt((ball_x - basket_x) ** 2 + (ball_y - basket_y) ** 2)

        extended_threshold = self.basket_threshold * 3

        # Tir raté si sommet atteint ou trop loin du panier
        if (y_prev1 - y_prev2) * (y_curr - y_prev1) < 0 or distance > extended_threshold:
            return True

        return False

    def detect_rebound(self, missed_shot_list, ball_positions, possession_list, frame_idx):
        """
        Détecte le rebond :
        - Un tir raté est détecté avant
        - La balle descend après le tir
        - Un joueur récupère la balle
        """
        if frame_idx < 2:
            return False

        # on ne regarde que si la balle est possédée
        if possession_list[frame_idx] == -1:
            return False

        # chercher le dernier tir raté avant cette frame
        for lookback in range(frame_idx - 1, -1, -1):
            if missed_shot_list[lookback]:
                # vérifier que la balle descend depuis le tir raté
                if ball_positions[frame_idx][1] > ball_positions[lookback][1]:
                    return True
                else:
                    return False  # pas encore descendu → pas de rebond
        return False
import numpy as np

class ReboundDetector:
    def __init__(self, basket_threshold=50):
        """
        basket_threshold : distance en pixels pour considérer la balle proche du panier
        """
        self.basket_threshold = basket_threshold

    def detect_shot_attempt(self, ball_positions, possession_list, frame_idx):
        if frame_idx == 0:
            return False

        prev_poss = possession_list[frame_idx - 1]
        curr_poss = possession_list[frame_idx]

        # Tir si joueur avait la balle et la perd + balle monte
        if prev_poss != -1 and curr_poss == -1:
            if ball_positions[frame_idx][1] < ball_positions[frame_idx - 1][1]:
                return True
        return False

    def detect_made_shot(self, ball_positions, basket_center, frame_idx):
        ball_x, ball_y = ball_positions[frame_idx]
        basket_x, basket_y = basket_center
        distance = np.sqrt((ball_x - basket_x) ** 2 + (ball_y - basket_y) ** 2)

        # Balle rentrée si proche du panier et sous le cercle
        return distance < self.basket_threshold and ball_y > basket_y

    def detect_missed_shot(self, ball_positions, basket_center, frame_idx):
        if frame_idx < 2:
            return False

        y_prev2 = ball_positions[frame_idx - 2][1]
        y_prev1 = ball_positions[frame_idx - 1][1]
        y_curr = ball_positions[frame_idx][1]

        ball_x, ball_y = ball_positions[frame_idx]
        basket_x, basket_y = basket_center
        distance = np.sqrt((ball_x - basket_x) ** 2 + (ball_y - basket_y) ** 2)

        extended_threshold = self.basket_threshold * 3

        # Tir raté si sommet atteint ou trop loin du panier
        if (y_prev1 - y_prev2) * (y_curr - y_prev1) < 0 or distance > extended_threshold:
            return True

        return False

    def detect_rebound(self, missed_shot_list, ball_positions, possession_list, frame_idx):
        """
        Détecte le rebond :
        - Un tir raté est détecté avant
        - La balle descend après le tir
        - Un joueur récupère la balle (instant précis de l'acquisition)
        """
        if frame_idx < 2:
            return False

        # 1. On s'assure qu'on est à la frame EXACTE de la récupération :
        # Le joueur a la balle maintenant, mais personne ne l'avait à la frame juste avant.
        if possession_list[frame_idx] == -1 or possession_list[frame_idx - 1] != -1:
            return False

        # 2. Chercher le dernier tir raté avant cette frame
        for lookback in range(frame_idx - 1, -1, -1):
            
            # Si quelqu'un d'autre a eu la balle entre temps, ce n'est plus un rebond lié à ce tir.
            if lookback < frame_idx - 1 and possession_list[lookback] != -1:
                return False

            if missed_shot_list[lookback]:
                # vérifier que la balle descend depuis le tir raté
                if ball_positions[frame_idx][1] > ball_positions[lookback][1]:
                    return True
                else:
                    return False  # pas encore descendu → pas de rebond
                    
        return False