import cv2
import numpy as np
from PIL import ImageOps, Image


def get_time(
        frame_idx: int,
        fps: int
) -> int:
    return int(frame_idx * 1000 / fps)


def frames_diff(
        frame1: np.ndarray,
        frame2: np.ndarray
) -> float:
    return np.abs(frame1 - frame2).sum()


def get_mask(image: np.ndarray):
    y, x, _ = image.shape
    x1, y1, x2, y2 = int(0.1 * x), int(0.7 * y), int(0.95 * x), int(0.99 * y)
    crop = image[y1:y2, x1:x2, :]
    mask = cv2.Canny(
        crop,
        threshold1=850,
        threshold2=int(850 / 1.5),
        L2gradient=True
    )

    contours, hierarchy = cv2.findContours(mask,
                                           mode=cv2.RETR_LIST,
                                           method=cv2.CHAIN_APPROX_NONE)
    result = cv2.drawContours(
        mask,
        np.array(contours, dtype=object),
        -1,  # all
        color=(255, 255, 255),
        thickness=1,
        lineType=8
    )
    return ImageOps.invert(Image.fromarray(result))
