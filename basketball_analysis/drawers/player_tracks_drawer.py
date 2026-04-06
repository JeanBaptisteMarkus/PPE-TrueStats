from .utils import draw_ellipse, draw_triangle
import cv2

class PlayerTracksDrawer:

    def __init__(self, team_1_color=(255,245,238), team_2_color=(128,0,0)):
        self.default_player_team_id = 1
        self.team_1_color = team_1_color
        self.team_2_color = team_2_color
        self.player_names = {}

    def draw(self, video_frames, tracks, player_assignment, ball_acquisition, player_identity_map=None):
        output_video_frames = []
        
        if player_identity_map is None:
            player_identity_map = {}
        
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            player_dict = tracks[frame_num]
            player_assignment_for_frame = player_assignment[frame_num]
            player_id_has_ball = ball_acquisition[frame_num]

            for track_id, player in player_dict.items():
                team_id = player_assignment_for_frame.get(track_id, self.default_player_team_id)

                if team_id == 1:
                    color = self.team_1_color
                else:
                    color = self.team_2_color

                if track_id == player_id_has_ball:
                    frame = draw_triangle(frame, player["bbox"], (0,0,255))

                frame = draw_ellipse(frame, player["bbox"], color, track_id)

                # Afficher le nom du joueur si disponible
                if track_id in player_identity_map:
                    player_name = player_identity_map[track_id]["name"]
                    bbox = player["bbox"]
                    x1, y1, x2, y2 = map(int, bbox)
                    cv2.putText(frame, player_name, (x1, y1-15), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

            output_video_frames.append(frame)
    
        return output_video_frames