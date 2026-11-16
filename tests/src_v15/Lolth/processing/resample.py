"""Angular 2x reduction by median over each 0.5-degree neighborhood."""
import numpy as np
import pandas as pd

def resample_angular_median(frame, step=1.0):
    """Return integer-degree angular centers; median I and Q within ±0.5°.

    For a 0.5° source grid this forms overlapping 3x3 neighborhoods. The
    target center point participates with its immediate half-degree neighbors.
    Recompute PdB from median I/Q to keep complex magnitude consistent.
    If complex samples are missing, use median PdB instead.
    """
    required = {"Freq", "Theta", "Phi", "PdB"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Angular resampling requires {sorted(required)}")
    columns = [x for x in ("I","Q","PdB") if x in frame.columns]
    out = []
    for (frequency, polarization), group in frame.groupby(["Freq", "P"], sort=False):
        tmin, tmax = group["Phi"].min(),group["Phi"].max()
        pmin, pmax = group["Theta"].min(),group["Theta"].max()
        phi_target = np.arange(np.ceil(tmin / step)*step, np.floor(tmax / step)*step+step*.01, step)
        theta_target = np.arange(np.ceil(pmin / step)*step, np.floor(pmax / step)*step+step*.01, step)
        # Each source contributes to integer-degree centers no farther than
        # half a degree along either axis. Integer-position samples contribute
        # once; half-integer samples contribute to both adjacent centers.
        src = group[["Phi", "Theta"] + columns].reset_index(drop=True)
        coords = src[["Phi", "Theta"]].to_numpy(dtype=float)
        target_low = np.floor(coords / step) * step
        target_high = np.ceil(coords / step) * step
        blocks = []
        for it in (0, 1):
            for ip in (0, 1):
                phi = (target_low if it == 0 else target_high)[:, 0]
                theta = (target_low if ip == 0 else target_high)[:, 1]
                valid = (np.abs(phi - coords[:, 0]) <= step / 2 + 1e-8) & (np.abs(theta - coords[:, 1]) <= step / 2 + 1e-8)
                if it == 1:
                    valid &= target_high[:, 0] != target_low[:, 0]
                if ip == 1:
                    valid &= target_high[:, 1] != target_low[:, 1]
                valid &= (phi >= phi_target[0]) & (phi <= phi_target[-1])
                valid &= (theta >= theta_target[0]) & (theta <= theta_target[-1])
                if np.any(valid):
                    block = src.loc[valid, columns].copy()
                    block["Phi"] = phi[valid]
                    block["Theta"] = theta[valid]
                    blocks.append(block)
        candidates = pd.concat(blocks, ignore_index=True)
        agg = candidates.groupby(["Phi","Theta"], as_index=False)[columns].median()
        agg.insert(0,"Freq",frequency)
        agg["P"] = polarization
        if "I" in agg and "Q" in agg:
            agg["PdB"] = 20*np.log10(np.maximum(np.hypot(agg["I"],agg["Q"]),1e-15))
        agg["E1"] = agg["Theta"]
        agg["A1"] = agg["Phi"]
        out.append(agg)
    return pd.concat(out, ignore_index=True) if out else frame.iloc[0:0].copy()
