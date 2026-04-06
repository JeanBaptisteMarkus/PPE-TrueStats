
from ultralytics import YOLO
import sys
import random
from collections import defaultdict
sys.path.append('../')
from utils import read_stub, save_stub

class TeamAssigner:
    def __init__(self, team_model_path, player_model_path, players_info_path):
        self.team_model = YOLO(team_model_path)
        self.player_model = YOLO(player_model_path)
        self.player_info = self.load_players_info(players_info_path)
        
        self.class_to_player = {
            0: "Baylor Scheierman", 1: "Nikola Vucevic", 2: "Hugo Gonzalez",
            3: "Myles Turner", 4: "Ousmane Dieng", 5: "Giannis Antetokounmpo",
            6: "Sam Hauser", 7: "Cameron Thomas", 8: "Derrick White",
            9: "Kevin Porter Jr", 10: "Payton Pritchard", 11: "Bobby Portis",
            12: "Gary Harris", 13: "Jericho Sims", 14: "Ron Harper Jr",
            15: "Andre Jackson Jr", 16: "Luka Garza", 17: "Pete Nance"
        }
        
        self.bucks_players = [n for n, i in self.player_info.items() if i == "Milwaukee"]
        self.celtics_players = [n for n, i in self.player_info.items() if i == "Celtics"]
        self.player_identity_map = {}
        self.max_players = 5
        self.used_names = set()  # ← AJOUTÉ : pour suivre les noms déjà assignés
        
    def load_players_info(self, path):
        info = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f.readlines()[1:]:
                if line.strip():
                    parts = line.split(',')
                    info[parts[0].strip()] = parts[2].strip()
        return info
    
    def get_player_teams_across_frames(self, video_frames, player_tracks, read_from_stub=False, stub_path=None):
        player_assignment = read_stub(read_from_stub, stub_path)
        if player_assignment is not None:
            return player_assignment
        
        print("\n🔒 ASSIGNATION DES ÉQUIPES PAR MOYENNE DE CONFIANCE")
        
        # 1. Récupérer tous les track_ids
        all_tracks = set()
        for ft in player_tracks:
            for tid in ft.keys():
                all_tracks.add(int(tid))
        
        # 2. Collecter les votes pour chaque track (avec confiance)
        track_votes = defaultdict(lambda: defaultdict(float))
        track_counts = defaultdict(lambda: defaultdict(int))
        
        for fn, frame in enumerate(video_frames):
            results = self.team_model(frame, verbose=False)
            if results[0].boxes:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    team = 2 if int(box.cls[0]) == 0 else 1
                    confidence = float(box.conf[0])
                    
                    best_tid, best_dist = None, 100
                    for tid, track in player_tracks[fn].items():
                        tid = int(tid)
                        tx1, ty1, tx2, ty2 = map(int, track['bbox'])
                        cx_t = (tx1+tx2)//2
                        cy_t = (ty1+ty2)//2
                        cx_b = (x1+x2)//2
                        cy_b = (y1+y2)//2
                        dist = ((cx_t-cx_b)**2 + (cy_t-cy_b)**2)**0.5
                        if dist < best_dist:
                            best_dist, best_tid = dist, tid
                    
                    if best_tid and best_dist < 50:
                        track_votes[best_tid][team] += confidence
                        track_counts[best_tid][team] += 1
        
        # 3. Calculer la meilleure moyenne pour chaque track
        track_team = {}
        track_team_confidence = {}
        
        print("\n🏆 Détection des équipes par moyenne de confiance:")
        for tid, teams in track_votes.items():
            best_team = None
            best_avg = 0
            for team, total_conf in teams.items():
                count = track_counts[tid][team]
                avg_conf = total_conf / count if count > 0 else 0
                if avg_conf > best_avg:
                    best_avg = avg_conf
                    best_team = team
            
            if best_team:
                track_team[tid] = best_team
                track_team_confidence[tid] = best_avg
                team_name = "Bucks" if best_team == 1 else "Celtics"
                print(f"  Track {tid} -> {team_name} (moyenne: {best_avg:.3f}, {track_counts[tid][best_team]} détections)")
        
        # 4. Assigner les noms des joueurs avec SYSTÈME DE TOURNOI
        used_bucks, used_celtics = set(), set()
        self.player_identity_map = {}
        self.used_names = set()  # ← pour éviter les doublons
        
        # 4a. Collecter toutes les détections de joueurs avec leur confiance
        player_detections = []  # (confiance, track_id, name, team)
        
        for fn, frame in enumerate(video_frames):
            results = self.team_model(frame, verbose=False)
            if results[0].boxes:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    team = 2 if int(box.cls[0]) == 0 else 1
                    
                    best_tid, best_dist = None, 100
                    for tid, track in player_tracks[fn].items():
                        tid = int(tid)
                        tx1, ty1, tx2, ty2 = map(int, track['bbox'])
                        cx_t = (tx1+tx2)//2
                        cy_t = (ty1+ty2)//2
                        cx_b = (x1+x2)//2
                        cy_b = (y1+y2)//2
                        dist = ((cx_t-cx_b)**2 + (cy_t-cy_b)**2)**0.5
                        if dist < best_dist:
                            best_dist, best_tid = dist, tid
                    
                    if best_tid and best_tid not in self.player_identity_map and best_dist < 70:
                        roi = frame[y1:y2, x1:x2]
                        if roi.size > 0:
                            r = self.player_model(roi, verbose=False)
                            if r[0].boxes:
                                cid = int(r[0].boxes.cls[0])
                                confidence = float(r[0].boxes.conf[0])
                                name = self.class_to_player.get(cid, "")
                                if name and name in self.player_info:
                                    real_team = self.player_info[name]
                                    if (real_team == "Milwaukee" and team == 1) or (real_team == "Celtics" and team == 2):
                                        player_detections.append((confidence, best_tid, name, team))
        
        # Trier par confiance décroissante (meilleur d'abord)
        player_detections.sort(reverse=True, key=lambda x: x[0])
        
        # Assigner les meilleures détections (un nom par joueur)
        for confidence, tid, name, team in player_detections:
            if name in self.used_names:
                continue  # ← CE NOM EST DÉJÀ PRIS
            
            if team == 1 and len(used_bucks) >= self.max_players:
                continue
            if team == 2 and len(used_celtics) >= self.max_players:
                continue
            
            self.player_identity_map[tid] = {"name": name, "team": team}
            self.used_names.add(name)
            
            if team == 1:
                used_bucks.add(name)
                print(f"  ✅ Track {tid} -> {name} (Bucks) [conf: {confidence:.3f}] [{len(used_bucks)}/{self.max_players}]")
            else:
                used_celtics.add(name)
                print(f"  ✅ Track {tid} -> {name} (Celtics) [conf: {confidence:.3f}] [{len(used_celtics)}/{self.max_players}]")
        
        # 4b. Assignation aléatoire pour les tracks restants (noms non encore utilisés)
        bucks_left = [p for p in self.bucks_players if p not in self.used_names]
        celtics_left = [p for p in self.celtics_players if p not in self.used_names]
        
        print("\n🎲 Assignation des joueurs restants:")
        for tid in all_tracks:
            if tid not in self.player_identity_map and tid in track_team:
                team = track_team[tid]
                
                # Vérifier si l'équipe a déjà 5 joueurs
                if team == 1 and len(used_bucks) >= self.max_players:
                    continue
                if team == 2 and len(used_celtics) >= self.max_players:
                    continue
                
                if team == 1 and bucks_left:
                    name = bucks_left.pop(0)
                    self.player_identity_map[tid] = {"name": name, "team": 1}
                    self.used_names.add(name)
                    used_bucks.add(name)
                    print(f"  🎲 Track {tid} -> {name} (Bucks) [{len(used_bucks)}/{self.max_players}]")
                elif team == 2 and celtics_left:
                    name = celtics_left.pop(0)
                    self.player_identity_map[tid] = {"name": name, "team": 2}
                    self.used_names.add(name)
                    used_celtics.add(name)
                    print(f"  🎲 Track {tid} -> {name} (Celtics) [{len(used_celtics)}/{self.max_players}]")
        
        # 5. Construire le résultat
        result = []
        for fn, frame in enumerate(video_frames):
            fd = {}
            for tid, track in player_tracks[fn].items():
                tid = int(tid)
                if tid in self.player_identity_map:
                    fd[tid] = self.player_identity_map[tid]["team"]
                elif tid in track_team:
                    fd[tid] = track_team[tid]
            result.append(fd)
        
        # Résumé final
        print(f"\n{'='*50}")
        print(f"📊 RÉSULTAT FINAL ({self.max_players} max par équipe):")
        print(f"  🟡 Milwaukee Bucks: {len(used_bucks)}/{self.max_players}")
        for name in used_bucks:
            print(f"      - {name}")
        print(f"  🟢 Boston Celtics: {len(used_celtics)}/{self.max_players}")
        for name in used_celtics:
            print(f"      - {name}")
        print(f"{'='*50}\n")
        
        save_stub(stub_path, result)
        return result
    
    def get_player_identity_map(self):
        return self.player_identity_map