"""Periodic angle offsets for loaded RF datasets."""
import numpy as np


def shift_dataset_angles(frame, azimuth_delta=0.0, elevation_delta=0.0):
    """Shift angular fields and wrap into the original signed intervals.

    Theta/A1: 360-degree period, canonical [-180, 180).
    Phi/E1:   180-degree period, canonical [-90, 90).

    The end points of each interval are equivalent under this periodic
    operation. Preserve the original source-field/plotting-alias agreement.
    """
    if azimuth_delta:
        theta = frame["Theta"].to_numpy(dtype=float)
        wrapped = (theta + float(azimuth_delta) + 180.0) % 360.0 - 180.0
        frame["Theta"] = wrapped
        if "A1" in frame.columns:
            frame["A1"] = wrapped

    if elevation_delta:
        phi = frame["Phi"].to_numpy(dtype=float)
        wrapped = (phi + float(elevation_delta) + 90.0) % 180.0 - 90.0
        frame["Phi"] = wrapped
        if "E1" in frame.columns:
            frame["E1"] = wrapped
    return frame
