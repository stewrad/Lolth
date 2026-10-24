
# plotters.py

import numpy as np
import pandas as pd


def plot_linear(ax, data, xlim=None, ylim=None):

    a_data, i_data, q_data, pdb_data = data

    ax.clear()
    ax.plot(a_data, pdb_data, linewidth=1.5)

    ax.set_xlabel("Angle (degrees)")
    ax.set_ylabel("Power (dB)")
    ax.set_title("Linear Plot")
    ax.grid(True)

    if xlim is not None:
        ax.set_xlim(*xlim)

    if ylim is not None:
        ax.set_ylim(*ylim)


def plot_polar(ax, data, rlim=None):

    theta_deg, i_data, q_data, gain_db = data

    ax.clear()

    ax.plot(
        np.deg2rad(theta_deg),
        gain_db,
        linewidth=2
    )

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.arange(0, 360, 30))

    if rlim is not None:
        ax.set_rlim(*rlim)
    else:
        rmin = np.floor(np.min(gain_db) / 10) * 10
        rmax = max(0, np.ceil(np.max(gain_db) / 10) * 10)

        if rmin == rmax:
            rmin -= 10

        ax.set_rlim(rmin, rmax)

    ax.grid(True)
    ax.set_title("Radiation Pattern")


def plot_heatmap(ax, rdata, cmap="viridis",
                 vmin=-80, vmax=0):

    theta = []
    phi = []
    power = []

    for _, row in rdata.iterrows():
        a_data, i_data, q_data, pdb_data = row["Data"]

        theta.extend([row["E1"]] * len(a_data))
        phi.extend(a_data)
        power.extend(pdb_data)

    hdf = pd.DataFrame({
        "Theta": theta,
        "Phi": phi,
        "Power": power
    })

    heatmap_df = hdf.pivot_table(
        index="Theta",
        columns="Phi",
        values="Power",
        aggfunc="mean"
    )

    ax.clear()

    mesh = ax.pcolormesh(
        heatmap_df.columns.to_numpy(),
        heatmap_df.index.to_numpy(),
        heatmap_df.to_numpy(),
        cmap=cmap,
        shading="auto",
        vmin=vmin,
        vmax=vmax
    )

    ax.set_xlabel("Phi (degrees)")
    ax.set_ylabel("Theta (degrees)")
    ax.set_title("RF Power Heatmap")

    return mesh

def plot_cdf():
    return 