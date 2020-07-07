from pathlib import Path

import cv2
import numpy as np


def read_image(path: Path) -> np.ndarray:
    """Read the image from the file in numpy format.

    Args:
        path: The path to the file to be read.

    Returns:
        Image data in numpy format, where the shape is (Height, Width, Channel).
        The color model is RGB.
    """
    image = cv2.imread(str(path))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def read_video(path: Path) -> np.ndarray:
    """Read the video from the file in numpy format.

    Args:
        path: The path to the file to be read.

    Returns:
        Video data in numpy format, where the shape is (Frame, Height, Width, Channel).
    """
    video = []
    cap = cv2.VideoCapture(str(path))
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video.append(frame)
        else:
            break
    cap.release()
    return np.array(video)
