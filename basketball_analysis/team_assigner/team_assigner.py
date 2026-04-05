
from ultralytics import YOLO

import sys
sys.path.append('../')
from utils import read_stub, save_stub

class TeamAssigner:

    def __init__(self, model_path):
        self.model = YOLO(model_path)
        
    def get_player_teams_across_frames(self, video_frames, player_tracks, read_from_stub=False, stub_path=None):
        # Lire stub
        player_assignment = read_stub(read_from_stub, stub_path)
        if player_assignment is not None:
            return player_assignment
        
        print("\n🔒 ASSIGNATION AVEC MODÈLE YOLO")
        
        player_assignment = []
        
        # Faire la détection sur TOUTE la frame, pas sur la ROI
        for frame_num, frame in enumerate(video_frames):
            frame_dict = {}
            
            # Détection sur la frame entière
            results = self.model(frame, verbose=False)
            
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                
                # Pour chaque détection
                for box in boxes:
                    # Récupérer les coordonnées
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    class_id = int(box.cls[0])
                    
                    # 0 = Celtics, 1 = Bucks
                    if class_id == 0:
                        team = 2  # Celtics
                    else:
                        team = 1  # Bucks
                    
                    # Associer chaque maillot détecté à un track_id
                    # On cherche quel joueur (par position) correspond à ce maillot
                    best_track_id = None
                    best_dist = 100
                    
                    for track_id, track in player_tracks[frame_num].items():
                        tx1, ty1, tx2, ty2 = map(int, track['bbox'])
                        # Centre du joueur
                        cx_track = (tx1 + tx2) // 2
                        cy_track = (ty1 + ty2) // 2
                        # Centre du maillot détecté
                        cx_det = (x1 + x2) // 2
                        cy_det = (y1 + y2) // 2
                        
                        dist = ((cx_track - cx_det)**2 + (cy_track - cy_det)**2)**0.5
                        
                        if dist < best_dist:
                            best_dist = dist
                            best_track_id = track_id
                    
                    if best_track_id is not None and best_dist < 50:
                        frame_dict[best_track_id] = team
            
            player_assignment.append(frame_dict)
        
        save_stub(stub_path, player_assignment)

        return player_assignment