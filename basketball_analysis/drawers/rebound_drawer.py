import cv2
import numpy as np

class ReboundDrawer:
    """
    A class responsible for calculating and drawing rebound statistics
    on a sequence of video frames.
    """
    def __init__(self):
        pass

    def get_stats(self, rebounds):
        team1_rebounds, team2_rebounds = 0, 0

        # On compte uniquement les rebonds
        for r in rebounds:
            if r == 1: team1_rebounds += 1
            elif r == 2: team2_rebounds += 1
                
        return team1_rebounds, team2_rebounds

    def draw(self, video_frames, rebounds):
        output_video_frames = []
        # Normalisation du format de la liste rebounds au cas où elle contient des booléens
        formatted_rebounds = [r if type(r) == int else 0 for r in rebounds]

        for frame_num, frame in enumerate(video_frames):
            if frame_num == 0:
                continue
            
            frame_drawn = self.draw_frame(frame, frame_num, formatted_rebounds)
            output_video_frames.append(frame_drawn)
        return output_video_frames
    
    def draw_frame(self, frame, frame_num, rebounds):
        overlay = frame.copy()
        frame_height, frame_width = overlay.shape[:2]
        
        # --- LOGIQUE DE POSITIONNEMENT ---
        margin_x = int(frame_width * 0.04) 
        margin_y = int(frame_height * 0.04) 
        
        # Largeur réduite car le texte est plus court
        bug_width = int(frame_width * 0.35) 
        bug_height = int(frame_height * 0.16) 

        # Définition des coordonnées ancrées en BAS À DROITE
        rect_x2 = frame_width - margin_x
        rect_y2 = frame_height - margin_y
        rect_x1 = rect_x2 - bug_width
        rect_y1 = rect_y2 - bug_height

        # Dessin du rectangle de fond
        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (255, 255, 255), -1)
        alpha = 0.8
        
        # Application de la transparence
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # --- LOGIQUE DE POSITIONNEMENT DU TEXTE ---
        font_scale = 0.6
        font_thickness = 2
        
        text_x = rect_x1 + int(bug_width * 0.06) 
        
        text_y1 = rect_y1 + int(bug_height * 0.42) 
        text_y2 = rect_y1 + int(bug_height * 0.82) 
        
        # Récupération des statistiques
        t1_rebs, t2_rebs = self.get_stats(rebounds[:frame_num+1])

        # Dessin de la ligne Team 1
        cv2.putText(
            frame, 
            f"Team 1 - Rebounds: {t1_rebs}",
            (text_x, text_y1), 
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness
        )
        
        # Dessin de la ligne Team 2
        cv2.putText(
            frame, 
            f"Team 2 - Rebounds: {t2_rebs}",
            (text_x, text_y2), 
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness
        )

        return frame