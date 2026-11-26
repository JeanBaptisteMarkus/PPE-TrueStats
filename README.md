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
│   ├── detection/            YOLO perception: players, ball, court keypoints, basket
│   ├── equipes/              Team assignment by jersey color (works for any game)
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
python -m analyse_video path/to/video.mp4 --equipes Bucks Celtics   # names: lighter jersey first
```

Any video can be given as input. Each video gets its own folders:
- `analyse_video/output_videos/<video name>/`: the annotated video (same frame rate as the source), plus the shot and rebound frames;
- `analyse_video/stubs/<video name>_<file size>/`: cached player/ball tracks and team assignments, reused on the next run of the same video. Use `--sans-cache` to recompute them.

Players are split into two teams by **jersey color**, computed again for every video. A color is never tied to a team for good, so two different teams wearing red in two different games are not a problem. Team 1 is the team with the lighter jersey; `--equipes` gives the teams their names. The previous models trained on the Celtics vs Bucks game remain available with `--attribution modele`.

The basket position is detected on every frame (the camera can move). When several baskets are visible, the one closest to the ball is used. If no basket is detected in the whole video, shots and rebounds are not detected and a warning is printed.

**Shots and rebounds** (`analyse_video/evenements/tirs.py`):
1. the ball leaves a player, or is already in the air when the video starts;
2. without anyone catching it, the ball goes higher than the basket area, then enters it within 3 s. A pass is caught before, or does not go up;
3. the shot is made if the ball leaves the basket area through the bottom, in its middle (through the rim). Otherwise it is missed;
4. the rebound is the first player to gain possession after a missed shot, within 5 s. It is offensive if the rebounder is on the shooter's team, defensive otherwise.

The basket area is the detected basket box, widened by a margin proportional to its size plus one ball diameter. Durations are in seconds and converted with the video frame rate. On `video9.mp4` the rule finds the actual play: a missed shot by Milwaukee (frame 73) and a defensive rebound by Boston (frame 220).

#### Current limitations on arbitrary videos

- **Similar jerseys**: if both teams wear similar colors, they cannot be told apart by color; a warning is printed.
- **Referees** are left out by the player detector, which only keeps the "Player" class. A referee who still got through would be put in the team with the closest jersey color.
- **Player identity** (needed for height and rebound stats) is not known in color mode: it would require reading jersey numbers. Only `--attribution modele` names players, and only for the Celtics vs Bucks game.
- **2D view**: a ball passing in front of or behind the rim can be judged wrongly, and an air ball that never gets near the basket is not counted as a shot.
- **Possession and tracking**: the shooter and the rebounder come from the possession detector. A ball flying close to a defender can be taken as his possession, and when the tracker swaps two players' IDs, the team of that track is wrong for part of the video.
- **Possession thresholds** (distance 50 px, 13 frames to confirm a possession) are still fixed in pixels and frames. They do not adapt to the resolution, zoom or frame rate of the video.
- **Memory**: the whole video is loaded in RAM (about 2.7 MB per 720p frame), so long videos should be cut into clips.

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
