import numpy as np

def cdf_statistics(values):
    arr = np.asarray(values, dtype=float)
    arr = np.sort(arr[np.isfinite(arr)])
    if not len(arr):
        return np.array([]), np.array([]), (np.nan, np.nan, np.nan)
    y = np.arange(1, len(arr) + 1, dtype=float) / len(arr)
    return arr, y, tuple(np.percentile(arr, [25,50,75]))
