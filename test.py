import os
import shutil
import random
import yaml
from ultralytics import YOLO

# ======================
# CONFIG
# ======================
dataset_raw = "frames"       # dossier contenant tes .jpg et .txt
dataset_dir = "dataset"      # dossier de sortie train/val + data.yaml
epochs = 200                 # nombre d'epochs
batch_size = 16
img_size = 640

# ======================
# LISTE DES JOUEURS
# ID unique + numéro de maillot + nom pour affichage
# ======================
player_list = [
    "0_55_BaylorScheierman",
    "1_4_NikolaVucecic",
    "2_28_HugoGonzalez",
    "3_3_MylesTurner",
    "4_21_OusmaneDieng",
    "5_34_GiannisAntetokounmpo",
    "6_30_SamHauser",
    "7_24_CameronThomas",
    "8_9_DerrickWhite",
    "9_7_KevinPorter",
    "10_11_PaytonPrichard",
    "11_9_BobbyPortis",
    "12_11_GaryHarris",
    "13_0_JerichoSims",
    "14_13_RonHarperJr",
    "15_44_AndreJacksonJr",
    "16_52_LukaGarza",
    "17_35_PeteNance"
]

# Extraire uniquement la partie affichée sur les bbox
names = [p.split("_", 1)[1] for p in player_list]

# ======================
# 1️⃣ Créer les dossiers train/val
# ======================
for d in ["train", "val"]:
    os.makedirs(os.path.join(dataset_dir, d, "images"), exist_ok=True)
    os.makedirs(os.path.join(dataset_dir, d, "labels"), exist_ok=True)

# ======================
# 2️⃣ Split train/val et copier les fichiers
# ======================
images = [f for f in os.listdir(dataset_raw) if f.endswith(".jpg")]
random.shuffle(images)
split = int(0.8 * len(images))

for i, img in enumerate(images):
    name = os.path.splitext(img)[0]
    txt = name + ".txt"
    folder = "train" if i < split else "val"

    shutil.copy(os.path.join(dataset_raw, img), os.path.join(dataset_dir, folder, "images", img))
    shutil.copy(os.path.join(dataset_raw, txt), os.path.join(dataset_dir, folder, "labels", txt))

# ======================
# 3️⃣ Générer data.yaml
# ======================
data_yaml = {
    "train": os.path.abspath(os.path.join(dataset_dir, "train/images")),
    "val": os.path.abspath(os.path.join(dataset_dir, "val/images")),
    "nc": len(names),
    "names": names
}

yaml_path = os.path.join(dataset_dir, "data.yaml")
with open(yaml_path, "w") as f:
    yaml.dump(data_yaml, f)

print("[+] data.yaml généré :", yaml_path)
print("[+] Classes :", names)

# ======================
# 4️⃣ Lancer l'entraînement YOLOv8
# ======================
model = YOLO("yolov8n.pt")  # modèle de base YOLOv8

print("[*] Training...")
model.train(
    data=yaml_path,
    epochs=epochs,
    imgsz=img_size,
    batch=batch_size,
    name="train",
    augment=True  # data augmentation activée
)

print("[+] Training terminé")
print("Ton modèle est ici : runs/detect/train/weights/best.pt")