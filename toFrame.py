import cv2
import os

input_folder = "clips_train"
output_folder = "frames"
frame_rate = 2

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for video_name in os.listdir(input_folder):
    if not video_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        continue

    video_path = os.path.join(input_folder, video_name)
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = max(int(fps / frame_rate), 1)

    count = 0
    saved_count = 0

    video_base = os.path.splitext(video_name)[0]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if count % frame_interval == 0:
            frame_filename = os.path.join(
                output_folder,
                f"{video_base}_frame_{saved_count:05d}.jpg"
            )
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        count += 1

    cap.release()
    print(f"✔ {video_name} terminé")

print("Toutes les vidéos sont traitées")