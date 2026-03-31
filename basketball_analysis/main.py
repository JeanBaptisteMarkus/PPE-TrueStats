import os
import sys
import cv2
import numpy as np
import pickle

from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker

from drawers import (
    PlayerTracksDrawer,
    BallTracksDrawer,
    TeamBallControlDrawer,
    PassAndInterceptionDrawer,
    CourtKeypointDrawer,
    BasketDrawer
)

from team_assigner import TeamAssigner
from ball_acquisition import BallAcquisitionDetector
from pass_and_interception_detector import PassAndInterceptionDetector
from court_keypoint_detector import CourtKeypointDetector
from basket_detector.basket_detector import BasketDetector

from ReboundDetector.rebound_detector import ReboundDetector

def stabilize_keypoints(keypoints_list, alpha=0.3):
    """
    Stabilise les keypoints d'une vidéo en faisant une moyenne exponentielle sur les frames.
    alpha: coefficient de lissage (0 = très lisse, 1 = pas de lissage)
    """
    stabilized = []
    last_kp = None

    for frame_kp in keypoints_list:
        if not frame_kp:
            stabilized.append(frame_kp)
            continue

        if last_kp is None:
            last_kp = frame_kp
            stabilized.append(frame_kp)
            continue

        smooth_frame = []
        for i, kp in enumerate(frame_kp):
            if i < len(last_kp):
                smoothed_x = alpha * kp['x'] + (1-alpha) * last_kp[i]['x']
                smoothed_y = alpha * kp['y'] + (1-alpha) * last_kp[i]['y']
                smoothed_conf = kp['confidence']
                smooth_frame.append({
                    'x': smoothed_x,
                    'y': smoothed_y,
                    'confidence': smoothed_conf,
                    'name': kp['name'],
                    'estimated': kp['estimated']
                })
            else:
                smooth_frame.append(kp)
        stabilized.append(smooth_frame)
        last_kp = smooth_frame

    return stabilized

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    input_video_path = os.path.join(BASE_DIR, "input_videos", "video7.mp4")
    output_dir = os.path.join(BASE_DIR, "output_videos")
    output_video_path = os.path.join(output_dir, "output_video.avi")

    player_model_path = os.path.join(BASE_DIR, "models", "player_detector.pt")
    ball_model_path = os.path.join(BASE_DIR, "models", "ball_detector.pt")
    court_model_path = os.path.join(BASE_DIR, "models", "court_keypoint.pt")
    basket_model_path = os.path.join(BASE_DIR, "models", "panier.pt")

    # OCR pour récupérer les noms des équipes
    stubs_dir = os.path.join(BASE_DIR, "stubs")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(stubs_dir, exist_ok=True)

    print("Lecture de la vidéo...")
    video_frames = read_video(input_video_path)
    if len(video_frames) == 0:
        print("Erreur : la vidéo n'a pas été chargée.")
        return

    print("\nChargement des modèles...")
    player_tracker = PlayerTracker(model_path=player_model_path)
    ball_tracker = BallTracker(model_path=ball_model_path)
    court_keypoint_detector = CourtKeypointDetector(model_path=court_model_path)
    basket_detector = BasketDetector(model_path=basket_model_path)
    print("✓ Modèles chargés")

    print("\n🔍 ÉTAPE 1/3 - DÉTECTION DES KEYPOINTS DU TERRAIN")
    stub_path = os.path.join(stubs_dir, "court_key_points_stubs.pkl")
    if os.path.exists(stub_path):
        os.remove(stub_path)

    court_keypoints = court_keypoint_detector.get_court_keypoints(
        video_frames,
        read_from_stub=False,
        stub_path=stub_path,
        conf_threshold=0.2
    )
    #court_keypoints = stabilize_keypoints(court_keypoints, alpha=0.3)

    print("\n🏀 DÉTECTION DES PANIERS")
    basket_detections = basket_detector.detect_baskets(video_frames)
    
    print("\n👥 ÉTAPE 2/3 - DÉTECTION DES JOUEURS ET DE LA BALLE")
    player_tracks = player_tracker.get_objects_tracks(
        video_frames,
        read_from_stub=True,
        stub_path=os.path.join(stubs_dir, "player_track_stubs.pkl")
    )
    ball_tracks = ball_tracker.get_objects_tracks(
        video_frames,
        read_from_stub=True,
        stub_path=os.path.join(stubs_dir, "ball_track_stubs.pkl")
    )
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    print("\n📊 ÉTAPE 3/3 - ANALYSE DU JEU")
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(
        video_frames,
        player_tracks,
        read_from_stub=True,
        stub_path=os.path.join(stubs_dir, "player_assignment_stubs.pkl")
    )
    ball_acquisition_detector = BallAcquisitionDetector()
    ball_acquisition = ball_acquisition_detector.detect_ball_possession(
        player_tracks,
        ball_tracks
    )
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(
        ball_acquisition,
        player_assignment
    )
    interceptions = pass_and_interception_detector.detect_interceptions(
        ball_acquisition,
        player_assignment
    )

    # -------------------------
    # 🟢 NOUVEAU : DÉTECTION DES REBONDS
    # -------------------------
    rebound_detector = ReboundDetector(basket_threshold=50)

    # extraire le centre de la balle par frame
    ball_positions = []
    for frame_ball in ball_tracks:
        bbox = frame_ball.get(1, {}).get("bbox", None)
        if bbox:
            x1, y1, x2, y2 = bbox
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            ball_positions.append((cx, cy))
        else:
            ball_positions.append((None, None))

    possession_list = ball_acquisition

    # choisir le panier (centre du premier panier détecté)
    if basket_detections and basket_detections[0]:
        basket_center = basket_detections[0][0]["center"]
    else:
        basket_center = (0, 0)

    # listes pour stocker tirs, ratés, rebonds
    missed_shots = [False] * len(ball_positions)
    rebounds = [False] * len(ball_positions)
    shot_attempts = [False] * len(ball_positions)
    made_shots = [False] * len(ball_positions)

    last_missed_shot_idx = None
    for t in range(len(ball_positions)):
        if ball_positions[t][0] is None:
            continue

        # détecter les tirs et leur résultat
        shot_attempts[t] = rebound_detector.detect_shot_attempt(ball_positions, possession_list, t)
        made_shots[t] = rebound_detector.detect_made_shot(ball_positions, basket_center, t)
        missed_shots[t] = rebound_detector.detect_missed_shot(ball_positions, basket_center, t)

        # détecter un rebond uniquement après un tir raté précédent
        if last_missed_shot_idx is not None:
            if possession_list[t] != -1:  # un joueur récupère la balle
                rebounds[t] = True
                last_missed_shot_idx = None  # on a pris en compte le rebond

        # mettre à jour le dernier tir raté
        if missed_shots[t]:
            last_missed_shot_idx = t

    # sauvegarde frames de tir
    shot_dir = os.path.join(output_dir, "shot_frames")
    os.makedirs(shot_dir, exist_ok=True)
    shot_frames = [i for i, shot in enumerate(shot_attempts) if shot]
    for idx in shot_frames:
        frame = video_frames[idx]
        filename = os.path.join(shot_dir, f"shot_frame_{idx:04d}.jpg")
        cv2.imwrite(filename, frame)
    print(f"Frames de tir enregistrées dans : {shot_dir}")

    # sauvegarde frames de rebond (une seule frame par rebond)
    rebound_frames = []
    for i, reb in enumerate(rebounds):
        if reb:
            if not rebound_frames or i - rebound_frames[-1] > 2:
                rebound_frames.append(i)

    rebound_dir = os.path.join(output_dir, "rebound_frames")
    os.makedirs(rebound_dir, exist_ok=True)
    for idx in rebound_frames:
        frame = video_frames[idx]
        filename = os.path.join(rebound_dir, f"rebound_frame_{idx:04d}.jpg")
        cv2.imwrite(filename, frame)
    print(f"Frames de rebond enregistrées dans : {rebound_dir}")

    # -------------------------
    # 🎨 DESSIN DE L'OUTPUT VIDÉO
    # -------------------------
    player_tracks_drawer = PlayerTracksDrawer()
    ball_tracks_drawer = BallTracksDrawer()
    team_ball_control_drawer = TeamBallControlDrawer()
    pass_and_interception_drawer = PassAndInterceptionDrawer()
    court_keypoint_drawer = CourtKeypointDrawer()
    basket_drawer = BasketDrawer()

    output_video_frames = video_frames.copy()
    output_video_frames = court_keypoint_drawer.draw(output_video_frames, court_keypoints)
    output_video_frames = player_tracks_drawer.draw(output_video_frames, player_tracks, player_assignment, ball_acquisition)
    output_video_frames = ball_tracks_drawer.draw(output_video_frames, ball_tracks)
    output_video_frames = team_ball_control_drawer.draw(output_video_frames, player_assignment, ball_acquisition)
    output_video_frames = pass_and_interception_drawer.draw(output_video_frames, passes, interceptions)
    output_video_frames = basket_drawer.draw(output_video_frames,basket_detections)

    save_video(output_video_frames, output_video_path)

    print("\n✅ TRAITEMENT TERMINÉ AVEC SUCCÈS")
    print(f"📹 Vidéo: {output_video_path}")
    print(f"🎯 Keypoints détectés: {sum(len(kp) for kp in court_keypoints)}")
    print(f"🔄 Passes: {len(passes)}")
    print(f"🛑 Interceptions: {len(interceptions)}")
    print(f"🏀 Frames de rebond détectées : {rebound_frames}")

if __name__ == "__main__":
    main()