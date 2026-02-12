import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from drawers import(
    PlayerTracksDrawer, 
    BallTracksDrawer
)
from team_assigner import TeamAssigner

def main():
    
    #Read Video
    video_frames = read_video("input_videos/video_1.mp4")

    #Initialize Tracker
    player_tracker = PlayerTracker(model_path="models/player_detector.pt")
    ball_tracker = BallTracker(model_path="models/ball_detector.pt")

    #Run Detector
    player_tracks = player_tracker.get_objects_tracks(video_frames, 
                                                      read_from_stub = True, 
                                                      stub_path = "stubs/player_track_stubs.pkl"
                                                      )
    
    ball_tracks = ball_tracker.get_objects_tracks(video_frames,
                                                  read_from_stub = True,
                                                  stub_path = "stubs/ball_track_stubs.pkl"
                                                  )

    #Remove Wrong Ball Detections
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)
    #Interpolate Ball Tracks
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    # Assign Player Teams
    team_assigner = TeamAssigner()
    player_teams = team_assigner.get_player_teams_across_frames(video_frames,
                                                                 player_tracks,
                                                                 read_from_stub=True,
                                                                 stub_path="stubs/player_assignment_stubs.pkl"
                                                                 )
    print(player_teams)

    #Draw Output
    #Intitialize Drawers
    player_tracks_drawer = PlayerTracksDrawer()
    ball_tracks_drawer = BallTracksDrawer()


    # Draw Object Tracks
    output_video_frames = player_tracks_drawer.draw(video_frames, player_tracks)
    output_video_frames = ball_tracks_drawer.draw(output_video_frames, ball_tracks)

    #Save Video
    save_video(output_video_frames, "output_videos/output_video.avi")

if __name__ == "__main__":
    main()