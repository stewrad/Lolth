"""RF multi-dataset viewer. Requires: PyQt6, numpy, pandas, matplotlib,
plus the existing file_loader.py and cdf.py modules.

Frequency bandwidth median: for each selected center frequency, replace its
PdB values with the median of samples at the SAME (Phi, Theta) coordinates
within a full bandwidth window centered on the frequency. Bandwidth can be
specified in MHz or percent of the center frequency. The selected frequencies
are retained as the plot/CDF centers.
"""

import sys
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

import file_loader as fl
from cdf import flatten_rf, cdf_statistics

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QCheckBox, QGroupBox, QFileDialog,
    QMessageBox, QScrollArea, QVBoxLayout, QHBoxLayout, QStackedLayout,
    QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDoubleSpinBox, QColorDialog, QSplitter, QFormLayout,
)


def normalized_flat(frame, name):
    """Keep cdf.flatten_rf as the canonical adapter for the existing loader."""
    flat = flatten_rf(frame, name).copy()
    if "Phi" not in flat.columns and "E1" in flat.columns:
        flat["Phi"] = flat["E1"]
    if "E1" not in flat.columns and "Phi" in flat.columns:
        flat["E1"] = flat["Phi"]
    required = ("Freq", "Phi", "Theta", "PdB")
    missing = [key for key in required if key not in flat.columns]
    if missing:
        raise ValueError(f"Missing flattened columns: {missing}. Found {list(flat.columns)}")
    for key in required:
        flat[key] = pd.to_numeric(flat[key], errors="coerce")
    return flat.dropna(subset=list(required)).reset_index(drop=True)


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


class FrequencyPicker(QWidget):
    """Available (-) and included (+) frequencies in MHz."""
    def __init__(self, frequencies, parent=None):
        super().__init__(parent)
        self.available = QListWidget()
        self.included = QListWidget()
        self.available.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.included.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        for val in sorted(set(float(x) for x in frequencies)):
            self.included.addItem(self.make_item(val))
        row = QHBoxLayout(self)
        left = QVBoxLayout()
        left.addWidget(QLabel("Excluded"))
        left.addWidget(self.available)
        middle = QVBoxLayout()
        middle.addStretch()
        plus = QPushButton("+  Include")
        minus = QPushButton("−  Exclude")
        plus.clicked.connect(lambda: self.move(self.available, self.included))
        minus.clicked.connect(lambda: self.move(self.included, self.available))
        middle.addWidget(plus)
        middle.addWidget(minus)
        middle.addStretch()
        right = QVBoxLayout()
        right.addWidget(QLabel("Included (MHz)"))
        right.addWidget(self.included)
        row.addLayout(left, 1)
        row.addLayout(middle)
        row.addLayout(right, 1)
        self.setMinimumHeight(115)

    @staticmethod
    def make_item(freq):
        item = QListWidgetItem(f"{freq:g}")
        item.setData(Qt.ItemDataRole.UserRole, float(freq))
        return item

    def move(self, source, dest):
        for item in source.selectedItems():
            source.takeItem(source.row(item))
            dest.addItem(item)
        dest.sortItems()

    def selected_frequencies(self):
        return sorted(self.included.item(i).data(Qt.ItemDataRole.UserRole)
                      for i in range(self.included.count()))


class DatasetLoadDialog(QDialog):
    """One load popup: assign files to groups, scan them, and configure groups."""
    def __init__(self, paths, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Group and configure RF datasets")
        self.resize(940, 720)
        self.paths = list(dict.fromkeys(str(p) for p in paths))
        self.configs = {}
        self.result_groups = []
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Assign a dataset name to each file. Files with identical dataset names "
            "will be combined. Click 'Scan groups' to choose frequencies and median settings."
        ))
        self.assignment_table = QTableWidget(len(self.paths), 2)
        self.assignment_table.setHorizontalHeaderLabels(["Selected file", "Dataset group (editable)"])
        self.assignment_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.assignment_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for index, path in enumerate(self.paths):
            item = QTableWidgetItem(Path(path).name)
            item.setToolTip(path)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.assignment_table.setItem(index, 0, item)
            self.assignment_table.setCellWidget(index, 1, QLineEdit(Path(path).stem))
        self.assignment_table.setMaximumHeight(210)
        layout.addWidget(self.assignment_table)
        scan = QPushButton("Scan groups / refresh frequency options")
        scan.clicked.connect(self.scan_groups)
        layout.addWidget(scan)
        self.note = QLabel("Frequency controls will appear after scanning groups.")
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.config_container = QWidget()
        self.config_layout = QVBoxLayout(self.config_container)
        self.config_layout.addStretch()
        self.scroll.setWidget(self.config_container)
        layout.addWidget(self.scroll, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Add datasets")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def assignments(self):
        groups = {}
        for i, path in enumerate(self.paths):
            name = self.assignment_table.cellWidget(i, 1).text().strip()
            if not name:
                raise ValueError(f"Please enter a group name for {Path(path).name}.")
            groups.setdefault(name, []).append(path)
        return groups

    def scan_groups(self):
        try:
            groups = self.assignments()
            result = []
            for name, paths in groups.items():
                data = fl.load_multiple(paths)
                if data is None or data.empty:
                    raise ValueError(f"{name} returned no data")
                flat = normalized_flat(data, name)
                if flat.empty:
                    raise ValueError(f"{name} contains no valid samples")
                result.append(dict(name=name, paths=paths, data=data, raw=flat))
        except Exception as exc:
            QMessageBox.critical(self, "Scan error", str(exc))
            return
        while self.config_layout.count():
            child = self.config_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.configs = {}
        for entry in result:
            name = entry["name"]
            group_box = QGroupBox(f"{name}  —  {len(entry['paths'])} file(s), {len(entry['raw']):,} samples")
            form = QVBoxLayout(group_box)
            row = QHBoxLayout()
            toggle = QCheckBox("Apply frequency bandwidth median")
            value = QDoubleSpinBox()
            value.setRange(0, 1_000_000)
            value.setDecimals(4)
            value.setValue(0)
            unit = QComboBox()
            unit.addItems(["MHz", "%"])
            value.setEnabled(False)
            unit.setEnabled(False)
            toggle.toggled.connect(value.setEnabled)
            toggle.toggled.connect(unit.setEnabled)
            row.addWidget(toggle)
            row.addWidget(QLabel("Full bandwidth:"))
            row.addWidget(value)
            row.addWidget(unit)
            row.addStretch()
            form.addLayout(row)
            form.addWidget(QLabel("Choose center frequencies to include (+) or exclude (−):"))
            picker = FrequencyPicker(entry["raw"]["Freq"].unique())
            form.addWidget(picker)
            self.config_layout.addWidget(group_box)
            self.configs[name] = dict(entry=entry, toggle=toggle, value=value,
                                      unit=unit, picker=picker)
        self.config_layout.addStretch()
        self.note.setText(f"Scanned {len(result)} dataset group(s). Changes to group names "
                          "or assignments require scanning again.")

    def accept(self):
        try:
            assignments = self.assignments()
            if not self.configs or set(assignments) != set(self.configs) or any(
                assignments[n] != self.configs[n]["entry"]["paths"] for n in assignments
            ):
                raise ValueError("Click 'Scan groups' after editing file assignments.")
            output = []
            for name, controls in self.configs.items():
                selected = controls["picker"].selected_frequencies()
                if not selected:
                    raise ValueError(f"{name}: include at least one frequency.")
                entry = controls["entry"]
                bandwidth = controls["value"].value() if controls["toggle"].isChecked() else 0
                unit = controls["unit"].currentText()
                flat = process_frequency_median(entry["raw"], selected, bandwidth, unit)
                output.append(dict(id=uuid4().hex, name=name, paths=entry["paths"],
                                   data=entry["data"], raw=entry["raw"], flat=flat,
                                   frequencies=selected, bandwidth=bandwidth, unit=unit,
                                   visible=True, role="None"))
            self.result_groups = output
        except Exception as exc:
            QMessageBox.warning(self, "Dataset configuration", str(exc))
            return
        super().accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RF Dataset Comparison")
        self.resize(1480, 880)
        self.last_dir = Path.cwd()
        self.groups = {}  # Unlimited dataset count, stable UUID keys
        self.group_widgets = {}
        self.freq_checks = {}
        self.phi_checks = {}
        self.line_styles = ["-", "--", "-.", ":"]
        self.cdf_paired = pd.DataFrame()
        self.cdf_summary = pd.DataFrame()
        self._build_menu()
        self._build_ui()
        self.plot_select.currentTextChanged.connect(self.update_plot)
        self.update_plot()

    def _build_menu(self):
        menu = self.menuBar().addMenu("&File")
        action = QAction("Load and group files…", self)
        action.setShortcut("Ctrl+O")
        action.triggered.connect(self.open_files)
        menu.addAction(action)

    def _build_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_panel = QWidget()
        left = QVBoxLayout(left_panel)
        add = QPushButton("Load / Group Files…")
        add.clicked.connect(self.open_files)
        left.addWidget(add)
        left.addWidget(QLabel("Datasets (rename, recolor, show/hide, assign CDF roles):"))
        self.dataset_holder = QWidget()
        self.dataset_layout = QVBoxLayout(self.dataset_holder)
        self.dataset_layout.setContentsMargins(0, 0, 0, 0)
        left.addWidget(self.dataset_holder)
        left.addWidget(QLabel("Plot Type"))
        self.plot_select = QComboBox()
        self.plot_select.addItems(["Linear Plot", "Polar Plot", "CDF"])
        left.addWidget(self.plot_select)
        left.addWidget(QLabel("Frequency Selection (across loaded datasets)"))
        self.freq_check_layout, freq_area = self._create_checkbox_area()
        left.addWidget(freq_area)
        left.addWidget(QLabel("Phi Selection (across loaded datasets)"))
        self.phi_check_layout, phi_area = self._create_checkbox_area()
        left.addWidget(phi_area)
        row = QHBoxLayout()
        for label, on in (("Select All", True), ("Clear All", False)):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, value=on: self.set_all_checks(value))
            row.addWidget(button)
        left.addLayout(row)
        self.match_label = QLabel("Load datasets to begin.")
        self.match_label.setWordWrap(True)
        left.addWidget(self.match_label)
        left.addStretch()
        left_scroll.setWidget(left_panel)
        left_scroll.setMinimumWidth(365)
        splitter.addWidget(left_scroll)
        right = QWidget()
        self.stacklayout = QStackedLayout(right)
        self.plot_pages = {}
        self.toolbars = {}
        self.linear_canvas = FigureCanvasQTAgg(Figure())
        self.polar_canvas = FigureCanvasQTAgg(Figure())
        self.cdf_canvas = FigureCanvasQTAgg(Figure())
        for canvas in (self.linear_canvas, self.polar_canvas, self.cdf_canvas):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0)
            toolbar = NavigationToolbar2QT(canvas, page)
            layout.addWidget(toolbar)
            layout.addWidget(canvas, 1)
            self.plot_pages[canvas] = page
            self.toolbars[canvas] = toolbar
            self.stacklayout.addWidget(page)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([410, 1060])
        self.setCentralWidget(splitter)

    def open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select RF files", str(self.last_dir),
            "RF Data (*.txt *.pkl);;All Files (*)")
        if not paths:
            return
        popup = DatasetLoadDialog(paths, self)
        if popup.exec() != QDialog.DialogCode.Accepted:
            return
        self.last_dir = Path(paths[-1]).parent
        for group in popup.result_groups:
            palette = plt.get_cmap("tab20")
            rgb = palette(len(self.groups) % 20)
            group["color"] = QColor.fromRgbF(*rgb[:3]).name()
            self.groups[group["id"]] = group
            self._add_group_editor(group["id"])
        self.populate_shared_selections()
        self.update_plot()
        self.statusBar().showMessage(f"Added {len(popup.result_groups)} datasets")

    def _add_group_editor(self, key):
        group = self.groups[key]
        box = QGroupBox()
        outer = QVBoxLayout(box)
        row = QHBoxLayout()
        visible = QCheckBox()
        visible.setChecked(True)
        visible.setToolTip("Show dataset on linear and polar plots")
        visible.toggled.connect(lambda checked, k=key: self.set_visibility(k, checked))
        name_edit = QLineEdit(group["name"])
        name_edit.setToolTip("Editable dataset name")
        name_edit.textChanged.connect(lambda text, k=key: self.rename_group(k, text))
        color = QPushButton("Color")
        color.setStyleSheet(f"background-color: {group['color']};")
        color.clicked.connect(lambda checked=False, k=key: self.choose_color(k))
        row.addWidget(visible)
        row.addWidget(name_edit, 1)
        row.addWidget(color)
        outer.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("CDF role:"))
        role = QComboBox()
        role.addItems(["None", "Test", "Synthetic"])
        role.currentTextChanged.connect(lambda text, k=key: self.set_role(k, text))
        row2.addWidget(role, 1)
        remove = QPushButton("Remove")
        remove.clicked.connect(lambda checked=False, k=key: self.remove_group(k))
        row2.addWidget(remove)
        outer.addLayout(row2)
        files = QLabel(f"{len(group['paths'])} file(s) | "
                       f"{len(group['flat']):,} samples | "
                       f"{len(group['frequencies'])} frequencies")
        files.setToolTip("\n".join(group["paths"]))
        outer.addWidget(files)
        if group["bandwidth"] > 0:
            outer.addWidget(QLabel(f"Frequency median: {group['bandwidth']:g} {group['unit']}"))
        self.dataset_layout.addWidget(box)
        self.group_widgets[key] = dict(box=box, name=name_edit, color=color,
                                        role=role, visible=visible)

    def rename_group(self, key, text):
        self.groups[key]["name"] = text.strip() or "Unnamed dataset"
        self.update_plot()

    def set_visibility(self, key, checked):
        self.groups[key]["visible"] = checked
        self.update_plot()

    def choose_color(self, key):
        color = QColorDialog.getColor(QColor(self.groups[key]["color"]), self, "Dataset plot color")
        if color.isValid():
            self.groups[key]["color"] = color.name()
            self.group_widgets[key]["color"].setStyleSheet(f"background-color: {color.name()};")
            self.update_plot()

    def set_role(self, key, role):
        if role != "None":
            for other_key, other in self.groups.items():
                if other_key != key and other["role"] == role:
                    other["role"] = "None"
                    widget = self.group_widgets[other_key]["role"]
                    widget.blockSignals(True)
                    widget.setCurrentText("None")
                    widget.blockSignals(False)
        self.groups[key]["role"] = role
        self.populate_shared_selections()
        self.update_plot()

    def remove_group(self, key):
        widget = self.group_widgets.pop(key)["box"]
        self.dataset_layout.removeWidget(widget)
        widget.deleteLater()
        del self.groups[key]
        self.populate_shared_selections()
        self.update_plot()

    @staticmethod
    def _create_checkbox_area():
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(4, 4, 4, 4)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(95)
        scroll.setMaximumHeight(160)
        scroll.setWidget(widget)
        return layout, scroll

    def _populate_checks(self, layout, mapping, values, suffix):
        previous = {key: checkbox.isChecked() for key, checkbox in mapping.items()}
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        mapping.clear()
        for value in values:
            checkbox = QCheckBox(f"{value:g}{suffix}")
            checkbox.setChecked(previous.get(value, True))
            checkbox.toggled.connect(self.update_plot)
            layout.addWidget(checkbox)
            mapping[value] = checkbox

    def selected_pair(self):
        test = next((x for x in self.groups.values() if x["role"] == "Test"), None)
        synthetic = next((x for x in self.groups.values() if x["role"] == "Synthetic"), None)
        return test, synthetic

    def populate_shared_selections(self):
        active = [x["flat"] for x in self.groups.values() if x["visible"]]
        freqs = sorted(set().union(*(set(x["Freq"].unique()) for x in active))) if active else []
        phis = sorted(set().union(*(set(x["Phi"].unique()) for x in active))) if active else []
        self._populate_checks(self.freq_check_layout, self.freq_checks, freqs, " MHz")
        self._populate_checks(self.phi_check_layout, self.phi_checks, phis, "°")
        test, synth = self.selected_pair()
        if test is not None and synth is not None:
            matched_f = set(test["flat"]["Freq"]) & set(synth["flat"]["Freq"])
            matched_p = set(test["flat"]["Phi"]) & set(synth["flat"]["Phi"])
            self.match_label.setText(f"CDF pair: {test['name']} − {synth['name']}\n"
                                     f"{len(matched_f)} common frequencies, {len(matched_p)} common phi values")
        else:
            self.match_label.setText(f"{len(self.groups)} datasets loaded. "
                                     "Assign Test and Synthetic roles to enable CDF.")

    def set_all_checks(self, checked):
        for checkbox in list(self.freq_checks.values()) + list(self.phi_checks.values()):
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)
        self.update_plot()

    def selected_filters(self):
        return ([f for f, c in self.freq_checks.items() if c.isChecked()],
                [p for p, c in self.phi_checks.items() if c.isChecked()])

    def filtered_data(self, group):
        freqs, phis = self.selected_filters()
        flat = group["flat"]
        if not freqs or not phis:
            return flat.iloc[0:0]
        return flat.loc[flat["Freq"].isin(freqs) & flat["Phi"].isin(phis)]

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

    def update_plot(self, *_):
        if self.plot_select.currentText() == "CDF":
            self.plot_cdf()
        else:
            self.plot_overlay(polar=self.plot_select.currentText() == "Polar Plot")

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
        combos = [(f, p) for f in freqs for p in phis]
        styles = {fp: self.line_styles[i % len(self.line_styles)] for i, fp in enumerate(combos)}
        curves = 0
        for group in active:
            filtered = self.filtered_data(group)
            if filtered.empty:
                continue
            for (freq, phi), subset in filtered.groupby(["Freq", "Phi"], sort=False):
                for sweep_index, sweep in enumerate(self.split_theta_sweeps(subset)):
                    theta = sweep["Theta"].to_numpy(dtype=float)
                    value = sweep["PdB"].to_numpy(dtype=float)
                    ax.plot(np.deg2rad(theta) if polar else theta, value,
                            color=group["color"], linestyle=styles.get((freq, phi), "-"),
                            linewidth=1.5, alpha=.85,
                            label=(f"{group['name']} | {freq:g} MHz, φ={phi:g}°"
                                   if sweep_index == 0 else "_nolegend_"))
                    curves += 1
        if not curves:
            self.draw_message(canvas, "No data matches selected filters.")
            return
        if polar:
            ax.set_title("Polar Radiation Pattern", pad=20)
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)
            ax.set_rlim(-80, 0)
            ax.set_rlabel_position(225)
        else:
            ax.set_title("Linear Radiation Pattern")
            ax.set_xlabel("Theta (degrees)")
            ax.set_ylabel("Power (dB)")
            ax.set_xlim(-180, 180)
            ax.set_ylim(-80, 0)
        ax.grid(True, alpha=.35)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize="small")
        fig.tight_layout()
        canvas.draw_idle()
        self.statusBar().showMessage(f"Displaying {curves} angular sweeps from {len(active)} datasets")

    def plot_cdf(self):
        canvas = self.cdf_canvas
        self.stacklayout.setCurrentWidget(self.plot_pages[canvas])
        test, synthetic = self.selected_pair()
        if test is None or synthetic is None:
            self.draw_message(canvas, "Assign one dataset as Test and another as Synthetic for CDF.")
            return
        left = self.filtered_data(test)
        right = self.filtered_data(synthetic)
        if left.empty or right.empty:
            self.draw_message(canvas, "No selected frequency/phi samples for the CDF pair.")
            return
        keys = ["Freq", "Phi", "Theta"]
        # Collapse duplicates before pairing to prevent Cartesian explosions when
        # a file contains repeated angular sweeps.
        left = left.groupby(keys, as_index=False)["PdB"].median().rename(columns={"PdB": "test_db"})
        right = right.groupby(keys, as_index=False)["PdB"].median().rename(columns={"PdB": "synthetic_db"})
        paired = left.merge(right, on=keys, how="inner")
        if paired.empty:
            self.draw_message(canvas, "No matching frequency / phi / theta samples.")
            return
        paired["delta_db"] = paired["test_db"] - paired["synthetic_db"]
        self.cdf_paired = paired
        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        summary = []
        for (freq, phi), subset in paired.groupby(["Freq", "Phi"], sort=True):
            x, y, (p25, p50, p75) = cdf_statistics(subset["delta_db"])
            if len(x) == 0:
                continue
            line, = ax.step(x, y, where="post", linewidth=1.8,
                            label=f"{test['name']} − {synthetic['name']} | {freq:g} MHz, φ={phi:g}°")
            for prob, value, marker in ((.25, p25, "o"), (.5, p50, "s"), (.75, p75, "^")):
                ax.plot(value, prob, marker=marker, color=line.get_color(), markersize=5, linestyle="None")
            summary.append({"Freq": freq, "Phi": phi, "Count": len(subset),
                            "P25": p25, "P50": p50, "P75": p75})
        self.cdf_summary = pd.DataFrame(summary)
        comparison = f"{test['name']} − {synthetic['name']}"
        ax.set_title(f"CDF of {comparison}")
        ax.set_xlabel(f"{comparison} (dB)")
        ax.set_ylabel("Cumulative Probability")
        ax.set_ylim(0, 1.02)
        ax.grid(True, alpha=.35)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize="small")
        fig.tight_layout()
        canvas.draw_idle()
        self.statusBar().showMessage(f"CDF: {len(paired):,} matched angular points, {len(summary)} curves")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
