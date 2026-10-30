"""RF ingestion from measurement text, flat pickle, or legacy nested pickle.

Original scan names are always retained: E1 is the -90..90 scan (Phi),
A1 is the -180..180 scan (Theta). Plotting aliases are additive, optional.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd

FREQ_RE = re.compile(r"frequency\s+([0-9.eE+-]+)\s*(GHz|MHz|kHz|Hz)?", re.I)


def read_rf_text(path):
    records = []
    frequency = None
    with open(path, "r", encoding="utf8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            match = FREQ_RE.search(line)
            if match:
                value = float(match.group(1))
                unit = (match.group(2) or "MHz").lower()
                frequency = value * {"ghz": 1000, "mhz": 1, "khz": .001,
                                     "hz": 1e-6}[unit]
                continue
            parts = line.split()
            if len(parts) < 9 or parts[0].strip("\"'") != "A":
                continue
            if frequency is None:
                raise ValueError(f"{path}:{lineno} data row precedes frequency header")
            try:
                e1, a1 = float(parts[1]), float(parts[2])
                real, imag, power = map(float, parts[6:9])
            except (ValueError, IndexError):
                continue
            records.append((frequency, e1, a1, real, imag, power))
    if not records:
        raise ValueError(f"No RF records in {path}")
    frame = pd.DataFrame.from_records(records,
                                      columns=["Freq", "E1", "A1", "I", "Q", "PdB"])
    return normalized_flat(frame, str(path))


def _nested_measurements(obj, parent):
    """Flatten legacy Data cells while retaining row-level Freq/E1/P metadata."""
    if obj is None:
        return pd.DataFrame()
    if isinstance(obj, pd.DataFrame):
        inner = obj.copy()
    elif isinstance(obj, pd.Series):
        inner = obj.to_frame().T if not isinstance(obj.iloc[0], (list, tuple, np.ndarray)) else pd.DataFrame(obj.to_dict())
    elif isinstance(obj, dict):
        inner = pd.DataFrame(obj)
    else:
        array = np.asarray(obj)
        if array.ndim == 0:
            raise ValueError("Unsupported scalar Data field in legacy pickle")
        if array.ndim == 1:
            if len(array) and isinstance(array[0], (dict, pd.Series)):
                inner = pd.DataFrame(list(array))
            else:
                inner = pd.DataFrame({"PdBsm": array})
        elif array.ndim == 2:
            # Legacy file_loader.mread / nest_data stores each field in a
            # separate ROW: (4, N) = [A1, I, Q, PdBsm]. Modern flat inputs
            # may instead store one measurement per row: (N, 4).
            names = {3: ["A1", "I", "Q"],
                     4: ["A1", "I", "Q", "PdBsm"],
                     5: ["A1", "E1", "I", "Q", "PdBsm"]}
            rows, cols = array.shape
            if rows in names and cols not in names:
                inner = pd.DataFrame(array.T, columns=names[rows])
            elif cols in names and rows not in names:
                inner = pd.DataFrame(array, columns=names[cols])
            elif rows in names and cols in names:
                # Prefer the legacy field-per-row convention for small arrays.
                inner = pd.DataFrame(array.T, columns=names[rows])
            else:
                raise ValueError(f"Unsupported nested Data array shape {array.shape}")
        else:
            raise ValueError(f"Unsupported nested Data array shape {array.shape}")
    for key in ("Freq", "E1", "A1", "P", "File"):
        if key not in inner.columns and key in parent:
            inner[key] = [parent[key]] * len(inner)
    # The original nested reader can store per-point A1 under 'A1',
    # but if only per-row E1 and an angular sweep are supplied, retain both.
    return inner


def normalized_flat(frame, name="Dataset"):
    if not isinstance(frame, pd.DataFrame):
        raise ValueError(f"{name}: loader did not return a DataFrame")
    frame = frame.copy()
    if "Data" in frame.columns:
        pieces = [_nested_measurements(row["Data"], row)
                  for _, row in frame.iterrows()]
        frame = pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame()
    if "Freq" not in frame:
        for candidate in ("Frequency", "frequency"):
            if candidate in frame:
                frame["Freq"] = frame[candidate]
                break
    # Source schema takes precedence over any previously derived aliases.
    if "E1" in frame:
        frame["Phi"] = frame["E1"]
    elif "Phi" in frame:
        frame["E1"] = frame["Phi"]
    if "A1" in frame:
        frame["Theta"] = frame["A1"]
    elif "Theta" in frame:
        frame["A1"] = frame["Theta"]
    elif "theta" in frame:
        frame["Theta"] = frame["theta"]
        frame["A1"] = frame["theta"]
    if "PdB" not in frame and "PdBsm" in frame:
        frame["PdB"] = frame["PdBsm"]
    if "PdB" not in frame and "I" in frame and "Q" in frame:
        real = pd.to_numeric(frame["I"], errors="coerce")
        imag = pd.to_numeric(frame["Q"], errors="coerce")
        frame["PdB"] = 20 * np.log10(np.maximum(np.hypot(real, imag), 1e-15))
    required = ["Freq", "E1", "A1", "PdB"]
    missing = [k for k in required if k not in frame]
    if missing:
        raise ValueError(f"{name}: missing {missing}; available columns: {list(frame.columns)}")
    for col in required + ["Phi", "Theta"] + [x for x in ("I", "Q") if x in frame]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    return frame.dropna(subset=required).reset_index(drop=True)


def load_multiple(paths):
    frames = []
    for path in paths:
        path = Path(path)
        if path.suffix.lower() == ".txt":
            frames.append(read_rf_text(path))
        elif path.suffix.lower() == ".pkl":
            try:
                frames.append(normalized_flat(pd.read_pickle(path), str(path)))
            except (TypeError, NotImplementedError) as exc:
                raise ValueError(f"Cannot read {path.name} with the installed pandas version. "
                                 f"Try the pandas version used to save the pickle. Details: {exc}") from exc
        else:
            raise ValueError(f"Unsupported extension: {path.suffix}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
