import cv2
import os

def read_video(video_path):
    cap=cv2.VideoCapture(video_path)
    frames=[]
    while True:
        ret,frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

def save_video(output_video_frames, output_video_path):
    if not output_video_frames:
        raise ValueError("Aucune frame à enregistrer")
    dossier = os.path.dirname(output_video_path)
    if dossier:
        os.makedirs(dossier, exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_video_path, fourcc, 24.0, (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()
