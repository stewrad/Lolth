"""Angle offsets for a loaded RF dataset (in-place)."""
import numpy as np


def shift_dataset_angles(frame, azimuth_delta=0.0, elevation_delta=0.0):
    """Shift A1/Theta on a ±180° circle, and E1/Phi by signed degrees.

    Keeping both original field names and plotting aliases consistent avoids
    changing the loader contract. Azimuth's +180 and -180 are equivalent.
    """
    if azimuth_delta:
        theta = frame["Theta"].to_numpy(dtype=float)
        wrapped = (theta + float(azimuth_delta) + 180.0) % 360.0 - 180.0
        frame["Theta"] = wrapped
        if "A1" in frame:
            frame["A1"] = wrapped
    if elevation_delta:
        phi = frame["Phi"].to_numpy(dtype=float) + float(elevation_delta)
        frame["Phi"] = phi
        if "E1" in frame:
            frame["E1"] = phi
    return frame
