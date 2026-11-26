"""Pipeline d'analyse vidéo : `python -m analyse_video [video.mp4] [--sans-cache]`.

Étapes :
1. détection des repères du terrain et des paniers ;
2. suivi des joueurs et du ballon ;
3. attribution des équipes / identités, possession, passes, interceptions ;
4. détection des tirs ratés puis des rebonds ;
5. export des frames de tir / rebond et de la vidéo annotée.
"""
import argparse
import os

import cv2

from . import config
from .affichage import (
    BallTracksDrawer,
    BasketDrawer,
    CourtKeypointDrawer,
    PlayerTracksDrawer,
    ReboundDrawer,
    TeamBallControlDrawer,
)
from .detection import BallTracker, BasketDetector, CourtKeypointDetector, PlayerTracker, TeamAssigner
from .evenements import BallAcquisitionDetector, PassAndInterceptionDetector, ReboundDetector
from .utils.video_utils import read_video, save_video


def stabilize_keypoints(keypoints_list, alpha=0.3):
    """Lisse les repères du terrain d'une frame à l'autre (moyenne exponentielle)."""
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


def positions_ballon(ball_tracks):
    """Centre (x, y) du ballon pour chaque frame, ou (None, None) s'il n'est pas détecté."""
    ball_positions = []
    for frame_ball in ball_tracks:
        bbox = frame_ball.get(1, {}).get("bbox", None)
        if bbox:
            x1, y1, x2, y2 = bbox
            ball_positions.append(((x1 + x2) // 2, (y1 + y2) // 2))
        else:
            ball_positions.append((None, None))
    return ball_positions


def detecter_tirs_et_rebonds(rebound_detector, ball_positions, possession_list, player_assignment, basket_center):
    """Retourne (tentatives de tir, rebonds) par frame ; rebonds[t] = id de l'équipe ou False."""
    n = len(ball_positions)
    shot_attempts = [False] * n
    made_shots = [False] * n
    missed_shots = [False] * n
    rebounds = [False] * n

    for t in range(n):
        if ball_positions[t][0] is None:
            continue
        shot_attempts[t] = rebound_detector.detect_shot_attempt(ball_positions, possession_list, t)
        made_shots[t] = rebound_detector.detect_made_shot(ball_positions, basket_center, t)
        missed_shots[t] = rebound_detector.detect_missed_shot(ball_positions, basket_center, t)

    for t in range(n):
        if ball_positions[t][0] is None:
            continue
        if rebound_detector.detect_rebound(missed_shots, ball_positions, possession_list, t):
            current_holder = possession_list[t]
            team_id = player_assignment[t].get(current_holder, -1)
            if team_id != -1:
                rebounds[t] = team_id
                print(f"  🏀 Rebond frame {t}: équipe {team_id}")

    return shot_attempts, rebounds


def enregistrer_frames(video_frames, indices, dossier, prefixe):
    """Enregistre les frames `indices` en JPEG dans `dossier`."""
    os.makedirs(dossier, exist_ok=True)
    for idx in indices:
        cv2.imwrite(os.path.join(dossier, f"{prefixe}_{idx:04d}.jpg"), video_frames[idx])


def main(input_video_path=config.VIDEO_PAR_DEFAUT, utiliser_cache=True):
    output_dir = str(config.DOSSIER_SORTIE)
    stubs_dir = str(config.DOSSIER_STUBS)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(stubs_dir, exist_ok=True)

    print("Lecture de la vidéo...")
    video_frames = read_video(str(input_video_path))
    if len(video_frames) == 0:
        print(f"Erreur : la vidéo n'a pas été chargée ({input_video_path}).")
        return

    print("\nChargement des modèles...")
    player_tracker = PlayerTracker(model_path=str(config.MODELE_JOUEURS))
    ball_tracker = BallTracker(model_path=str(config.MODELE_BALLON))
    court_keypoint_detector = CourtKeypointDetector(model_path=str(config.MODELE_TERRAIN))
    basket_detector = BasketDetector(model_path=str(config.MODELE_PANIER))
    print("✓ Modèles chargés")

    print("\n🔍 ÉTAPE 1/3 - DÉTECTION DES KEYPOINTS DU TERRAIN")
    stub_path = os.path.join(stubs_dir, "court_key_points_stubs.pkl")
    if os.path.exists(stub_path):
        os.remove(stub_path)
    court_keypoints = court_keypoint_detector.get_court_keypoints(
        video_frames,
        read_from_stub=False,
        stub_path=stub_path,
        conf_threshold=config.SEUIL_CONFIANCE_TERRAIN
    )

    print("\n🏀 DÉTECTION DES PANIERS")
    basket_detections = basket_detector.detect_baskets(video_frames)

    print("\n👥 ÉTAPE 2/3 - DÉTECTION DES JOUEURS ET DE LA BALLE")
    player_tracks = player_tracker.get_objects_tracks(
        video_frames,
        read_from_stub=utiliser_cache,
        stub_path=os.path.join(stubs_dir, "player_track_stubs.pkl")
    )
    ball_tracks = ball_tracker.get_objects_tracks(
        video_frames,
        read_from_stub=utiliser_cache,
        stub_path=os.path.join(stubs_dir, "ball_track_stubs.pkl")
    )
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    print("\n📊 ÉTAPE 3/3 - ANALYSE DU JEU")
    team_assigner = TeamAssigner(str(config.MODELE_EQUIPES), str(config.MODELE_IDENTITE_JOUEURS),
                                 str(config.FICHIER_JOUEURS))
    player_assignment = team_assigner.get_player_teams_across_frames(
        video_frames,
        player_tracks,
        read_from_stub=utiliser_cache,
        stub_path=os.path.join(stubs_dir, "player_assignment_stubs.pkl")
    )
    player_identity_map = team_assigner.get_player_identity_map()

    ball_acquisition = BallAcquisitionDetector().detect_ball_possession(player_tracks, ball_tracks)
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(ball_acquisition, player_assignment)
    interceptions = pass_and_interception_detector.detect_interceptions(ball_acquisition, player_assignment)

    # --- Tirs et rebonds ---------------------------------------------------
    ball_positions = positions_ballon(ball_tracks)
    if basket_detections and basket_detections[0]:
        basket_center = basket_detections[0][0]["center"]
    else:
        basket_center = (0, 0)

    rebound_detector = ReboundDetector(basket_threshold=config.SEUIL_DISTANCE_PANIER)
    shot_attempts, rebounds = detecter_tirs_et_rebonds(
        rebound_detector, ball_positions, ball_acquisition, player_assignment, basket_center)

    shot_dir = os.path.join(output_dir, "shot_frames")
    enregistrer_frames(video_frames, [i for i, shot in enumerate(shot_attempts) if shot], shot_dir, "shot_frame")
    print(f"Frames de tir enregistrées dans : {shot_dir}")

    # Un seul rebond par séquence (frames distantes de plus de 2)
    rebound_frames = []
    rebound_teams = []
    for i, reb in enumerate(rebounds):
        if reb:
            if not rebound_frames or i - rebound_frames[-1] > 2:
                rebound_frames.append(i)
                rebound_teams.append(reb)

    rebound_dir = os.path.join(output_dir, "rebound_frames")
    enregistrer_frames(video_frames, rebound_frames, rebound_dir, "rebound_frame")
    print(f"Frames de rebond enregistrées dans : {rebound_dir}")

    if rebound_teams:
        bucks_rebounds = sum(1 for t in rebound_teams if t == 1)
        celtics_rebounds = sum(1 for t in rebound_teams if t == 2)
        print(f"📊 Rebonds détectés: Bucks: {bucks_rebounds}, Celtics: {celtics_rebounds}")

    # --- Vidéo annotée -------------------------------------------------------
    output_video_frames = video_frames.copy()
    output_video_frames = CourtKeypointDrawer().draw(output_video_frames, court_keypoints)
    output_video_frames = PlayerTracksDrawer().draw(output_video_frames, player_tracks, player_assignment,
                                                    ball_acquisition, player_identity_map)
    output_video_frames = BallTracksDrawer().draw(output_video_frames, ball_tracks)
    # output_video_frames = TeamBallControlDrawer().draw(output_video_frames, player_assignment, ball_acquisition)
    output_video_frames = ReboundDrawer().draw(output_video_frames, rebounds)
    output_video_frames = BasketDrawer().draw(output_video_frames, basket_detections)

    save_video(output_video_frames, str(config.VIDEO_SORTIE))

    print("\n✅ TRAITEMENT TERMINÉ AVEC SUCCÈS")
    print(f"📹 Vidéo: {config.VIDEO_SORTIE}")
    print(f"🎯 Keypoints détectés: {sum(len(kp) for kp in court_keypoints)}")
    print(f"🔄 Passes: {len(passes)}")
    print(f"🛑 Interceptions: {len(interceptions)}")
    print(f"🏀 Frames de rebond détectées : {rebound_frames}")


def parse_args():
    parser = argparse.ArgumentParser(prog="python -m analyse_video", description=__doc__.splitlines()[0])
    parser.add_argument("video", nargs="?", default=config.VIDEO_PAR_DEFAUT,
                        help=f"vidéo à analyser (défaut : {config.VIDEO_PAR_DEFAUT.relative_to(config.RACINE_PROJET)})")
    parser.add_argument("--sans-cache", action="store_true",
                        help="recalcule les détections au lieu de relire les stubs pickle")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.video, utiliser_cache=not args.sans_cache)
