import cv2
import os

FPS_PAR_DEFAUT = 24.0


def read_video(video_path):
    cap=cv2.VideoCapture(video_path)
    frames=[]
    while True:
        ret,frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames


def lire_fps(video_path, defaut=FPS_PAR_DEFAUT):
    """Nombre d'images par seconde de la vidéo (`defaut` s'il est illisible)."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps if fps and fps > 0 else defaut


def save_video(output_video_frames, output_video_path, fps=FPS_PAR_DEFAUT):
    if not output_video_frames:
        raise ValueError("Aucune frame à enregistrer")
    dossier = os.path.dirname(output_video_path)
    if dossier:
        os.makedirs(dossier, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()
