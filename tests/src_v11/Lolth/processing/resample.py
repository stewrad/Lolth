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
    required = {"Freq", "Phi", "Theta", "PdB"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Angular resampling requires {sorted(required)}")
    columns = [x for x in ("I","Q","PdB") if x in frame.columns]
    out = []
    for (frequency, polarization), group in frame.groupby(["Freq", "P"], sort=False):
        tmin, tmax = group["Theta"].min(),group["Theta"].max()
        pmin, pmax = group["Phi"].min(),group["Phi"].max()
        theta_target = np.arange(np.ceil(tmin / step)*step, np.floor(tmax / step)*step+step*.01, step)
        phi_target = np.arange(np.ceil(pmin / step)*step, np.floor(pmax / step)*step+step*.01, step)
        # Each source contributes to integer-degree centers no farther than
        # half a degree along either axis. Integer-position samples contribute
        # once; half-integer samples contribute to both adjacent centers.
        src = group[["Theta", "Phi"] + columns].reset_index(drop=True)
        coords = src[["Theta", "Phi"]].to_numpy(dtype=float)
        target_low = np.floor(coords / step) * step
        target_high = np.ceil(coords / step) * step
        blocks = []
        for it in (0, 1):
            for ip in (0, 1):
                theta = (target_low if it == 0 else target_high)[:, 0]
                phi = (target_low if ip == 0 else target_high)[:, 1]
                valid = (np.abs(theta - coords[:, 0]) <= step / 2 + 1e-8) & (np.abs(phi - coords[:, 1]) <= step / 2 + 1e-8)
                if it == 1:
                    valid &= target_high[:, 0] != target_low[:, 0]
                if ip == 1:
                    valid &= target_high[:, 1] != target_low[:, 1]
                valid &= (theta >= theta_target[0]) & (theta <= theta_target[-1])
                valid &= (phi >= phi_target[0]) & (phi <= phi_target[-1])
                if np.any(valid):
                    block = src.loc[valid, columns].copy()
                    block["Theta"] = theta[valid]
                    block["Phi"] = phi[valid]
                    blocks.append(block)
        candidates = pd.concat(blocks, ignore_index=True)
        agg = candidates.groupby(["Theta","Phi"], as_index=False)[columns].median()
        agg.insert(0,"Freq",frequency)
        agg["P"] = polarization
        if "I" in agg and "Q" in agg:
            agg["PdB"] = 20*np.log10(np.maximum(np.hypot(agg["I"],agg["Q"]),1e-15))
        agg["E1"] = agg["Phi"]
        agg["A1"] = agg["Theta"]
        out.append(agg)
    return pd.concat(out, ignore_index=True) if out else frame.iloc[0:0].copy()
