"""Logique de jeu à partir des détections : possession, passes, interceptions, tirs et rebonds.

Ce sous-package ne dépend que de numpy (pas de YOLO ni d'OpenCV).
"""
from .ball_acquisition_detector import BallAcquisitionDetector
from .pass_and_interception_detector import PassAndInterceptionDetector
from .rebound_detector import ReboundDetector, centres_panier_par_frame
