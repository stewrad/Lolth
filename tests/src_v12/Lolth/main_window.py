import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg,NavigationToolbar2QT
from PyQt6.QtCore import Qt,QTimer,QSignalBlocker
from PyQt6.QtGui import QAction,QColor
from PyQt6.QtWidgets import (QApplication,QMainWindow,QWidget,QLabel,QLineEdit,QPushButton,QListWidget,QListWidgetItem,QComboBox,QCheckBox,QGroupBox,QFileDialog,QMessageBox,QScrollArea,QVBoxLayout,QHBoxLayout,QStackedLayout,QDialog,QSplitter,QColorDialog,QDoubleSpinBox,QFormLayout)
from .modeling.vtk_viewer import EmbeddedVTKDialog
from .file_reading.load_dialog import DatasetLoadDialog
from .plotting.charts import PlotMixin
from .plotting.export import CDFExportMixin

class MainWindow(PlotMixin, CDFExportMixin, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RF Dataset Comparison")
        self.resize(1480, 880)
        self.last_dir = Path.cwd()
        self.groups = {}  # Unlimited dataset count, stable UUID keys
        self.group_widgets = {}
        self.freq_checks = {}
        self.phi_checks = {}
        self.p_checks = {}
        self.line_styles = ["-", "--", "-.", ":"]
        self.cdf_paired = pd.DataFrame()
        self.cdf_summary = pd.DataFrame()
        self.cdf_plot_data = pd.DataFrame()
        self.cdf_overall_p75 = None
        self.stl_viewers = []
        self._build_menu()
        self._build_ui()
        # UI signals only schedule a redraw; rapid user input is consolidated.
        self._plot_timer = QTimer(self)
        self._plot_timer.setSingleShot(True)
        self._plot_timer.setInterval(85)
        self._plot_timer.timeout.connect(self._paint_selected_plot)
        self._plot_pending = False
        self.plot_select.currentTextChanged.connect(self.update_plot)
        self.update_plot()

    def _build_menu(self):
        menu = self.menuBar().addMenu("&File")
        action = QAction("Load and group files…", self)
        action.setShortcut("Ctrl+O")
        action.triggered.connect(self.open_files)
        menu.addAction(action)
        export_action = QAction("Export CDF data…", self)
        export_action.setShortcut("Ctrl+Shift+E")
        export_action.triggered.connect(self.export_cdf_data)
        menu.addAction(export_action)
        view_menu = self.menuBar().addMenu("&3D Plots")
        model_action = QAction("3D Model", self)
        model_action.triggered.connect(self.open_stl_viewer)
        view_menu.addAction(model_action)
        radiation_action = QAction("3D Model - Radiation Pattern", self)
        radiation_action.triggered.connect(self.open_radiation_viewer)
        view_menu.addAction(radiation_action)
        edit_menu = self.menuBar().addMenu("&Edit")
        shift_action = QAction("Shift Dataset Angles…", self)
        shift_action.triggered.connect(self.open_shift_dialog)
        edit_menu.addAction(shift_action)

    def open_shift_dialog(self):
        """Apply signed offsets to one dataset; values are degrees."""
        if not self.groups:
            QMessageBox.information(self, "Shift Dataset", "Load a dataset first.")
            return
        from .processing.shift import shift_dataset_angles
        dialog = QDialog(self)
        dialog.setWindowTitle("Shift Dataset Angles")
        dialog.setMinimumWidth(340)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        dataset = QComboBox()
        for key, group in self.groups.items():
            dataset.addItem(group["name"], key)
        form.addRow("Dataset", dataset)
        az = QDoubleSpinBox()
        el = QDoubleSpinBox()
        for spin in (az, el):
            spin.setRange(-360.0, 360.0)
            spin.setDecimals(3)
            spin.setSingleStep(1.0)
            spin.setSuffix("°")
        form.addRow("Azimuth / Theta shift", az)
        form.addRow("Elevation / Phi shift", el)
        layout.addLayout(form)
        note = QLabel("Applies a signed angular offset to the selected dataset. "
                      "Azimuth/Theta wraps to ±180°. Elevation/Phi is shifted "
                      "without clipping. Original E1/A1 columns stay synchronized.")
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QHBoxLayout()
        apply_button = QPushButton("Apply Shift")
        cancel_button = QPushButton("Cancel")
        buttons.addWidget(apply_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        cancel_button.clicked.connect(dialog.reject)

        def apply():
            key = dataset.currentData()
            group = self.groups.get(key)
            if group is None:
                return
            az_delta, el_delta = az.value(), el.value()
            if not az_delta and not el_delta:
                dialog.accept()
                return
            shift_dataset_angles(group["flat"], az_delta, el_delta)
            # Cache invalidation ensures the selectors reflect the moved grid.
            group.pop("phi_options", None)
            group.pop("frequency_options", None)
            self.populate_shared_selections(clear=True)
            self.update_plot()
            self.statusBar().showMessage(
                f"Shifted {group['name']}: azimuth {az_delta:+g}°, elevation {el_delta:+g}°")
            dialog.accept()

        apply_button.clicked.connect(apply)
        dialog.exec()

    def open_stl_viewer(self):
        popup = EmbeddedVTKDialog(self, radiation=False)
        popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        popup.destroyed.connect(lambda *_: self.stl_viewers.remove(popup)
                                if popup in self.stl_viewers else None)
        self.stl_viewers.append(popup)
        popup.show()

    def open_radiation_viewer(self):
        popup = EmbeddedVTKDialog(self, radiation=True)
        popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        popup.destroyed.connect(lambda *_: self.stl_viewers.remove(popup)
                                if popup in self.stl_viewers else None)
        self.stl_viewers.append(popup)
        popup.show()

    def _build_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = QWidget()
        left = QVBoxLayout(left_panel)
        add = QPushButton("Load / Group Files…")
        add.clicked.connect(self.open_files)
        left.addWidget(add)
        left.addWidget(QLabel("Datasets (rename, recolor, show/hide, assign CDF roles):"))
        # Only the dataset cards scroll: the selectors stay pinned to the bottom left.
        dataset_scroll = QScrollArea()
        dataset_scroll.setWidgetResizable(True)
        dataset_scroll.setMinimumHeight(120)
        self.dataset_holder = QWidget()
        self.dataset_layout = QVBoxLayout(self.dataset_holder)
        self.dataset_layout.setContentsMargins(0, 0, 0, 0)
        self.dataset_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        dataset_scroll.setWidget(self.dataset_holder)
        left.addWidget(dataset_scroll, 1)
        left.addWidget(QLabel("Plot Type"))
        self.plot_select = QComboBox()
        self.plot_select.addItems(["Linear Plot", "Polar Plot", "CDF", "Heatmap"])
        left.addWidget(self.plot_select)
        # Presentation-only coordinate convention. Internal columns remain
        # Theta (azimuth) and Phi (elevation) for all processing operations.
        self.plot_phi_theta = QCheckBox("Plot Phi-Theta")
        self.plot_phi_theta.setChecked(True)  # Retain the original plot appearance.
        self.plot_phi_theta.setToolTip(
            "Checked: use measured Phi/Theta scan coordinates. "
            "Unchecked: transform scan directions into Azimuth/Elevation. "
            "Raw RF samples are not modified."
        )
        self.plot_phi_theta.toggled.connect(self._on_plot_coordinate_mode_changed)
        left.addWidget(self.plot_phi_theta)
        self.heatmap_controls = QWidget()
        heatmap_row = QHBoxLayout(self.heatmap_controls)
        heatmap_row.setContentsMargins(0, 0, 0, 0)
        heatmap_row.addWidget(QLabel("Heatmap dataset:"))
        self.heatmap_dataset_select = QComboBox()
        self.heatmap_dataset_select.currentIndexChanged.connect(self.update_plot)
        heatmap_row.addWidget(self.heatmap_dataset_select, 1)
        self.heatmap_p_select = QComboBox()
        self.heatmap_p_select.addItems(["AA", "AB", "BA", "BB"])
        self.heatmap_p_select.currentTextChanged.connect(self.update_plot)
        heatmap_row.addWidget(QLabel("P:"))
        heatmap_row.addWidget(self.heatmap_p_select)
        left.addWidget(self.heatmap_controls)
        self.heatmap_controls.setVisible(False)
        self.match_label = QLabel("Load datasets to begin.")
        self.match_label.setWordWrap(True)
        left.addWidget(self.match_label)
        left.addWidget(QLabel("Frequency Selection (across loaded datasets)"))
        self.freq_check_layout, freq_area = self._create_checkbox_area()
        left.addWidget(freq_area)
        freq_row = QHBoxLayout()
        for label, on in (("Select All", True), ("Clear All", False)):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, value=on: self.set_all_checks(value, "freq"))
            freq_row.addWidget(button)
        left.addLayout(freq_row)
        self.phi_selection_label = QLabel("Phi Selection (across loaded datasets)")
        left.addWidget(self.phi_selection_label)
        self.phi_check_layout, phi_area = self._create_checkbox_area()
        left.addWidget(phi_area)
        phi_row = QHBoxLayout()
        for label, on in (("Select All", True), ("Clear All", False)):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, value=on: self.set_all_checks(value, "phi"))
            phi_row.addWidget(button)
        left.addLayout(phi_row)
        left.addWidget(QLabel("Polarization Selection (P)"))
        p_row = QHBoxLayout()
        for pol in ("AA", "AB", "BA", "BB"):
            checkbox = QCheckBox(pol)
            checkbox.setChecked(True)
            checkbox.toggled.connect(self.update_plot)
            self.p_checks[pol] = checkbox
            p_row.addWidget(checkbox)
        left.addLayout(p_row)
        left_panel.setMinimumWidth(365)
        splitter.addWidget(left_panel)
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.cdf_overall_label = QLabel("Overall |ΔdB| P75: —")
        self.cdf_overall_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.cdf_overall_label.setStyleSheet("font-weight: 600; padding: 5px 12px;")
        self.cdf_overall_label.hide()
        right_layout.addWidget(self.cdf_overall_label)
        plot_stack_holder = QWidget()
        self.stacklayout = QStackedLayout(plot_stack_holder)
        self.stacklayout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(plot_stack_holder, 1)
        self.plot_pages = {}
        self.toolbars = {}
        self.linear_canvas = FigureCanvasQTAgg(Figure())
        self.polar_canvas = FigureCanvasQTAgg(Figure())
        self.cdf_canvas = FigureCanvasQTAgg(Figure())
        self.heatmap_canvas = FigureCanvasQTAgg(Figure())
        for canvas in (self.linear_canvas, self.polar_canvas, self.cdf_canvas, self.heatmap_canvas):
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

    def _on_plot_coordinate_mode_changed(self, *_):
        """Replot transformed scan positions without modifying original RF data."""
        if self.plot_phi_theta.isChecked():
            self.phi_selection_label.setText("Phi Selection (across loaded datasets)")
        else:
            self.phi_selection_label.setText("Elevation Selection (across loaded datasets)")
        self.update_plot()

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
        self.populate_shared_selections(clear=True)
        self.update_heatmap_datasets()
        self.update_plot()
        self.statusBar().showMessage(f"Added {len(popup.result_groups)} datasets; frequency/Phi selections cleared")

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
        self.update_heatmap_datasets()
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
        self.update_heatmap_datasets()
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

    def _populate_checks(self, layout, mapping, values, suffix, clear=False):
        previous = {} if clear else {key: checkbox.isChecked() for key, checkbox in mapping.items()}
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        mapping.clear()
        for value in values:
            checkbox = QCheckBox(f"{value:g}{suffix}")
            checkbox.setChecked(previous.get(value, False))
            checkbox.toggled.connect(self.update_plot)
            layout.addWidget(checkbox)
            mapping[value] = checkbox

    def selected_pair(self):
        test = next((x for x in self.groups.values() if x["role"] == "Test"), None)
        synthetic = next((x for x in self.groups.values() if x["role"] == "Synthetic"), None)
        return test, synthetic

    def populate_shared_selections(self, clear=False):
        active = [x for x in self.groups.values() if x["visible"]]
        # Cache unique selectors per dataset: avoid scanning millions of rows
        # whenever a CDF role or dataset visibility is changed.
        for group in self.groups.values():
            if "frequency_options" not in group:
                group["frequency_options"] = np.sort(group["flat"]["Freq"].dropna().unique())
            if "phi_options" not in group:
                group["phi_options"] = np.sort(group["flat"]["Phi"].dropna().unique())
        freqs = sorted(set().union(*(set(x["frequency_options"]) for x in active))) if active else []
        phis = sorted(set().union(*(set(x["phi_options"]) for x in active))) if active else []
        self._populate_checks(self.freq_check_layout, self.freq_checks, freqs, " MHz", clear)
        self._populate_checks(self.phi_check_layout, self.phi_checks, phis, "°", clear)
        test, synth = self.selected_pair()
        if test is not None and synth is not None:
            matched_f = set(test["frequency_options"]) & set(synth["frequency_options"])
            matched_p = set(test["phi_options"]) & set(synth["phi_options"])
            self.match_label.setText(f"CDF pair: {test['name']} − {synth['name']}\n"
                                     f"{len(matched_f)} common frequencies, {len(matched_p)} common phi values")
        else:
            self.match_label.setText(f"{len(self.groups)} datasets loaded. "
                                     "Assign Test and Synthetic roles to enable CDF.")

    def set_all_checks(self, checked, selection):
        checks = self.freq_checks if selection == "freq" else self.phi_checks
        for checkbox in checks.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)
        self.update_plot()

    def selected_filters(self):
        return ([f for f, c in self.freq_checks.items() if c.isChecked()],
                [p for p, c in self.phi_checks.items() if c.isChecked()])

    def selected_polarizations(self):
        return [p for p, cb in self.p_checks.items() if cb.isChecked()]

    def filtered_data(self, group):
        freqs, phis = self.selected_filters()
        flat = group["flat"]
        if not freqs or not phis or not self.selected_polarizations():
            return flat.iloc[0:0]
        return flat.loc[flat["Freq"].isin(freqs) & flat["Phi"].isin(phis)
                        & flat["P"].isin(self.selected_polarizations())]

