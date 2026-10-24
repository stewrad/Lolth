
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import file_loader as fl
from cdf import flatten_rf, compare_db, cdf_statistics

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT,
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("RF Dataset Comparison")
        # self.resize(1400, 850)

        self.last_dir = Path.cwd()

        # Dataset names are editable.
        # Internal keys remain fixed.
        self.groups = {
            "test": {
                "name": "Test Data",
                "paths": [],
                "data": None,
                "flat": None,
            },
            "synth": {
                "name": "Synthetic Data",
                "paths": [],
                "data": None,
                "flat": None,
            },
        }

        # Consistent colors between plot types.
        self.dataset_colors = {
            "test": "tab:blue",
            "synth": "tab:orange",
        }

        # Different line styles for different
        # frequency / phi combinations.
        self.line_styles = [
            "-",
            "--",
            "-.",
            ":",
        ]

        self.group_widgets = {}

        self.freq_checks = {}
        self.phi_checks = {}

        self._build_menu()
        self._build_ui()

        self.plot_select.currentTextChanged.connect(
            self.update_plot
        )

        self.update_plot()

    # ==================================================
    # MENU
    # ==================================================

    def _build_menu(self):

        file_menu = self.menuBar().addMenu("&File")

        actions = [
            (
                "Load Test Data",
                "test",
                "Ctrl+O",
            ),
            (
                "Load Synthetic Data",
                "synth",
                "Ctrl+Shift+O",
            ),
        ]

        for label, key, shortcut in actions:

            action = QAction(label, self)
            action.setShortcut(shortcut)

            action.triggered.connect(
                lambda checked=False, k=key:
                self.open_file(k)
            )

            file_menu.addAction(action)

    # ==================================================
    # MAIN UI
    # ==================================================

    def _build_ui(self):

        root = QHBoxLayout()

        # ----------------------------------------------
        # Left panel
        # ----------------------------------------------

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.setSpacing(10)

        # Dataset management
        self._add_group_editor(
            left_layout,
            "test",
            "Dataset 1",
        )

        self._add_group_editor(
            left_layout,
            "synth",
            "Dataset 2",
        )

        # ----------------------------------------------
        # Plot type
        # ----------------------------------------------

        left_layout.addWidget(
            QLabel("Plot Type")
        )

        self.plot_select = QComboBox()

        self.plot_select.addItems([
            "Linear Plot",
            "Polar Plot",
            "CDF",
        ])

        left_layout.addWidget(self.plot_select)

        # ----------------------------------------------
        # Shared frequency selection
        # ----------------------------------------------

        left_layout.addWidget(
            QLabel("Frequency Selection")
        )

        (
            self.freq_check_layout,
            freq_area,
        ) = self._create_checkbox_area()

        left_layout.addWidget(freq_area)

        # ----------------------------------------------
        # Shared phi selection
        # ----------------------------------------------

        left_layout.addWidget(
            QLabel("Phi Selection")
        )

        (
            self.phi_check_layout,
            phi_area,
        ) = self._create_checkbox_area()

        left_layout.addWidget(phi_area)

        # ----------------------------------------------
        # Checkbox control buttons
        # ----------------------------------------------

        row = QHBoxLayout()

        select_all = QPushButton("Select All")

        select_all.clicked.connect(
            lambda: self.set_all_checks(True)
        )

        clear_all = QPushButton("Clear All")

        clear_all.clicked.connect(
            lambda: self.set_all_checks(False)
        )

        row.addWidget(select_all)
        row.addWidget(clear_all)

        left_layout.addLayout(row)

        # ----------------------------------------------
        # Selection status
        # ----------------------------------------------

        self.match_label = QLabel(
            "Load both datasets to identify "
            "common frequencies and phi values."
        )

        self.match_label.setWordWrap(True)

        left_layout.addWidget(self.match_label)

        left_layout.addStretch()

        # ----------------------------------------------
        # Scrollable left panel
        # ----------------------------------------------

        left_scroll = QScrollArea()

        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(left_panel)

        left_scroll.setMinimumWidth(320)
        left_scroll.setMaximumWidth(390)

        root.addWidget(left_scroll)

        # ----------------------------------------------
        # Plotting area
        # ----------------------------------------------

        self.stacklayout = QStackedLayout()

        self.linear_canvas = FigureCanvasQTAgg(
            Figure()
        )

        self.polar_canvas = FigureCanvasQTAgg(
            Figure()
        )

        self.cdf_canvas = FigureCanvasQTAgg(
            Figure()
        )

        self.plot_pages = {}
        self.toolbars = {}

        for canvas in (
            self.linear_canvas,
            self.polar_canvas,
            self.cdf_canvas,
        ):

            page = QWidget()
            layout = QVBoxLayout(page)

            layout.setContentsMargins(0, 0, 0, 0)

            toolbar = NavigationToolbar2QT(
                canvas,
                page,
            )

            layout.addWidget(toolbar)
            layout.addWidget(
                canvas,
                stretch=1,
            )

            self.plot_pages[canvas] = page
            self.toolbars[canvas] = toolbar

            self.stacklayout.addWidget(page)

        root.addLayout(
            self.stacklayout,
            stretch=1,
        )

        central = QWidget()
        central.setLayout(root)

        self.setCentralWidget(central)

    # ==================================================
    # DATASET GROUP MANAGEMENT
    # ==================================================

    def _add_group_editor(
        self,
        layout,
        key,
        title,
    ):

        group_box = QGroupBox(title)

        group_layout = QVBoxLayout(group_box)

        # Dataset name
        name_edit = QLineEdit(
            self.groups[key]["name"]
        )

        name_edit.textChanged.connect(
            lambda text, k=key:
            self.rename_group(k, text)
        )

        group_layout.addWidget(name_edit)

        # File list
        file_list = QListWidget()
        file_list.setMaximumHeight(85)

        group_layout.addWidget(file_list)

        # File buttons
        button_row = QHBoxLayout()

        add_button = QPushButton("Add Files")

        add_button.clicked.connect(
            lambda checked=False, k=key:
            self.open_file(k)
        )

        clear_button = QPushButton("Clear")

        clear_button.clicked.connect(
            lambda checked=False, k=key:
            self.clear_group(k)
        )

        button_row.addWidget(add_button)
        button_row.addWidget(clear_button)

        group_layout.addLayout(button_row)

        self.group_widgets[key] = {
            "name": name_edit,
            "files": file_list,
        }

        layout.addWidget(group_box)

    def rename_group(self, key, text):

        self.groups[key]["name"] = (
            text.strip()
            or (
                "Dataset 1"
                if key == "test"
                else "Dataset 2"
            )
        )

        self.update_plot()

    # ==================================================
    # FILE LOADING
    # ==================================================

    def open_file(self, group_id):

        paths, _ = QFileDialog.getOpenFileNames(
            self,
            f"Load {self.groups[group_id]['name']}",
            str(self.last_dir),
            "RF Data (*.txt *.pkl);;All Files (*)",
        )

        if paths:
            self.load_files(paths, group_id)

    def load_files(self, file_paths, group_id):

        group = self.groups[group_id]

        combined_paths = list(
            dict.fromkeys(
                group["paths"]
                + [str(p) for p in file_paths]
            )
        )

        try:

            data = fl.load_multiple(combined_paths)

            if data is None or data.empty:
                raise ValueError(
                    "The loader returned no data."
                )

            # Convert the nested RF dataset into
            # frequency, phi, theta, PdB samples.
            #
            # Cached so that every checkbox change
            # does not require re-flattening.
            flat = flatten_rf(
                data,
                group["name"],
            )

            group["paths"] = combined_paths
            group["data"] = data
            group["flat"] = flat

            self.last_dir = Path(
                combined_paths[-1]
            ).parent

            file_widget = (
                self.group_widgets[group_id]["files"]
            )

            file_widget.clear()

            for path in combined_paths:

                file_widget.addItem(
                    Path(path).name
                )

                file_widget.item(
                    file_widget.count() - 1
                ).setToolTip(path)

            self.populate_shared_selections()

            self.update_plot()

            self.statusBar().showMessage(
                f"{group['name']}: "
                f"{len(combined_paths)} files, "
                f"{len(flat):,} samples"
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "File Load Error",
                str(exc),
            )

    def clear_group(self, key):

        self.groups[key]["paths"] = []
        self.groups[key]["data"] = None
        self.groups[key]["flat"] = None

        self.group_widgets[key]["files"].clear()

        self.populate_shared_selections()
        self.update_plot()

    # ==================================================
    # CHECKBOX CONTAINERS
    # ==================================================

    def _create_checkbox_area(self):

        container = QWidget()
        layout = QVBoxLayout(container)

        layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        layout.setContentsMargins(4, 4, 4, 4)

        area = QScrollArea()
        area.setWidgetResizable(True)

        area.setMinimumHeight(100)
        area.setMaximumHeight(165)

        area.setWidget(container)

        return layout, area

    def _populate_checkboxes(
        self,
        layout,
        target,
        values,
        suffix,
    ):

        previous = {
            key: checkbox.isChecked()
            for key, checkbox in target.items()
        }

        while layout.count():

            item = layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        target.clear()

        for value in values:

            checkbox = QCheckBox(
                f"{value:g}{suffix}"
            )

            checkbox.setChecked(
                previous.get(value, True)
            )

            checkbox.stateChanged.connect(
                self.update_plot
            )

            layout.addWidget(checkbox)

            target[value] = checkbox

    # ==================================================
    # COMMON FREQUENCY / PHI SELECTION
    # ==================================================

    def populate_shared_selections(self):

        first = self.groups["test"]["flat"]
        second = self.groups["synth"]["flat"]

        frequencies = []
        phis = []

        if first is not None and second is not None:

            frequencies = sorted(
                set(first["Freq"].unique())
                & set(second["Freq"].unique())
            )

            phis = sorted(
                set(first["E1"].unique())
                & set(second["E1"].unique())
            )

            self.match_label.setText(
                f"Common selections:\n"
                f"{len(frequencies)} frequencies\n"
                f"{len(phis)} phi values"
            )

        else:

            self.match_label.setText(
                "Load both datasets to identify "
                "common frequencies and phi values."
            )

        self._populate_checkboxes(
            self.freq_check_layout,
            self.freq_checks,
            frequencies,
            " MHz",
        )

        self._populate_checkboxes(
            self.phi_check_layout,
            self.phi_checks,
            phis,
            "°",
        )

    def set_all_checks(self, enabled):

        for checkbox in (
            list(self.freq_checks.values())
            + list(self.phi_checks.values())
        ):

            checkbox.blockSignals(True)
            checkbox.setChecked(enabled)
            checkbox.blockSignals(False)

        self.update_plot()

    def selected_filters(self):

        frequencies = [
            freq
            for freq, checkbox
            in self.freq_checks.items()
            if checkbox.isChecked()
        ]

        phis = [
            phi
            for phi, checkbox
            in self.phi_checks.items()
            if checkbox.isChecked()
        ]

        return frequencies, phis

    # ==================================================
    # DATA FILTERING
    # ==================================================

    def filtered_data(self, group_id):
        """Filter a dataset using shared frequency/phi selections."""

        flat = self.groups[group_id]["flat"]

        if flat is None:
            return pd.DataFrame()

        frequencies, phis = self.selected_filters()

        if not frequencies or not phis:
            return flat.iloc[0:0].copy()

        return flat[
            flat["Freq"].isin(frequencies)
            & flat["Phi"].isin(phis)
        ].copy()

    # ==================================================
    # PLOT DISPATCHER
    # ==================================================

    def update_plot(self, *_):

        plot_type = self.plot_select.currentText()

        if plot_type == "Linear Plot":
            self.plot_overlay(polar=False)

        elif plot_type == "Polar Plot":
            self.plot_overlay(polar=True)

        elif plot_type == "CDF":
            self.plot_cdf()

    # ==================================================
    # EMPTY PLOT MESSAGES
    # ==================================================

    @staticmethod
    def draw_message(canvas, message):

        fig = canvas.figure
        fig.clear()

        ax = fig.add_subplot(111)

        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            transform=ax.transAxes,
            wrap=True,
        )

        ax.set_axis_off()

        canvas.draw_idle()

    # ==================================================
    # SPLIT REPEATED THETA SWEEPS
    # ==================================================

    @staticmethod
    def split_theta_sweeps(data):
        """
        Keep repeated angular sweeps separate.

        This prevents a line from connecting the end
        of one -180..180 sweep to the beginning of
        another sweep.

        The original input order is preserved.
        """

        if data.empty:
            return []

        theta = data["Theta"].to_numpy(dtype=float)

        # Detect resets across most of a full revolution.
        reset_indices = np.where(
            np.diff(theta) < -180
        )[0] + 1

        index_groups = np.split(
            np.arange(len(data)),
            reset_indices,
        )

        return [
            data.iloc[indices]
            for indices in index_groups
            if len(indices)
        ]

    # ==================================================
    # LINEAR / POLAR OVERLAY
    # ==================================================

    def plot_overlay(self, polar=False):
        """
        Overlay both datasets using:
            color = dataset
            linestyle = frequency/phi combination

        Shared frequency and phi checkboxes determine
        which curves are displayed.
        """

        canvas = (
            self.polar_canvas
            if polar
            else self.linear_canvas
        )

        self.stacklayout.setCurrentWidget(
            self.plot_pages[canvas]
        )

        first_data = self.groups["test"]["flat"]
        second_data = self.groups["synth"]["flat"]

        if first_data is None or second_data is None:

            self.draw_message(
                canvas,
                "Load both datasets to compare.",
            )

            return

        frequencies, phis = self.selected_filters()

        if not frequencies or not phis:

            self.draw_message(
                canvas,
                "Select at least one frequency and phi.",
            )

            return

        fig = canvas.figure
        fig.clear()

        if polar:
            ax = fig.add_subplot(
                111,
                projection="polar",
            )
        else:
            ax = fig.add_subplot(111)

        # All requested combinations receive the
        # same linestyle in both dataset groups.
        combinations = [
            (freq, phi)
            for freq in frequencies
            for phi in phis
        ]

        style_map = {
            combination:
            self.line_styles[
                i % len(self.line_styles)
            ]
            for i, combination in enumerate(combinations)
        }

        curves_drawn = 0

        # ----------------------------------------------
        # Plot each dataset
        # ----------------------------------------------

        for group_id in ("test", "synth"):

            group = self.groups[group_id]

            data = self.filtered_data(group_id)

            if data.empty:
                continue

            color = self.dataset_colors[group_id]

            # Group by frequency and phi so that
            # curves do not connect across either.
            for (freq, phi), subset in data.groupby(
                ["Freq", "E1"],
                sort=False,
            ):

                linestyle = style_map.get(
                    (freq, phi),
                    "-",
                )

                label = (
                    f"{group['name']} | "
                    f"{freq:g} MHz, "
                    f"φ={phi:g}°"
                )

                # More than one angular sweep can
                # exist within the same group.
                sweeps = self.split_theta_sweeps(subset)

                for sweep_index, sweep in enumerate(sweeps):

                    theta = sweep[
                        "Theta"
                    ].to_numpy(dtype=float)

                    power = sweep[
                        "PdB"
                    ].to_numpy(dtype=float)

                    if polar:

                        x = np.deg2rad(theta)

                    else:

                        x = theta

                    # Only one legend entry per
                    # dataset/frequency/phi combination.
                    curve_label = (
                        label
                        if sweep_index == 0
                        else "_nolegend_"
                    )

                    ax.plot(
                        x,
                        power,
                        color=color,
                        linestyle=linestyle,
                        linewidth=1.5,
                        alpha=0.85,
                        label=curve_label,
                    )

                    curves_drawn += 1

        if curves_drawn == 0:

            self.draw_message(
                canvas,
                "No data matches the selected filters.",
            )

            return

        # ----------------------------------------------
        # Plot formatting
        # ----------------------------------------------

        names = (
            f"{self.groups['test']['name']} vs "
            f"{self.groups['synth']['name']}"
        )

        if polar:

            ax.set_title(
                f"Polar Radiation Pattern\n{names}",
                pad=20,
            )

            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)

            ax.set_thetagrids(
                np.arange(0, 360, 30)
            )

            # Retain the original RF plot range.
            ax.set_rlim(-80, 0)

            ax.set_rlabel_position(225)

        else:

            ax.set_title(
                f"Linear Radiation Pattern\n{names}"
            )

            ax.set_xlabel("Theta (degrees)")
            ax.set_ylabel("Power (dB)")

            ax.set_xlim(-180, 180)
            ax.set_ylim(-80, 0)

        ax.grid(
            True,
            alpha=0.35,
        )

        ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.02, 1),
            fontsize="small",
        )

        fig.tight_layout()
        canvas.draw_idle()

        self.statusBar().showMessage(
            f"Displaying {curves_drawn} angular sweeps "
            f"from {len(combinations)} selected "
            f"frequency/phi combinations"
        )

    # ==================================================
    # CDF
    # ==================================================

    def plot_cdf(self):
        """
        Compare the two datasets by matching:
            Frequency
            Phi
            Theta

        Then compute:
            delta_dB = Dataset 1 - Dataset 2

        Plot empirical CDF for each selected
        frequency/phi combination.
        """

        canvas = self.cdf_canvas

        self.stacklayout.setCurrentWidget(
            self.plot_pages[canvas]
        )

        first = self.groups["test"]
        second = self.groups["synth"]

        if first["data"] is None or second["data"] is None:

            self.draw_message(
                canvas,
                "Load both datasets to calculate CDF.",
            )

            return

        frequencies, phis = self.selected_filters()

        if not frequencies or not phis:

            self.draw_message(
                canvas,
                "Select at least one frequency and phi.",
            )

            return

        try:

            paired = compare_db(
                first["data"],
                second["data"],
                frequencies,
                phis,
                first["name"],
                second["name"],
            )

        except Exception as exc:

            self.draw_message(
                canvas,
                f"CDF matching error:\n{exc}",
            )

            return

        if paired.empty:

            self.draw_message(
                canvas,
                "No matching frequency/phi/theta samples.",
            )

            return

        fig = canvas.figure
        fig.clear()

        ax = fig.add_subplot(111)

        # CDF colors distinguish frequency/phi curves.
        # Dataset names identify the comparison.
        summary = []

        for (freq, phi), subset in paired.groupby(
            ["Freq", "Phi"],
            sort=True,
        ):

            x, y, percentiles = cdf_statistics(
                subset["delta_db"]
            )

            p25, p50, p75 = percentiles

            label = (
                f"{first['name']} − {second['name']} | "
                f"{freq:g} MHz, φ={phi:g}°"
            )

            line, = ax.step(
                x,
                y,
                where="post",
                linewidth=1.8,
                label=label,
            )

            color = line.get_color()

            for probability, value, marker in (
                (0.25, p25, "o"),
                (0.50, p50, "s"),
                (0.75, p75, "^"),
            ):

                ax.plot(
                    value,
                    probability,
                    marker=marker,
                    color=color,
                    linestyle="None",
                    markersize=5,
                )

            summary.append({
                "Freq": freq,
                "E1": phi,
                "Count": len(x),
                "P25": p25,
                "P50": p50,
                "P75": p75,
            })

        # ----------------------------------------------
        # Plot formatting
        # ----------------------------------------------

        name_difference = (
            f"{first['name']} − {second['name']}"
        )

        ax.set_title(
            f"CDF of {name_difference}"
        )

        ax.set_xlabel(
            f"{name_difference} (dB)"
        )

        ax.set_ylabel(
            "Cumulative Probability"
        )

        ax.set_ylim(0, 1.02)

        ax.grid(
            True,
            alpha=0.35,
        )

        ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.02, 1),
            fontsize="small",
        )

        fig.tight_layout()
        canvas.draw_idle()

        # Save results for later export functionality.
        self.cdf_summary = pd.DataFrame(summary)
        self.cdf_paired = paired

        self.statusBar().showMessage(
            f"CDF: {len(paired):,} matched samples, "
            f"{len(summary)} frequency/phi curves"
        )


# ======================================================
# ENTRY POINT
# ======================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
