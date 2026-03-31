import cv2

def draw_ellipse(frame, bbox, color=(0, 255, 0), track_id=0):
    """
    Dessine une ellipse autour de la bbox d'un joueur
    bbox: [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = map(int, bbox)
    center = ((x1 + x2)//2, (y1 + y2)//2)
    axes = ((x2 - x1)//2, (y2 - y1)//2)
    cv2.ellipse(frame, center, axes, 0, 0, 360, color, 2)
    cv2.putText(frame, str(track_id), (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return frame