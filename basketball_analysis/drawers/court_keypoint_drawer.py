import supervision as sv
import cv2

class CourtKeypointDrawer:
    """
    Drawer for court keypoints - VERSION SIMPLIFIÉE POUR VOIR LES POINTS
    """
    def draw(self, frames, court_keypoints):
        """
        Dessine les keypoints du terrain sur les frames.
        """
        output_frames = frames.copy()
        
        for i, frame in enumerate(output_frames):
            if i < len(court_keypoints):
                keypoints = court_keypoints[i]
                
                # Dessiner chaque keypoint
                for kp in keypoints:
                    if isinstance(kp, dict):
                        x = int(kp.get('x', 0))
                        y = int(kp.get('y', 0))
                        conf = kp.get('confidence', 0)
                        name = kp.get('name', 'kp')
                        
                        # VERT pour les points détectés
                        color = (0, 255, 0)
                        radius = 8
                        
                        # Dessiner un cercle bien visible
                        cv2.circle(frame, (x, y), radius, color, -1)
                        cv2.circle(frame, (x, y), radius + 2, (255, 255, 255), 2)
                        
                        # Ajouter la confiance
                        cv2.putText(frame, f"{conf:.2f}", 
                                  (x + 15, y - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        # Si c'est un objet avec attributs
                        if hasattr(kp, 'x') and hasattr(kp, 'y'):
                            x = int(kp.x)
                            y = int(kp.y)
                            cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)
        
        return output_frames