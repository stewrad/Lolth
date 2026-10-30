import pandas as pd

def process_frequency_median(flat, selected, bandwidth, unit):
    """Process at selected center frequencies, preserving individual angular sweeps.

    Median is computed across frequencies, NOT with an angular median filter.
    A bandwidth of zero disables processing. Angular coordinates must coincide.
    """
    if not selected:
        return flat.iloc[0:0].copy()
    centers = flat.loc[flat["Freq"].isin(selected)].copy()
    if centers.empty or bandwidth <= 0:
        return centers
    outputs = []
    for center in sorted(set(selected)):
        target = centers.loc[centers["Freq"] == center].copy()
        if target.empty:
            continue
        width_mhz = bandwidth if unit == "MHz" else center * bandwidth / 100.0
        neighbors = flat.loc[(flat["Freq"] >= center - width_mhz / 2)
                             & (flat["Freq"] <= center + width_mhz / 2)]
        if neighbors.empty:
            outputs.append(target)
            continue
        median = (neighbors.groupby(["Phi", "Theta"], sort=False)["PdB"]
                  .median().rename("_median_power"))
        target = target.join(median, on=["Phi", "Theta"])
        target["PdB"] = target["_median_power"].fillna(target["PdB"])
        outputs.append(target.drop(columns=["_median_power"]))
    return pd.concat(outputs, ignore_index=True) if outputs else centers.iloc[0:0]
