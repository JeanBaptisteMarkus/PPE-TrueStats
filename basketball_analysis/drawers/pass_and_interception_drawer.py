import cv2
import numpy as np

class PassAndInterceptionDrawer:
    def __init__(self):
        pass

    def get_stats(self, passes, interceptions, rebounds):
        team1_passes, team2_passes = 0, 0
        team1_interceptions, team2_interceptions = 0, 0
        team1_rebounds, team2_rebounds = 0, 0

        # On compte les passes et interceptions
        for p, i in zip(passes, interceptions):
            if p == 1: team1_passes += 1
            elif p == 2: team2_passes += 1
            if i == 1: team1_interceptions += 1
            elif i == 2: team2_interceptions += 1
            
        # On compte les rebonds
        for r in rebounds:
            if r == 1: team1_rebounds += 1
            elif r == 2: team2_rebounds += 1
                
        return (team1_passes, team2_passes, 
                team1_interceptions, team2_interceptions, 
                team1_rebounds, team2_rebounds)

    def draw(self, video_frames, passes, interceptions, rebounds):
        output_video_frames = []
        # Normalisation du format de la liste rebounds au cas où elle contient des booléens
        formatted_rebounds = [r if type(r) == int else 0 for r in rebounds]

        for frame_num, frame in enumerate(video_frames):
            if frame_num == 0:
                continue
            
            frame_drawn = self.draw_frame(frame, frame_num, passes, interceptions, formatted_rebounds)
            output_video_frames.append(frame_drawn)
        return output_video_frames
    
    def draw_frame(self, frame, frame_num, passes, interceptions, rebounds):
        overlay = frame.copy()
        frame_height, frame_width = overlay.shape[:2]
        
        # --- NOUVELLE LOGIQUE DE POSITIONNEMENT ---
        # On définit des marges proportionnelles à la largeur de l'image (ex: 5%)
        # et une taille de bandeau (bug) proportionnelle
        margin_x = int(frame_width * 0.04) # 4% de marge latérale
        margin_y = int(frame_height * 0.04) # 4% de marge inférieure
        
        # J'ai réduit la largeur pour le rendre plus compact (45% de la frame)
        bug_width = int(frame_width * 0.45) 
        # J'ai un peu augmenté la hauteur pour bien aérer (16% de la frame)
        bug_height = int(frame_height * 0.16) 

        # Définition des coordonnées ancrées en BAS À DROITE
        rect_x2 = frame_width - margin_x
        rect_y2 = frame_height - margin_y
        rect_x1 = rect_x2 - bug_width
        rect_y1 = rect_y2 - bug_height

        # Dessin du rectangle de fond (en gardant ta couleur blanche semi-transparente)
        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (255, 255, 255), -1)
        alpha = 0.8
        # User's logic has addWeighted, let's keep it clean
        # but apply it only to the region of interest to be cleaner
        roi = frame[rect_y1:rect_y2, rect_x1:rect_x2]
        overlay_roi = overlay[rect_y1:rect_y2, rect_x1:rect_x2]
        # On blend tout le cadre comme avant, c'est simple
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # --- NOUVELLE LOGIQUE DE POSITIONNEMENT DU TEXTE ---
        font_scale = 0.6
        font_thickness = 2
        
        # Alignement à gauche à l'intérieur du bandeau, avec un léger indent
        text_x = rect_x1 + int(bug_width * 0.06) 
        
        # Centrage vertical avec un spacing précis pour les deux lignes
        # text_y1 (ligne Team 1) et text_y2 (ligne Team 2) sont calculées par rapport au rect_y1
        # pour s'assurer que les deux lignes rentrent
        line_height = int(bug_height * 0.35) # Hauteur de ligne
        text_y1 = rect_y1 + int(bug_height * 0.42) # Position verticale de la ligne 1
        text_y2 = rect_y1 + int(bug_height * 0.82) # Position verticale de la ligne 2
        
        # Récupération des statistiques (logique existante)
        (t1_passes, t2_passes, t1_interc, t2_interc, t1_rebs, t2_rebs) = self.get_stats(
            passes[:frame_num+1], interceptions[:frame_num+1], rebounds[:frame_num+1]
        )

        # Dessin de la ligne Team 1
        cv2.putText(
            frame, 
            f"Team 1 - Passes: {t1_passes} | Interc: {t1_interc} | Rebounds: {t1_rebs}",
            (text_x, text_y1), 
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness
        )
        
        # Dessin de la ligne Team 2
        cv2.putText(
            frame, 
            f"Team 2 - Passes: {t2_passes} | Interc: {t2_interc} | Rebounds: {t2_rebs}",
            (text_x, text_y2), 
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness
        )

        return frame