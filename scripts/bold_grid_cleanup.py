"""Remove long table-rule pixels before measuring cell stroke thickness.

Parameters are fixed from the earlier error diagnosis, not tuned on this run.
The downstream median/vote/ResNet decisions keep their upstream thresholds.
"""
import cv2
import numpy as np


def remove_grid_lines(ink: np.ndarray) -> np.ndarray:
    """Return a new uint8 foreground mask, excluding long horizontal/vertical runs."""
    height, width = ink.shape
    horizontal = cv2.morphologyEx(
        ink, cv2.MORPH_OPEN,
        np.ones((1, max(15, round(width * 0.55))), dtype=np.uint8),
    )
    vertical = cv2.morphologyEx(
        ink, cv2.MORPH_OPEN,
        np.ones((max(15, round(height * 0.80)), 1), dtype=np.uint8),
    )
    cleaned = ink.copy()
    cleaned[cv2.bitwise_or(horizontal, vertical) > 0] = 0
    return cleaned


def cell_stroke_width(cell: dict, image: np.ndarray) -> float | None:
    height, width = image.shape
    x1, y1, x2, y2 = cell['bbox']
    left, right = int(x1 * width), int(x2 * width)
    top, bottom = int(y1 * height), int(y2 * height)
    crop = image[top:bottom, left:right]
    if crop.size == 0 or min(crop.shape) < 5:
        return None
    _, ink = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    border = max(1, round(min(ink.shape) * 0.03))
    ink[:border, :] = ink[-border:, :] = 0
    ink[:, :border] = ink[:, -border:] = 0
    ink = remove_grid_lines(ink)
    if int((ink > 0).sum()) < 10:
        return None
    distance = cv2.distanceTransform(ink, cv2.DIST_L2, 3)
    return float(2 * distance[ink > 0].mean())
