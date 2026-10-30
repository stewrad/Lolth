"""2D Matplotlib rendering methods mixed into the main window."""
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QMessageBox
from ..processing.cdf import cdf_statistics
from .coordinates import scan_to_az_el

class PlotMixin:
    def plot_coordinate_labels(self):
        """Axis labels corresponding to raw scan angles or converted Az/El."""
        return (("Theta", "Phi") if self.plot_phi_theta.isChecked()
                else ("Azimuth", "Elevation"))

    @staticmethod
    def draw_message(canvas, message):
        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.text(.5, .5, message, transform=ax.transAxes, ha="center", va="center", wrap=True)
        ax.axis("off")
        canvas.draw_idle()


    @staticmethod
    def split_theta_sweeps(data):
        if data.empty:
            return []
        theta = data["Theta"].to_numpy(dtype=float)
        split = np.where(np.diff(theta) < -180)[0] + 1
        return [data.iloc[idx] for idx in np.split(np.arange(len(data)), split) if len(idx)]


    def update_heatmap_datasets(self):
        previous = self.heatmap_dataset_select.currentData()
        self.heatmap_dataset_select.blockSignals(True)
        self.heatmap_dataset_select.clear()
        for key, group in self.groups.items():
            self.heatmap_dataset_select.addItem(group["name"], key)
        index = self.heatmap_dataset_select.findData(previous)
        if index >= 0:
            self.heatmap_dataset_select.setCurrentIndex(index)
        self.heatmap_dataset_select.blockSignals(False)


    def update_plot(self, *_):
        """Allow native combo popups and button animations to close before rendering."""
        self._plot_timer.start()


    def _paint_selected_plot(self):
        kind = self.plot_select.currentText()
        self.cdf_overall_label.setVisible(kind == "CDF")
        self.heatmap_controls.setVisible(kind == "Heatmap")
        if kind == "CDF":
            self.plot_cdf()
        elif kind == "Heatmap":
            self.plot_heatmap()
        else:
            self.plot_overlay(polar=kind == "Polar Plot")


    def plot_heatmap(self):
        """Single-dataset Phi vs Theta heatmap for one selected frequency.

        With multiple selected frequencies, choose the first selected frequency
        present in this dataset. Repeated angular samples are median-aggregated.
        """
        canvas = self.heatmap_canvas
        self.stacklayout.setCurrentWidget(self.plot_pages[canvas])
        key = self.heatmap_dataset_select.currentData()
        if key not in self.groups:
            self.draw_message(canvas, "Load a dataset and select it for the heatmap.")
            return
        group = self.groups[key]
        data = self.filtered_data(group)
        if data.empty:
            self.draw_message(canvas, "No data matches the selected frequency and Phi filters.")
            return
        chosen_p = self.heatmap_p_select.currentText()
        data = data.loc[data["P"] == chosen_p]
        if data.empty:
            self.draw_message(canvas, f"No {chosen_p} measurements match selected filters.")
            return
        freq = float(np.min(data["Freq"].unique()))
        data = data.loc[data["Freq"] == freq]
        # Rows = Phi, columns = Theta; repeated angles use a median.
        grid = data.pivot_table(index="Phi", columns="Theta", values="PdB", aggfunc="median")
        if grid.empty:
            self.draw_message(canvas, "No heatmap samples available.")
            return
        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        theta_vals = grid.columns.to_numpy(dtype=float)
        phi_vals = grid.index.to_numpy(dtype=float)
        power = grid.to_numpy(dtype=float)
        if self.plot_phi_theta.isChecked():
            horizontal_points, vertical_points = theta_vals, phi_vals
        else:
            # Pure angular wrap/flip, NOT a spatial rotation or regridding.
            # Sort both transformed axes and reorder power accordingly.
            horizontal_points, vertical_points = scan_to_az_el(theta_vals, phi_vals)
            order_x = np.argsort(horizontal_points, kind="stable")
            order_y = np.argsort(vertical_points, kind="stable")
            horizontal_points = horizontal_points[order_x]
            vertical_points = vertical_points[order_y]
            power = power[np.ix_(order_y, order_x)]
        mesh = ax.pcolormesh(horizontal_points, vertical_points,
                             np.ma.masked_invalid(power),
                             shading="auto", cmap="viridis")
        fig.colorbar(mesh, ax=ax, label="Power (dB)")
        ax.set_title(f"{group['name']} | {freq:g} MHz | {chosen_p}")
        horizontal, vertical = self.plot_coordinate_labels()
        ax.set_xlabel(f"{horizontal} (degrees)")
        ax.set_ylabel(f"{vertical} (degrees)")
        fig.tight_layout()
        canvas.draw_idle()
        self.statusBar().showMessage(f"Heatmap: {group['name']} at {freq:g} MHz")


    def plot_overlay(self, polar=False):
        canvas = self.polar_canvas if polar else self.linear_canvas
        self.stacklayout.setCurrentWidget(self.plot_pages[canvas])
        active = [x for x in self.groups.values() if x["visible"]]
        if not active:
            self.draw_message(canvas, "Load datasets or enable dataset visibility.")
            return
        freqs, phis = self.selected_filters()
        if not freqs or not phis:
            self.draw_message(canvas, "Select at least one frequency and phi.")
            return
        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111, projection="polar" if polar else None)
        horizontal, vertical = self.plot_coordinate_labels()
        combos = [(f, p) for f in freqs for p in phis]
        styles = {fp: self.line_styles[i % len(self.line_styles)] for i, fp in enumerate(combos)}
        curves = 0
        for group in active:
            filtered = self.filtered_data(group)
            if filtered.empty:
                continue
            for (freq, pol, phi), subset in filtered.groupby(["Freq", "P", "Phi"], sort=False):
                for sweep_index, sweep in enumerate(self.split_theta_sweeps(subset)):
                    theta = sweep["Theta"].to_numpy(dtype=float)
                    value = sweep["PdB"].to_numpy(dtype=float)
                    if self.plot_phi_theta.isChecked():
                        x_values = theta
                    else:
                        x_values, _ = scan_to_az_el(theta, np.full_like(theta, phi))
                    # The angular flip reverses sweep order; sort each portion
                    # before plotting and avoid crossing the 0/360 seam.
                    x_values = np.asarray(x_values, dtype=float).copy()
                    jumps = np.flatnonzero(np.abs(np.diff(x_values)) > 180) + 1
                    for segment in np.split(np.arange(len(x_values)), jumps):
                        if not len(segment):
                            continue
                        segment = segment[np.argsort(x_values[segment])]
                        ax.plot(np.deg2rad(x_values[segment]) if polar else x_values[segment],
                            value[segment],
                            color=group["color"], linestyle=styles.get((freq, phi), "-"),
                            linewidth=1.5, alpha=.85,
                            label=(f"{group['name']} | {freq:g} MHz, {pol}, Phi cut={phi:g}°"
                                   if sweep_index == 0 and segment[0] == 0 else "_nolegend_"))
                    curves += 1
        if not curves:
            self.draw_message(canvas, "No data matches selected filters.")
            return
        if polar:
            ax.set_title(f"Polar Radiation Pattern ({horizontal}/{vertical})", pad=20)
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)
            ax.set_rlim(-80, 0)
            ax.set_rlabel_position(225)
        else:
            ax.set_title(f"Linear Radiation Pattern ({horizontal}/{vertical})")
            ax.set_xlabel(f"{horizontal} (degrees)")
            ax.set_ylabel("Power (dB)")
            ax.set_xlim((-180, 180) if self.plot_phi_theta.isChecked() else (0, 360))
            ax.set_ylim(-80, 0)
        ax.grid(True, alpha=.35)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize="small")
        fig.tight_layout()
        canvas.draw_idle()
        self.statusBar().showMessage(f"Displaying {curves} angular sweeps from {len(active)} datasets")


    def plot_cdf(self):
        """CDF of |test-synthetic|; overlay per-curve P75 quantile envelope."""
        canvas = self.cdf_canvas
        self.stacklayout.setCurrentWidget(self.plot_pages[canvas])
        self.cdf_plot_data = pd.DataFrame()
        self.cdf_summary = pd.DataFrame()
        self.cdf_overall_p75 = None
        self.cdf_overall_label.setText("Overall |ΔdB| P75: —")
        self.cdf_overall_label.show()
        test, synthetic = self.selected_pair()
        if test is None or synthetic is None:
            self.draw_message(canvas, "Assign one dataset as Test and another as Synthetic for CDF.")
            return
        left, right = self.filtered_data(test), self.filtered_data(synthetic)
        if left.empty or right.empty:
            self.draw_message(canvas, "No selected frequency/phi samples for the CDF pair.")
            return
        keys = ["Freq", "P", "Phi", "Theta"]
        left = left.groupby(keys, as_index=False)["PdB"].median().rename(columns={"PdB": "test_db"})
        right = right.groupby(keys, as_index=False)["PdB"].median().rename(columns={"PdB": "synthetic_db"})
        paired = left.merge(right, on=keys, how="inner")
        if paired.empty:
            self.draw_message(canvas, "No matching frequency / phi / theta samples.")
            return
        paired["signed_delta_db"] = paired["test_db"] - paired["synthetic_db"]
        paired["delta_db"] = paired["signed_delta_db"].abs()
        self.cdf_paired = paired
        all_deltas = paired["delta_db"].to_numpy(dtype=float)
        overall_p75 = float(np.percentile(all_deltas, 75))
        x_max = max(3.5, float(np.max(all_deltas)) * 1.05)
        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.axvspan(0, 3, ymin=0, ymax=1, facecolor="#ccead1", alpha=.78, zorder=0)
        ax.fill_between([3, x_max], 0, .75, color="#fff0af", alpha=.82, zorder=0)
        ax.fill_between([3, x_max], .75, 1, color="#f5c5c5", alpha=.82, zorder=0)
        ax.axvline(3, color="black", linestyle=":", linewidth=1.3, zorder=3)
        ax.hlines(.75, 3, x_max, color="black", linestyle=":", linewidth=1.3, zorder=3)
        _, vertical = self.plot_coordinate_labels()
        summary, export_curves, per_curve_arrays = [], [], []
        # A shared probability grid lets the P75 curve follow the other CDFs.
        probability_grid = np.linspace(0, 1, 501)
        for (freq, pol, phi), subset in paired.groupby(["Freq", "P", "Phi"], sort=True):
            x, y, (p25, p50, p75) = cdf_statistics(subset["delta_db"])
            if len(x) == 0:
                continue
            label = f"{test['name']} vs {synthetic['name']} | {freq:g} MHz, {pol}, {vertical}={phi:g}°"
            line, = ax.step(x, y, where="post", linewidth=1.6, zorder=4, label=label)
            for prob, value, marker in ((.25, p25, "o"), (.5, p50, "s"), (.75, p75, "^")):
                ax.plot(value, prob, marker=marker, color=line.get_color(), markersize=4,
                        linestyle="None", zorder=5)
            summary.append({"Freq": freq, "P": pol, "Phi": phi, "Count": len(subset),
                            "P25": p25, "P50": p50, "P75": p75})
            export_curves.append(pd.DataFrame({"Curve": label, "P": pol, "Freq_MHz": freq,
                                               "Phi_deg": phi, "Abs_Delta_dB": x,
                                               "Cumulative_Probability": y,
                                               "Curve_P75_dB": p75}))
            per_curve_arrays.append(np.quantile(subset["delta_db"].to_numpy(dtype=float),
                                                  probability_grid))
        if not per_curve_arrays:
            self.draw_message(canvas, "No CDF curves could be generated.")
            return
        # At each probability, calculate the 75th percentile of the individual
        # curve quantiles. This is a CDF-shaped aggregate, not a fixed-x line.
        p75_trace = np.percentile(np.vstack(per_curve_arrays), 75, axis=0)
        ax.plot(p75_trace, probability_grid, color="black", linewidth=2.7,
                zorder=12, label="P75 across plotted CDF curves")
        export_curves.append(pd.DataFrame({
            "Curve": "P75 across plotted CDF curves", "P": "All", "Freq_MHz": np.nan,
            "Phi_deg": np.nan, "Abs_Delta_dB": p75_trace,
            "Cumulative_Probability": probability_grid,
            "Curve_P75_dB": np.nan}))
        ax.set_title(f"Absolute Power Difference CDF: {test['name']} vs {synthetic['name']}")
        ax.set_xlabel("Absolute power difference |Test − Synthetic| (dB)")
        ax.set_ylabel("Cumulative Probability")
        ax.set_xlim(0, x_max)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=.18, zorder=1)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize="small")
        fig.tight_layout()
        canvas.draw_idle()
        self.cdf_summary = pd.DataFrame(summary)
        self.cdf_plot_data = pd.concat(export_curves, ignore_index=True)
        self.cdf_overall_p75 = overall_p75
        self.cdf_overall_label.setText(f"Overall |ΔdB| P75: {overall_p75:.3f} dB")
        self.statusBar().showMessage(
            f"CDF: {len(paired):,} matches, {len(summary)} curves, overall |ΔdB| P75 = {overall_p75:.2f} dB")

