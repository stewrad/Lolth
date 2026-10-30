"""Reversible angular display remapping; never changes the imported RF arrays.

The requested Az/El display convention uses an angle reversal about 180 degrees.
The horizontal axis is wrapped to 0..360 degrees, equivalent to MATLAB wrapTo360.
The vertical scan is reversed about 180 as well, rather than performing a
Cartesian rotation. Its resulting display range is 90..270 for -90..90 input.
"""
import numpy as np


def wrap_to_360(degrees):
    values = np.mod(np.asarray(degrees, dtype=float), 360.0)
    # Keep zero at zero including source angles representing full revolutions.
    return values


def scan_to_az_el(theta_deg, phi_deg):
    """Return flipped/wrapped display azimuth and vertical-angle coordinates.

    Theta/A1: -180..180 -> display Az = wrap360(180 - Theta)
    Phi/E1:   -90..90 -> display El = wrap360(180 - Phi)
    """
    return (wrap_to_360(180.0 - np.asarray(theta_deg, dtype=float)),
            wrap_to_360(180.0 - np.asarray(phi_deg, dtype=float)))
