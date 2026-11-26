"""Pipeline d'analyse vidéo : `python -m analyse_video [video.mp4] [--sans-cache]`.

Étapes :
1. détection des repères du terrain et des paniers ;
2. suivi des joueurs et du ballon ;
3. attribution des équipes / identités, possession, passes, interceptions ;
4. détection des tirs ratés puis des rebonds ;
5. export des frames de tir / rebond et de la vidéo annotée.

Les résultats vont dans output_videos/<nom de la vidéo>/ et le cache des
détections dans stubs/<nom de la vidéo>_<taille>/ : chaque vidéo a les siens.
"""
import argparse
import os
from pathlib import Path

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
from .equipes import EquipesParCouleur
from .evenements import (
    BallAcquisitionDetector,
    PassAndInterceptionDetector,
    ReboundDetector,
    centres_panier_par_frame,
)
from .utils.video_utils import lire_fps, read_video, save_video


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


def dossiers_pour_video(input_video_path):
    """(dossier de cache, dossier de sortie) propres à une vidéo.

    Le cache est identifié par le nom ET la taille du fichier, pour ne jamais
    relire les détections d'une autre vidéo portant le même nom.
    """
    chemin = Path(input_video_path)
    taille = chemin.stat().st_size if chemin.exists() else 0
    return config.DOSSIER_STUBS / f"{chemin.stem}_{taille}", config.DOSSIER_SORTIE / chemin.stem


def nombre_evenements(evenements_par_frame):
    """Nombre de frames où un événement (passe, interception) a eu lieu (-1 = aucun)."""
    return sum(1 for e in evenements_par_frame if e != -1)


def detecter_tirs_et_rebonds(rebound_detector, ball_positions, possession_list, player_assignment, basket_centers):
    """Retourne (tentatives de tir, rebonds) par frame ; rebonds[t] = id de l'équipe ou False.

    basket_centers[t] : centre du panier à la frame t (None si inconnu).
    """
    n = len(ball_positions)
    shot_attempts = [False] * n
    made_shots = [False] * n
    missed_shots = [False] * n
    rebounds = [False] * n

    for t in range(n):
        if ball_positions[t][0] is None:
            continue
        shot_attempts[t] = rebound_detector.detect_shot_attempt(ball_positions, possession_list, t)
        if basket_centers[t] is None:
            continue
        made_shots[t] = rebound_detector.detect_made_shot(ball_positions, basket_centers[t], t)
        missed_shots[t] = rebound_detector.detect_missed_shot(ball_positions, basket_centers[t], t)

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
    """Enregistre les frames `indices` en JPEG dans `dossier` (en retirant celles d'une analyse précédente)."""
    os.makedirs(dossier, exist_ok=True)
    for ancien in Path(dossier).glob(f"{prefixe}_*.jpg"):
        ancien.unlink()
    for idx in indices:
        cv2.imwrite(os.path.join(dossier, f"{prefixe}_{idx:04d}.jpg"), video_frames[idx])


def main(input_video_path=config.VIDEO_PAR_DEFAUT, utiliser_cache=True, attribution="couleur", noms_equipes=None):
    dossier_stubs, dossier_sortie = dossiers_pour_video(input_video_path)
    output_dir, stubs_dir = str(dossier_sortie), str(dossier_stubs)
    output_video_path = os.path.join(output_dir, "output_video.avi")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(stubs_dir, exist_ok=True)

    print("Lecture de la vidéo...")
    video_frames = read_video(str(input_video_path))
    if len(video_frames) == 0:
        print(f"Erreur : la vidéo n'a pas été chargée ({input_video_path}).")
        return
    fps = lire_fps(str(input_video_path))
    print(f"{len(video_frames)} frames à {fps:.2f} images/s")

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
    if attribution == "modele":
        # Modèles entraînés sur le match Celtics - Bucks uniquement (donne aussi le nom des joueurs)
        team_assigner = TeamAssigner(str(config.MODELE_EQUIPES), str(config.MODELE_IDENTITE_JOUEURS),
                                     str(config.FICHIER_JOUEURS))
        stub_equipes = "player_assignment_stubs.pkl"
        noms_equipes = noms_equipes or ("Bucks", "Celtics")
    else:
        # Couleur des maillots : fonctionne pour n'importe quel match
        team_assigner = EquipesParCouleur()
        stub_equipes = "team_color_stubs.pkl"
        noms_equipes = noms_equipes or ("Équipe claire", "Équipe foncée")
    player_assignment = team_assigner.get_player_teams_across_frames(
        video_frames,
        player_tracks,
        read_from_stub=utiliser_cache,
        stub_path=os.path.join(stubs_dir, stub_equipes)
    )
    player_identity_map = team_assigner.get_player_identity_map()
    couleurs_equipes = getattr(team_assigner, "couleurs_equipes", {})
    for numero, nom in enumerate(noms_equipes, start=1):
        couleur = couleurs_equipes.get(numero)
        print(f"  Équipe {numero} = {nom}" + (f" (couleur BGR du maillot {couleur})" if couleur else ""))
    if attribution == "couleur" and not team_assigner.attribution_fiable():
        print(f"⚠️ Maillots de couleurs proches (écart {team_assigner.ecart_couleurs:.0f}) : "
              "attribution des équipes peu fiable.")

    ball_acquisition = BallAcquisitionDetector().detect_ball_possession(player_tracks, ball_tracks)
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(ball_acquisition, player_assignment)
    interceptions = pass_and_interception_detector.detect_interceptions(ball_acquisition, player_assignment)

    # --- Tirs et rebonds ---------------------------------------------------
    ball_positions = positions_ballon(ball_tracks)
    basket_centers = centres_panier_par_frame(basket_detections, ball_positions)
    if all(c is None for c in basket_centers):
        print("⚠️ Aucun panier détecté dans la vidéo : tirs ratés et rebonds non détectables.")

    rebound_detector = ReboundDetector(basket_threshold=config.SEUIL_DISTANCE_PANIER)
    shot_attempts, rebounds = detecter_tirs_et_rebonds(
        rebound_detector, ball_positions, ball_acquisition, player_assignment, basket_centers)

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
        rebonds_1 = sum(1 for t in rebound_teams if t == 1)
        rebonds_2 = sum(1 for t in rebound_teams if t == 2)
        print(f"📊 Rebonds détectés: {noms_equipes[0]}: {rebonds_1}, {noms_equipes[1]}: {rebonds_2}")

    # --- Vidéo annotée -------------------------------------------------------
    output_video_frames = video_frames.copy()
    output_video_frames = CourtKeypointDrawer().draw(output_video_frames, court_keypoints)
    output_video_frames = PlayerTracksDrawer(
        team_1_color=couleurs_equipes.get(1, (255, 255, 255)),
        team_2_color=couleurs_equipes.get(2, (0, 230, 0)),
    ).draw(output_video_frames, player_tracks, player_assignment,
                                                    ball_acquisition, player_identity_map)
    output_video_frames = BallTracksDrawer().draw(output_video_frames, ball_tracks)
    # output_video_frames = TeamBallControlDrawer().draw(output_video_frames, player_assignment, ball_acquisition)
    output_video_frames = ReboundDrawer(noms_equipes).draw(output_video_frames, rebounds)
    output_video_frames = BasketDrawer().draw(output_video_frames, basket_detections)

    save_video(output_video_frames, output_video_path, fps=fps)

    print("\n✅ TRAITEMENT TERMINÉ AVEC SUCCÈS")
    print(f"📹 Vidéo: {output_video_path}")
    print(f"🎯 Keypoints détectés: {sum(len(kp) for kp in court_keypoints)}")
    print(f"🔄 Passes: {nombre_evenements(passes)}")
    print(f"🛑 Interceptions: {nombre_evenements(interceptions)}")
    print(f"🏀 Frames de rebond détectées : {rebound_frames}")


def parse_args():
    parser = argparse.ArgumentParser(prog="python -m analyse_video", description=__doc__.splitlines()[0])
    parser.add_argument("video", nargs="?", default=config.VIDEO_PAR_DEFAUT,
                        help=f"vidéo à analyser (défaut : {config.VIDEO_PAR_DEFAUT.relative_to(config.RACINE_PROJET)})")
    parser.add_argument("--attribution", choices=["couleur", "modele"], default="couleur",
                        help="équipes par couleur des maillots (tout match, défaut) ou par les modèles "
                             "team.pt / JoueurEquipe.pt (match Celtics - Bucks uniquement)")
    parser.add_argument("--equipes", nargs=2, metavar=("EQUIPE_1", "EQUIPE_2"),
                        help="noms des équipes : avec --attribution couleur, l'équipe 1 est celle "
                             "au maillot le plus clair")
    parser.add_argument("--sans-cache", action="store_true",
                        help="recalcule les détections au lieu de relire les stubs pickle")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.video, utiliser_cache=not args.sans_cache, attribution=args.attribution, noms_equipes=args.equipes)
