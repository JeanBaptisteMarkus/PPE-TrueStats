# True Stats: Basketball Rebound Analysis

## Overview

This project (PPE, ECE ING4) analyzes and evaluates basketball rebounds using data-driven methods. The main objective is an algorithm that rates how hard a rebound was to win, based on player positions, distances, heights, rebounding stats and game context.

The project has two components:
- **Virtual court + rebound value algorithm** (`terrain_virtuel/`): players are positioned by hand on a virtual half court, the user picks the rebounder, and the algorithm computes a rebound value between 0.7 (easy) and 1.3 (heavily contested). This part is functional.
- **Video analysis** (`analyse_video/`): a YOLO-based pipeline that detects players, ball, court and basket in real footage, tracks possession, and detects shots and rebounds. This part is **in development**: positions are still in image pixels and are not yet converted to court meters, so its output is not yet fed into the rebound algorithm.

## Project structure

```
PPE-TrueStats/
├── terrain_virtuel/          Virtual court (python -m terrain_virtuel)
│   ├── config.py             Court dimensions, basket position, radii, file paths
│   ├── joueurs.py            Joueur class, NBA teams, CSV loading
│   ├── situation.py          Geometry of a rebound situation (nearby opponents, ratio, distance)
│   ├── calcul_rebond.py      Rebound value algorithm (offensive / defensive)
│   ├── export.py             Excel export (one row per situation)
│   └── interface/            GUI: context window (tkinter), court drawing, drag & drop,
│                             substitutions, "Valider" button (matplotlib)
├── analyse_video/            Video pipeline (python -m analyse_video)
│   ├── config.py             Paths to models, videos, caches
│   ├── detection/            YOLO perception: players, ball, court keypoints, basket, teams
│   ├── evenements/           Game logic (numpy only): possession, passes, interceptions, rebounds
│   ├── affichage/            OpenCV drawing of the annotated output video
│   ├── utils/                Bounding boxes, video I/O, pickle caches
│   └── models/               YOLO weights (*.pt, not versioned, see models/README.md)
├── entrainement/             YOLO training scripts and notebooks
├── experimentations/         Earlier prototypes (sigmoid formula, random forest)
├── data/
│   ├── joueurs_nba.csv           300 NBA players (ID, team, name, height cm, rebounds/game)
│   └── joueurs_celtics_bucks.csv 18 players used by the video identification model
├── tests/                    pytest suite
├── requirements.txt          Virtual court dependencies
└── requirements-video.txt    Video analysis dependencies (YOLO, OpenCV…)
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt            # virtual court only
pip install -r requirements-video.txt      # + video analysis
```

tkinter ships with Python; on Debian/Ubuntu install it with `sudo apt install python3-tk`.

## Usage

### Virtual court

```bash
python -m terrain_virtuel
```

1. Choose both teams, the score and the remaining time (empty fields get random values).
2. Drag players on the court; click a player then a name in the right panel to substitute.
3. Select the rebounder, tick **Rebond Offensif** if needed, then click **Valider**.

The rebound value is printed in the terminal and the situation is appended to `output/donnees_rebonds.xlsx`.

### Video analysis

Put the YOLO weights in `analyse_video/models/` (see [its README](analyse_video/models/README.md)) and a video in `analyse_video/input_videos/`, then:

```bash
python -m analyse_video                         # analyse_video/input_videos/video9.mp4
python -m analyse_video path/to/video.mp4 --sans-cache
```

Player/ball tracks and team assignments are cached in `analyse_video/stubs/`. Use `--sans-cache` when you change video. Results go to `analyse_video/output_videos/`: an annotated video, plus the shot and rebound frames.

The videos, datasets and caches from the original work are still available on the `dev_analyse_vidéo` branch (they were not copied to `main`: ~600 MB).

### Experiments

```bash
python experimentations/version_initiale_terrain.py   # first prototype (sigmoid formula)
python experimentations/random_forest_rebond.py       # random forest on synthetic data
```

### Tests

```bash
pytest
```

## How the rebound value works

For the selected rebounder, `terrain_virtuel/situation.py` computes:
- opponents within 1 m, and opponents between 1 m and 2 m (their heights and rebound averages);
- the opponents / teammates ratio within 3 m;
- the distance between the rebounder and the basket;
- the score difference (from the rebounder's team point of view) and the remaining time.

`terrain_virtuel/calcul_rebond.py` then sums **difficulty** terms (close, taller or better opponents) and **ease** terms (nobody around, height or stats advantage, long rebound, numerical superiority), adds a **clutch** bonus for close games in the last minute, and clamps the result to [0.7, 1.3]. Offensive rebounds carry an extra structural difficulty (+0.07) and weigh opponents between 1 m and 2 m more heavily.

## Roadmap

1. Map image coordinates to court meters, using a homography from the detected court keypoints.
2. At each detected rebound, build the situation (players' positions in meters) automatically.
3. Feed it to the rebound value algorithm, so a real game can be rated from its video alone.
