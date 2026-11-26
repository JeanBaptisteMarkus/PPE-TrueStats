"""Position du panier à chaque frame, pour une vidéo quelconque (caméra mobile)."""
import bisect


def paniers_par_frame(basket_detections, ball_positions):
    """Cadre (x1, y1, x2, y2) du panier visé à chaque frame, ou None.

    - plusieurs paniers détectés : on garde le plus proche du ballon ;
    - frame sans détection : cadre détecté à la frame la plus proche dans le temps ;
    - aucun panier dans toute la vidéo : None pour chaque frame.
    """
    n = len(ball_positions)
    cadres = [None] * n
    for t, detections in enumerate(basket_detections[:n]):
        if not detections:
            continue
        bx, by = ball_positions[t]
        if bx is None:
            choisi = detections[0]
        else:
            choisi = min(detections, key=lambda d: (d["center"][0] - bx) ** 2 + (d["center"][1] - by) ** 2)
        cadres[t] = tuple(choisi["bbox"])

    connues = [t for t, c in enumerate(cadres) if c is not None]
    if not connues:
        return cadres
    for t in range(n):
        if cadres[t] is None:
            i = bisect.bisect_left(connues, t)
            voisines = [connues[j] for j in (i - 1, i) if 0 <= j < len(connues)]
            cadres[t] = cadres[min(voisines, key=lambda k: abs(k - t))]
    return cadres
