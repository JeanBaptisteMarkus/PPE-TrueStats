import cv2
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import sys
import numpy as np
sys.path.append('../')
from utils import read_stub, save_stub

class TeamAssigner:
    def __init__(self, team_1_class_name="white shirt", team_2_class_name="dark green shirt"):
        self.team_1_class_name = team_1_class_name
        self.team_2_class_name = team_2_class_name
        self.persistent_id_counter = 1000
        self.persistent_to_team = {}
        self.track_to_persistent = {}
        self.last_positions = {}
        self.team_counts = {1: 0, 2: 0}
        self.max_players = 5
        
    def load_model(self):
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
    def get_player_color(self, frame, bbox):
        x1, y1, x2, y2 = map(int, bbox)
        image = frame[y1:y2, x1:x2]
        
        if image.size == 0:
            return None
            
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        classes = [self.team_1_class_name, self.team_2_class_name]
        inputs = self.processor(text=classes, images=pil_image, return_tensors="pt", padding=True)
        outputs = self.model(**inputs)
        
        probs = outputs.logits_per_image.softmax(dim=1)
        class_idx = probs.argmax(dim=1)[0].item()
        
        # 1 = white shirt (Bucks), 2 = dark green shirt (Celtics)
        return 1 if class_idx == 0 else 2
    
    def distance(self, bbox1, bbox2):
        cx1 = (bbox1[0] + bbox1[2]) / 2
        cy1 = (bbox1[1] + bbox1[3]) / 2
        cx2 = (bbox2[0] + bbox2[2]) / 2
        cy2 = (bbox2[1] + bbox2[3]) / 2
        return np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
    
    def find_by_position(self, bbox, threshold=100):
        best_id = None
        best_dist = threshold
        
        for persistent_id, last_bbox in self.last_positions.items():
            dist = self.distance(bbox, last_bbox)
            if dist < best_dist:
                best_dist = dist
                best_id = persistent_id
        
        return best_id
    
    def assign_new_player(self, frame, bbox, frame_num):
        team = self.get_player_color(frame, bbox)
        
        if team is None:
            return None
        
        if self.team_counts[team] >= self.max_players:
            team = 2 if team == 1 else 1
            if self.team_counts[team] >= self.max_players:
                print(f"  ⚠️ Frame {frame_num}: Les deux équipes ont 5 joueurs")
                return None
        
        persistent_id = self.persistent_id_counter
        self.persistent_id_counter += 1
        
        self.persistent_to_team[persistent_id] = team
        self.team_counts[team] += 1
        self.last_positions[persistent_id] = bbox
        
        team_name = "Bucks (Blanc)" if team == 1 else "Celtics (Vert Foncé)"
        print(f"  🆕 Frame {frame_num}: Nouveau joueur -> {team_name}")
        
        return persistent_id
    
    def get_player_teams_across_frames(self, video_frames, player_tracks, read_from_stub=False, stub_path=None):
        player_assignment = read_stub(read_from_stub, stub_path)
        if player_assignment is not None and len(player_assignment) == len(video_frames):
            print("✓ Assignation chargée")
            return player_assignment
        
        self.load_model()
        
        self.persistent_id_counter = 1000
        self.persistent_to_team = {}
        self.track_to_persistent = {}
        self.last_positions = {}
        self.team_counts = {1: 0, 2: 0}
        
        print("\n🔒 ASSIGNATION PERSISTANTE DES ÉQUIPES")
        print("   🟡 Milwaukee Bucks: Maillot BLANC")
        print("   🟢 Boston Celtics: Maillot VERT FONCÉ\n")
        
        player_assignment = []
        
        for frame_num, player_track in enumerate(player_tracks):
            frame_dict = {}
            
            for track_id, track in player_track.items():
                track_id = int(track_id)
                bbox = track['bbox']
                
                if track_id in self.track_to_persistent:
                    persistent_id = self.track_to_persistent[track_id]
                    frame_dict[track_id] = self.persistent_to_team[persistent_id]
                    self.last_positions[persistent_id] = bbox
                else:
                    found_id = self.find_by_position(bbox)
                    
                    if found_id is not None:
                        self.track_to_persistent[track_id] = found_id
                        team = self.persistent_to_team[found_id]
                        frame_dict[track_id] = team
                        self.last_positions[found_id] = bbox
                        team_name = "Bucks" if team == 1 else "Celtics"
                        print(f"  🔄 Frame {frame_num}: Track {track_id} -> {team_name}")
                    else:
                        persistent_id = self.assign_new_player(video_frames[frame_num], bbox, frame_num)
                        if persistent_id is not None:
                            self.track_to_persistent[track_id] = persistent_id
                            frame_dict[track_id] = self.persistent_to_team[persistent_id]
                            self.last_positions[persistent_id] = bbox
            
            player_assignment.append(frame_dict)
        
        print(f"\n{'='*50}")
        print(f"📊 RÉSULTAT FINAL:")
        print(f"  🟡 Milwaukee Bucks (Blanc): {self.team_counts[1]} joueurs")
        print(f"  🟢 Boston Celtics (Vert Foncé): {self.team_counts[2]} joueurs")
        print(f"  Total joueurs uniques: {len(self.persistent_to_team)}")
        print(f"{'='*50}\n")
        
        save_stub(stub_path, player_assignment)
        
        return player_assignment