import numpy as np
import pandas as pd

PHI_COLUMNS = ("E1", "E2", "AA", "P1")
THETA_COLUMNS = ("Theta", "theta", "A1", "Angle", "angle")
DB_COLUMNS = ("PdB", "P_dB", "dB", "Gain_dB", "gain_db")


def _find_column(columns, options):
    return next((k for k in options if k in columns), None)


def _vectors(nested):
    if isinstance(nested, pd.DataFrame):
        tcol = _find_column(nested.columns, THETA_COLUMNS)
        pcol = _find_column(nested.columns, DB_COLUMNS)

        if tcol is None or pcol is None:
            raise ValueError(
                f"Nested Data needs theta and PdB columns; "
                f"found {list(nested.columns)}"
            )

        return nested[tcol].to_numpy(), nested[pcol].to_numpy()

    if isinstance(nested, dict):
        tcol = _find_column(nested, THETA_COLUMNS)
        pcol = _find_column(nested, DB_COLUMNS)

        if tcol is None or pcol is None:
            raise ValueError(
                f"Nested Data dict needs theta and PdB keys; "
                f"found {list(nested)}"
            )

        return nested[tcol], nested[pcol]

    if isinstance(nested, (tuple, list)) and len(nested) == 4:
        return nested[0], nested[3]

    raise ValueError(
        "Unsupported nested Data format. Expected DataFrame, "
        "dict, or (A1,I,Q,PdB)."
    )


def flatten_rf(frame, dataset_name):
    """Convert top-level RF rows into (Freq, Phi, Theta, PdB) samples."""

    if frame is None or frame.empty:
        raise ValueError(f"{dataset_name}: no data loaded")

    if not {"Freq", "Data"}.issubset(frame.columns):
        raise ValueError(
            f"{dataset_name}: top-level frame requires Freq and Data"
        )

    phi_col = _find_column(frame.columns, PHI_COLUMNS)

    if phi_col is None:
        raise ValueError(
            f"{dataset_name}: could not find top-level phi field "
            f"(one of {PHI_COLUMNS}). "
            f"Present columns: {list(frame.columns)}. "
            "Phi should describe the whole nested sweep, "
            "not each theta point."
        )

    blocks = []

    for idx, row in frame.iterrows():
        theta, power_db = _vectors(row["Data"])

        theta = np.asarray(theta).reshape(-1)
        power_db = np.asarray(power_db).reshape(-1)

        if theta.size != power_db.size:
            raise ValueError(
                f"{dataset_name}, row {idx}: "
                "theta and PdB lengths differ"
            )

        if theta.size == 0:
            continue

        blocks.append(
            pd.DataFrame({
                "Freq": [row["Freq"]] * theta.size,
                "Phi": [row[phi_col]] * theta.size,
                "Theta": theta,
                "PdB": power_db,
            })
        )

    if not blocks:
        raise ValueError(f"{dataset_name}: no nested samples")

    result = pd.concat(blocks, ignore_index=True)

    for column in ("Freq", "Phi", "Theta", "PdB"):
        result[column] = pd.to_numeric(
            result[column], errors="coerce"
        )

    return (
        result
        .replace([np.inf, -np.inf], np.nan)
        .dropna(subset=["Freq", "Phi", "Theta", "PdB"])
    )


def compare_db(
    test_frame,
    synth_frame,
    frequencies,
    phis,
    first_name="Test Data",
    second_name="Synthetic Data",
):
    """Pair directional measurements and calculate first minus second in dB.

    Returns DataFrame with:
        Freq, Phi, Theta, first_db, second_db, delta_db
    """

    if not frequencies or not phis:
        return pd.DataFrame(
            columns=[
                "Freq", "E1", "Theta",
                "first_db", "second_db", "delta_db"
            ]
        )

    first = flatten_rf(test_frame, first_name)
    second = flatten_rf(synth_frame, second_name)

    def apply_filters(data):
        return data[
            data.Freq.isin(frequencies)
            & data.Phi.isin(phis)
        ].copy()

    first = apply_filters(first)
    second = apply_filters(second)

    keys = ["Freq", "E1", "Theta"]

    # Pair repeated measurements one-to-one by occurrence
    # rather than generating a many-to-many cross-product.
    first["occurrence"] = (
        first.groupby(keys, sort=False).cumcount()
    )

    second["occurrence"] = (
        second.groupby(keys, sort=False).cumcount()
    )

    merged = first.merge(
        second,
        on=keys + ["occurrence"],
        how="inner",
        suffixes=("_first", "_second"),
        validate="one_to_one",
    )

    merged = merged.rename(
        columns={
            "PdB_first": "first_db",
            "PdB_second": "second_db",
        }
    )

    merged["delta_db"] = (
        merged["first_db"] - merged["second_db"]
    )

    return merged[
        [
            "Freq", "E1", "Theta",
            "first_db", "second_db", "delta_db"
        ]
    ]


def cdf_statistics(values):
    """Calculate empirical CDF and 25th, 50th, 75th percentiles."""

    x = np.sort(np.asarray(values, dtype=float))
    x = x[np.isfinite(x)]

    if not len(x):
        raise ValueError("No finite samples to calculate CDF")

    y = np.arange(1, len(x) + 1, dtype=float) / len(x)

    p25, p50, p75 = np.percentile(x, [25, 50, 75])

    return x, y, (p25, p50, p75)
