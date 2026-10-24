import sys
from pathlib import Path

import numpy as np
import pandas as pd

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT,
)

from cdf import compare_db, cdf_statistics

import file_loader as fl
from viz import plot_linear, plot_polar

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("RF Dataset Comparison / CDF")
        self.resize(1300, 800)

        self.last_dir = Path.cwd()

        # Internal group IDs remain fixed even when the display
        # names are modified by the user.
        self.groups = {
            "test": {
                "name": "Test Data",
                "paths": [],
                "data": None,
            },
            "synth": {
                "name": "Synthetic Data",
                "paths": [],
                "data": None,
            },
        }

        self.group_widgets = {}
        self.rdata = None

        # ----------------------------------------------
        # File menu
        # ----------------------------------------------

        file_menu = self.menuBar().addMenu("&File")

        for group_id, caption, shortcut in (
            ("test", "Add files to first dataset", "Ctrl+O"),
            ("synth", "Add files to second dataset", "Ctrl+Shift+O"),
        ):
            action = QAction(caption, self)
            action.setShortcut(shortcut)

            action.triggered.connect(
                lambda _checked=False, key=group_id:
                self.open_file(key)
            )

            file_menu.addAction(action)

        # ----------------------------------------------
        # Main layouts
        # ----------------------------------------------

        root = QHBoxLayout()

        left = QFrame()
        left.setFrameShape(QFrame.Shape.StyledPanel)
        left.setMinimumWidth(295)
        left.setMaximumWidth(370)

        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(8)

        # Dataset groups
        for key in self.groups:
            self._add_group_editor(left_layout, key)

        # ----------------------------------------------
        # Plot selection
        # ----------------------------------------------

        left_layout.addWidget(QLabel("Plot type"))

        self.plot_select = QComboBox()

        self.plot_select.addItems([
            "Linear Plot",
            "Polar Plot",
            "CDF",
        ])

        left_layout.addWidget(self.plot_select)

        # ----------------------------------------------
        # Preview dataset
        # ----------------------------------------------

        left_layout.addWidget(
            QLabel("Preview dataset (linear / polar)")
        )

        self.preview_group = QComboBox()
        left_layout.addWidget(self.preview_group)

        # ----------------------------------------------
        # Preview frequency
        # ----------------------------------------------

        left_layout.addWidget(QLabel("Preview frequency"))

        self.freq_select = QComboBox()
        left_layout.addWidget(self.freq_select)

        # ----------------------------------------------
        # CDF frequency checkboxes
        # ----------------------------------------------

        left_layout.addWidget(
            QLabel("CDF frequency selection (common only)")
        )

        (
            self.freq_checks,
            self.freq_check_layout,
        ) = self._checkbox_area(left_layout)

        # ----------------------------------------------
        # CDF phi checkboxes
        # ----------------------------------------------

        left_layout.addWidget(
            QLabel("CDF phi selection (common only)")
        )

        (
            self.phi_checks,
            self.phi_check_layout,
        ) = self._checkbox_area(left_layout)

        # ----------------------------------------------
        # Select / clear checkboxes
        # ----------------------------------------------

        button_row = QHBoxLayout()

        select_all = QPushButton("Select all")
        select_all.clicked.connect(
            lambda: self._set_all_checks(True)
        )

        clear_all = QPushButton("Clear selections")
        clear_all.clicked.connect(
            lambda: self._set_all_checks(False)
        )

        button_row.addWidget(select_all)
        button_row.addWidget(clear_all)

        left_layout.addLayout(button_row)

        # Matching information
        self.match_label = QLabel(
            "Load both datasets to find matching "
            "frequencies and phi values."
        )

        self.match_label.setWordWrap(True)

        left_layout.addWidget(self.match_label)
        left_layout.addStretch(1)

        # ----------------------------------------------
        # Scrollable left panel
        # ----------------------------------------------

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left)

        scroll.setMinimumWidth(330)
        scroll.setMaximumWidth(390)

        root.addWidget(scroll)

        # ----------------------------------------------
        # Matplotlib canvases and toolbars
        # ----------------------------------------------

        self.stacklayout = QStackedLayout()

        self.linear_canvas = FigureCanvasQTAgg(Figure())
        self.polar_canvas = FigureCanvasQTAgg(Figure())
        self.cdf_canvas = FigureCanvasQTAgg(Figure())

        self.plot_pages = {}

        for canvas in (
            self.linear_canvas,
            self.polar_canvas,
            self.cdf_canvas,
        ):
            page = QWidget()
            page_layout = QVBoxLayout(page)

            page_layout.setContentsMargins(0, 0, 0, 0)

            toolbar = NavigationToolbar2QT(canvas, page)

            page_layout.addWidget(toolbar)
            page_layout.addWidget(canvas, stretch=1)

            self.plot_pages[canvas] = page
            self.stacklayout.addWidget(page)

        root.addLayout(self.stacklayout, stretch=1)

        widget = QWidget()
        widget.setLayout(root)

        self.setCentralWidget(widget)

        # ----------------------------------------------
        # Signals
        # ----------------------------------------------

        self.plot_select.currentTextChanged.connect(
            self.update_plot
        )

        self.preview_group.currentIndexChanged.connect(
            self._on_preview_group_changed
        )

        self.freq_select.currentIndexChanged.connect(
            self.update_plot
        )

        self._update_group_names()

        self._draw_message(
            self.linear_canvas,
            "Load data to begin"
        )

        self.update_plot()

    # ==================================================
    # DATASET GROUP EDITORS
    # ==================================================

    def _add_group_editor(self, layout, key):

        group_box = QGroupBox(
            "Dataset 1" if key == "test" else "Dataset 2"
        )

        group_layout = QVBoxLayout(group_box)

        # Editable dataset name
        name = QLineEdit(self.groups[key]["name"])
        name.setPlaceholderText("Display name")

        name.textChanged.connect(
            lambda _value, k=key: self._rename_group(k)
        )

        group_layout.addWidget(name)

        # Files belonging to this group
        files = QListWidget()
        files.setMaximumHeight(83)
        files.setToolTip("Files loaded into this group")

        group_layout.addWidget(files)

        row = QHBoxLayout()

        add_button = QPushButton("Add files...")

        add_button.clicked.connect(
            lambda _checked=False, k=key:
            self.open_file(k)
        )

        clear_button = QPushButton("Clear")

        clear_button.clicked.connect(
            lambda _checked=False, k=key:
            self.clear_group(k)
        )

        row.addWidget(add_button)
        row.addWidget(clear_button)

        group_layout.addLayout(row)

        self.group_widgets[key] = {
            "name": name,
            "files": files,
        }

        layout.addWidget(group_box)

    # ==================================================
    # CHECKBOX AREAS
    # ==================================================

    @staticmethod
    def _checkbox_area(layout):

        area = QScrollArea()
        area.setWidgetResizable(True)

        area.setMinimumHeight(90)
        area.setMaximumHeight(145)

        container = QWidget()
        content = QVBoxLayout(container)

        content.setContentsMargins(4, 4, 4, 4)
        content.setAlignment(Qt.AlignmentFlag.AlignTop)

        area.setWidget(container)
        layout.addWidget(area)

        return {}, content

    # ==================================================
    # RENAME GROUP
    # ==================================================

    def _rename_group(self, key):

        self.groups[key]["name"] = (
            self.group_widgets[key]["name"].text().strip()
            or (
                "Dataset 1"
                if key == "test"
                else "Dataset 2"
            )
        )

        self._update_group_names()
        self.update_plot()

    def _update_group_names(self):

        current = self.preview_group.currentData()

        self.preview_group.blockSignals(True)
        self.preview_group.clear()

        for key, group in self.groups.items():
            self.preview_group.addItem(
                group["name"],
                userData=key,
            )

        index = self.preview_group.findData(current)

        self.preview_group.setCurrentIndex(
            index if index >= 0 else 0
        )

        self.preview_group.blockSignals(False)

    # ==================================================
    # FILE LOADING
    # ==================================================

    def open_file(self, group_id="test"):

        paths, _ = QFileDialog.getOpenFileNames(
            self,
            f"Add files to {self.groups[group_id]['name']}",
            str(self.last_dir),
            "Data Files (*.txt *.pkl);;All Files (*)",
        )

        if paths:
            self.load_files(paths, group_id)

    def load_file(self, path, group_id="test"):
        self.load_files([path], group_id)

    def load_files(self, file_paths, group_id="test"):
        """Load files into one dataset group."""

        if group_id not in self.groups:
            raise ValueError(f"Unknown group: {group_id}")

        existing = self.groups[group_id]["paths"]

        combined_paths = list(
            dict.fromkeys([
                *existing,
                *(str(p) for p in file_paths),
            ])
        )

        try:
            data = fl.load_multiple(combined_paths)

            if data is None or data.empty:
                raise ValueError("No measurement data found")

            if (
                "Freq" not in data.columns
                or "Data" not in data.columns
            ):
                raise ValueError(
                    "Expected the loader to return "
                    "'Freq' and 'Data' columns"
                )

            self.groups[group_id]["paths"] = combined_paths
            self.groups[group_id]["data"] = data

            self.last_dir = Path(
                combined_paths[-1]
            ).parent

            widget = self.group_widgets[group_id]["files"]
            widget.clear()

            for path in combined_paths:
                widget.addItem(Path(path).name)

                widget.item(
                    widget.count() - 1
                ).setToolTip(path)

            self._refresh_controls()

            self.statusBar().showMessage(
                f"{self.groups[group_id]['name']}: "
                f"{len(combined_paths)} files, "
                f"{len(data)} rows"
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

        self.group_widgets[key]["files"].clear()

        self._refresh_controls()

    def _on_preview_group_changed(self, *_):

        self.populate_frequencies()
        self.update_plot()

    def _refresh_controls(self):

        self.populate_frequencies()
        self.populate_match_checkboxes()
        self.update_plot()

    def populate_frequencies(self):

        key = self.preview_group.currentData()

        data = (
            self.groups[key]["data"]
            if key
            else None
        )

        prior = self.freq_select.currentData()

        self.freq_select.blockSignals(True)
        self.freq_select.clear()

        if data is not None:

            for freq in self._unique(data, "Freq"):

                self.freq_select.addItem(
                    f"{self._fmt(freq)} MHz",
                    userData=freq,
                )

            idx = self.freq_select.findData(prior)

            if idx >= 0:
                self.freq_select.setCurrentIndex(idx)

        self.freq_select.blockSignals(False)

    @staticmethod
    def _unique(data, column):

        if data is None or column not in data.columns:
            return []

        values = (
            data[column]
            .dropna()
            .unique()
            .tolist()
        )

        try:
            return sorted(values, key=float)

        except (TypeError, ValueError):
            return sorted(values, key=str)

    @staticmethod
    def _fmt(value):

        if isinstance(value, (int, float, np.number)):
            return f"{value:g}"

        return str(value)

    @staticmethod
    def _phi_column(data):
        """Identify the phi metadata column."""

        if data is None:
            return None

        for name in ("Phi", "phi", "AA", "P1"):
            if name in data.columns:
                return name

        return None

    def _populate_checkbox_list(
        self,
        layout,
        target,
        values,
        previous,
        suffix="",
    ):

        while layout.count():
            child = layout.takeAt(0)

            if child.widget():
                child.widget().deleteLater()

        target.clear()

        for value in values:

            checkbox = QCheckBox(
                f"{self._fmt(value)}{suffix}"
            )

            checkbox.setChecked(
                previous.get(value, True)
            )

            checkbox.stateChanged.connect(
                self.update_plot
            )

            layout.addWidget(checkbox)
            target[value] = checkbox

    def populate_match_checkboxes(self):

        first = self.groups["test"]["data"]
        second = self.groups["synth"]["data"]

        old_freq = {
            k: cb.isChecked()
            for k, cb in self.freq_checks.items()
        }

        old_phi = {
            k: cb.isChecked()
            for k, cb in self.phi_checks.items()
        }

        frequencies = []
        phis = []

        note = (
            "Load both datasets to find "
            "common selections."
        )

        if first is not None and second is not None:

            frequencies = sorted(
                set(self._unique(first, "Freq"))
                & set(self._unique(second, "Freq")),
                key=str,
            )

            try:
                frequencies.sort(key=float)

            except (TypeError, ValueError):
                pass

            first_phi_col = self._phi_column(first)
            second_phi_col = self._phi_column(second)

            if first_phi_col and second_phi_col:

                phis = list(
                    set(self._unique(first, first_phi_col))
                    & set(self._unique(second, second_phi_col))
                )

                try:
                    phis.sort(key=float)

                except (TypeError, ValueError):
                    phis.sort(key=str)

                note = (
                    f"Common: {len(frequencies)} frequencies, "
                    f"{len(phis)} phi values. "
                    f"Phi columns: "
                    f"{first_phi_col} / {second_phi_col}."
                )

            else:
                note = (
                    "Frequency matching available, "
                    "but phi metadata column was "
                    "not found in both datasets."
                )

        self._populate_checkbox_list(
            self.freq_check_layout,
            self.freq_checks,
            frequencies,
            old_freq,
            " MHz",
        )

        self._populate_checkbox_list(
            self.phi_check_layout,
            self.phi_checks,
            phis,
            old_phi,
            "°",
        )

        self.match_label.setText(note)

    def _set_all_checks(self, state):

        for cb in (
            *self.freq_checks.values(),
            *self.phi_checks.values(),
        ):
            cb.blockSignals(True)
            cb.setChecked(state)
            cb.blockSignals(False)

        self.update_plot()

    def selected_cdf_filters(self):
        """Return the selected CDF frequencies and phi values."""

        return {
            "frequencies": [
                key
                for key, cb in self.freq_checks.items()
                if cb.isChecked()
            ],
            "phis": [
                key
                for key, cb in self.phi_checks.items()
                if cb.isChecked()
            ],
        }

    def update_plot(self, *_):

        plot = self.plot_select.currentText()

        if plot == "Linear Plot":

            self._plot_existing(
                self.linear_canvas,
                "linear",
            )

        elif plot == "Polar Plot":

            self._plot_existing(
                self.polar_canvas,
                "polar",
            )

        elif plot == "CDF":

            self.plot_cdf()

    @staticmethod
    def _draw_message(canvas, message):

        figure = canvas.figure
        figure.clear()

        ax = figure.add_subplot(111)

        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            wrap=True,
            transform=ax.transAxes,
        )

        ax.set_axis_off()

        canvas.draw_idle()

    def _plot_existing(self, canvas, mode):

        self.stacklayout.setCurrentWidget(
            self.plot_pages[canvas]
        )

        key = self.preview_group.currentData()

        data = (
            self.groups[key]["data"]
            if key
            else None
        )

        freq = self.freq_select.currentData()

        if data is None or freq is None:

            self._draw_message(
                canvas,
                "Choose a dataset and frequency to preview",
            )

            return

        selected_rows = data[
            data["Freq"] == freq
        ]

        if selected_rows.empty:

            self._draw_message(
                canvas,
                "No data at the selected frequency",
            )

            return

        # Preserve original preview behavior.
        # Use the first row at the selected frequency.
        nested_data = (
            selected_rows.iloc[0]["Data"]
        )

        self.rdata = data

        fig = canvas.figure
        fig.clear()

        ax = fig.add_subplot(
            111,
            projection=(
                "polar"
                if mode == "polar"
                else None
            ),
        )

        try:

            if mode == "linear":

                plot_linear(
                    ax,
                    nested_data,
                    xlim=(-180, 180),
                    ylim=(-80, 0),
                )

            else:

                plot_polar(
                    ax,
                    nested_data,
                    rlim=(-80, 0),
                )

            fig.tight_layout()
            canvas.draw_idle()

        except Exception as exc:

            self._draw_message(
                canvas,
                f"Preview plot failed: {exc}",
            )

    def plot_cdf(self):
        """Plot directional dB-difference ECDFs."""

        canvas = self.cdf_canvas

        self.stacklayout.setCurrentWidget(
            self.plot_pages[canvas]
        )

        first = self.groups["test"]
        second = self.groups["synth"]

        if (
            first["data"] is None
            or second["data"] is None
        ):

            self._draw_message(
                canvas,
                "Load both datasets to compare",
            )

            return

        filters = self.selected_cdf_filters()

        if (
            not filters["frequencies"]
            or not filters["phis"]
        ):

            self._draw_message(
                canvas,
                "Select at least one common frequency and phi",
            )

            return

        try:

            paired = compare_db(
                first["data"],
                second["data"],
                filters["frequencies"],
                filters["phis"],
                first["name"],
                second["name"],
            )

        except (ValueError, KeyError, TypeError) as exc:

            self._draw_message(
                canvas,
                f"CDF matching error:\n{exc}",
            )

            self.statusBar().showMessage(
                str(exc)
            )

            return

        if paired.empty:

            self._draw_message(
                canvas,
                "No samples matched by frequency, "
                "phi, and theta",
            )

            return

        fig = canvas.figure
        fig.clear()

        ax = fig.add_subplot(111)

        summary = []

        for (freq, phi), portion in paired.groupby(
            ["Freq", "Phi"],
            sort=True,
        ):

            x, y, (p25, p50, p75) = (
                cdf_statistics(
                    portion["delta_db"]
                )
            )

            # Editable names appear in the legend.
            label = (
                f"{first['name']} − {second['name']} | "
                f"{freq:g} MHz, "
                f"φ={phi:g}° "
                f"(n={len(x)})"
            )

            line, = ax.step(
                x,
                y,
                where="post",
                linewidth=1.8,
                label=label,
            )

            color = line.get_color()

            for percentile, value, marker in (
                (0.25, p25, "o"),
                (0.50, p50, "s"),
                (0.75, p75, "^"),
            ):

                ax.plot(
                    value,
                    percentile,
                    marker=marker,
                    color=color,
                    markersize=5,
                    linestyle="None",
                )

            summary.append(
                f"{freq:g} MHz, "
                f"φ={phi:g}°: "
                f"P25={p25:.2f}, "
                f"P50={p50:.2f}, "
                f"P75={p75:.2f} dB"
            )

        ax.set_title(
            f"CDF: {first['name']} − {second['name']}"
        )

        ax.set_xlabel(
            f"{first['name']} − {second['name']} (dB)"
        )

        ax.set_ylabel("Cumulative probability")

        ax.set_ylim(0, 1.02)

        ax.grid(
            True,
            alpha=0.3,
        )

        ax.legend(
            loc="best",
            fontsize="small",
        )

        fig.tight_layout()
        canvas.draw_idle()

        self.statusBar().showMessage(
            f"{len(paired):,} matched samples across "
            f"{len(summary)} curves | "
            + " | ".join(summary[:2])
            + (
                " | ..."
                if len(summary) > 2
                else ""
            )
        )

if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
