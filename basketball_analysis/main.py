import os
import sys
from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from drawers import(
    PlayerTracksDrawer, 
    BallTracksDrawer,
    TeamBallControlDrawer,
    PassAndInterceptionDrawer,
    CourtKeypointDrawer
)
from team_assigner import TeamAssigner
from ball_acquisition import BallAcquisitionDetector
from pass_and_interception_detector import PassAndInterceptionDetector
from court_keypoint_detector import CourtKeypointDetector

def main():
    
    #Read Video
    video_frames = read_video("input_videos/video_1.mp4")

    #Initialize Tracker
    player_tracker = PlayerTracker(model_path="models/player_detector.pt")
    ball_tracker = BallTracker(model_path="models/ball_detector.pt")

    # Initialize Court Keypoint Detector
    court_keypoint_detector = CourtKeypointDetector(model_path="models/court_keypoint_detector.pt")

    #Run Trackers
    player_tracks = player_tracker.get_objects_tracks(video_frames, 
                                                      read_from_stub = True, 
                                                      stub_path = "stubs/player_track_stubs.pkl"
                                                      )
    
    ball_tracks = ball_tracker.get_objects_tracks(video_frames,
                                                  read_from_stub = True,
                                                  stub_path = "stubs/ball_track_stubs.pkl"
                                                  )
    
    # Get Court Keypoints
    court_keypoints = court_keypoint_detector.get_court_keypoints(video_frames,
                                                                read_from_stub = True,
                                                                stub_path = "stubs/court_key_points_stubs.pkl"
                                                                )

    #Remove Wrong Ball Detections
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)
    #Interpolate Ball Tracks
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    # Assign Player Teams
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(video_frames,
                                                                 player_tracks,
                                                                 read_from_stub = True,
                                                                 stub_path="stubs/player_assignment_stubs.pkl"
                                                                 )
    
    # Ball Acquisition Detection
    ball_acquisition_detector = BallAcquisitionDetector()
    ball_acquisition = ball_acquisition_detector.detect_ball_possession(player_tracks, ball_tracks)

    # Detect Passes and Interceptions
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(ball_acquisition, player_assignment)
    interceptions = pass_and_interception_detector.detect_interceptions(ball_acquisition, player_assignment)

    #Draw Output
    #Intitialize Drawers
    player_tracks_drawer = PlayerTracksDrawer()
    ball_tracks_drawer = BallTracksDrawer()
    team_ball_control_drawer = TeamBallControlDrawer()
    pass_and_interception_drawer = PassAndInterceptionDrawer()
    court_keypoint_drawer = CourtKeypointDrawer()

    # Draw Object Tracks
    output_video_frames = player_tracks_drawer.draw(video_frames,
                                                    player_tracks,
                                                    player_assignment,
                                                    ball_acquisition
                                                    )
    output_video_frames = ball_tracks_drawer.draw(output_video_frames, ball_tracks)

    #Draw Team Ball Control
    output_video_frames = team_ball_control_drawer.draw(output_video_frames,
                                                        player_assignment,
                                                        ball_acquisition)
    
    # Draw Pass and Interception 
    output_video_frames = pass_and_interception_drawer.draw(output_video_frames,
                                                            passes,
                                                            interceptions)
    
    # Draw Court Keypoints
    output_video_frames = court_keypoint_drawer.draw(output_video_frames, 
                                                     court_keypoints)

    #Save Video
    save_video(output_video_frames, "output_videos/output_video.avi")

    print("test")

if __name__ == "__main__":
    main()