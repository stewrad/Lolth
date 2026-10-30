"""RF multi-dataset viewer. Requires: PyQt6, numpy, pandas, matplotlib,
plus vtk 9.4.2, scipy and numpy-stl for experimental embedded VTK viewers,
and the existing file_loader.py and cdf.py modules.

Frequency bandwidth median: for each selected center frequency, replace its
PdB values with the median of samples at the SAME (Phi, Theta) coordinates
within a full bandwidth window centered on the frequency. Bandwidth can be
specified in MHz or percent of the center frequency. The selected frequencies
are retained as the plot/CDF centers.
"""

import sys
import os
# On Linux, use XCB for the Qt/VTK native-window integration.
# Override from the shell if your system requires a different Qt platform.
if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
from pathlib import Path


from uuid import uuid4

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

import file_loader as fl
from cdf import flatten_rf, cdf_statistics

from PyQt6.QtCore import Qt, QTimer
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


class EmbeddedVTKDialog(QDialog):
    """Experimental Qt6 QOpenGLWidget interactor for VTK 9.4.2."""

    def __init__(self, parent=None, radiation=False):
        super().__init__(parent)
        self.radiation_mode = radiation
        self.setWindowTitle("3D Model - Radiation Pattern" if radiation else "3D Model")
        self.resize(1200, 820)
        self.model_path = None
        self.model_color = QColor("#a6bdd0")
        self.model_actor = None
        self.pattern_actor = None
        self.bar_actor = None
        self._initialized = False
        self._pending_render = False
        self.last_dir = getattr(parent, "last_dir", Path.cwd())
        self.groups = parent.groups if parent is not None else {}

        # Request the Qt6 OpenGL widget implementation rather than the default
        # native child QWidget window. Must be set before importing the class.
        import vtkmodules.qt
        vtkmodules.qt.QVTKRWIBase = "QOpenGLWidget"
        from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
        from vtkmodules.vtkRenderingCore import vtkRenderer
        from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
        import vtkmodules.vtkRenderingOpenGL2  # Register OpenGL rendering backend

        outer = QHBoxLayout(self)
        controls = QWidget()
        controls.setMaximumWidth(310)
        layout = QVBoxLayout(controls)
        layout.addWidget(QLabel("STL geometry"))
        browse = QPushButton("Load STL…")
        browse.clicked.connect(self.open_stl)
        layout.addWidget(browse)
        self.model_label = QLabel("No STL loaded")
        self.model_label.setWordWrap(True)
        layout.addWidget(self.model_label)
        self.color_button = QPushButton("Model Color…")
        self.color_button.clicked.connect(self.choose_color)
        layout.addWidget(self.color_button)
        self._refresh_color()

        if radiation:
            layout.addWidget(QLabel("RF dataset"))
            self.dataset_combo = QComboBox()
            for key, group in self.groups.items():
                self.dataset_combo.addItem(group["name"], key)
            self.dataset_combo.currentIndexChanged.connect(self.refresh_frequencies)
            layout.addWidget(self.dataset_combo)
            layout.addWidget(QLabel("Center frequency (MHz)"))
            self.frequency_combo = QComboBox()
            layout.addWidget(self.frequency_combo)
            layout.addWidget(QLabel("Radiation origin (x, y, z) in STL units"))
            self.origin_spins = []
            for label in ("X", "Y", "Z"):
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                spin = QDoubleSpinBox()
                spin.setRange(-1e9, 1e9)
                spin.setDecimals(4)
                row.addWidget(spin)
                layout.addLayout(row)
                self.origin_spins.append(spin)
            layout.addWidget(QLabel("Radiation scale (relative to STL size)"))
            self.scale_spin = QDoubleSpinBox()
            self.scale_spin.setRange(0.001, 1000)
            self.scale_spin.setDecimals(3)
            self.scale_spin.setValue(1.5)
            layout.addWidget(self.scale_spin)
            layout.addWidget(QLabel("Gain floor (relative dB)"))
            self.floor_spin = QDoubleSpinBox()
            self.floor_spin.setRange(-200, -0.01)
            self.floor_spin.setValue(-35)
            layout.addWidget(self.floor_spin)
            layout.addWidget(QLabel("Color scale (relative gain, dB)"))
            color_range_row = QHBoxLayout()
            self.color_min_spin = QDoubleSpinBox()
            self.color_min_spin.setRange(-200, 200)
            self.color_min_spin.setDecimals(1)
            self.color_min_spin.setSingleStep(5)
            self.color_min_spin.setValue(-35.0)
            self.color_min_spin.setPrefix("Min: ")
            color_range_row.addWidget(self.color_min_spin)
            self.color_max_spin = QDoubleSpinBox()
            self.color_max_spin.setRange(-200, 200)
            self.color_max_spin.setDecimals(1)
            self.color_max_spin.setSingleStep(5)
            self.color_max_spin.setValue(0.0)
            self.color_max_spin.setPrefix("Max: ")
            color_range_row.addWidget(self.color_max_spin)
            layout.addLayout(color_range_row)
            self.color_min_spin.valueChanged.connect(self.update_color_scale)
            self.color_max_spin.valueChanged.connect(self.update_color_scale)
            layout.addWidget(QLabel("Gaussian sigma (samples)"))
            self.sigma_spin = QDoubleSpinBox()
            self.sigma_spin.setRange(0, 50)
            self.sigma_spin.setDecimals(2)
            self.sigma_spin.setValue(2)
            layout.addWidget(self.sigma_spin)
            layout.addWidget(QLabel("Pattern opacity"))
            self.opacity_spin = QDoubleSpinBox()
            self.opacity_spin.setRange(0.05, 1.0)
            self.opacity_spin.setSingleStep(0.05)
            self.opacity_spin.setValue(0.75)
            layout.addWidget(self.opacity_spin)
            update = QPushButton("Render radiation pattern")
            update.clicked.connect(self.render_pattern)
            layout.addWidget(update)
            self.refresh_frequencies()
        layout.addStretch(1)
        self.status_label = QLabel("Drag to rotate; scroll to zoom.")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        outer.addWidget(controls)

        self.vtk_widget = QVTKRenderWindowInteractor(self)
        outer.addWidget(self.vtk_widget, 1)
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(1.0, 1.0, 1.0)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtk_widget.GetRenderWindow().GetInteractor().SetInteractorStyle(
            vtkInteractorStyleTrackballCamera())

    def showEvent(self, event):
        super().showEvent(event)
        if not self._initialized:
            QTimer.singleShot(0, self._initialize_vtk)

    def _initialize_vtk(self):
        if self._initialized:
            return
        self._initialized = True
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()
        self.vtk_widget.GetRenderWindow().Render()

    def _render(self, reset_camera=False):
        if reset_camera:
            self.renderer.ResetCamera()
        if self._initialized:
            self.vtk_widget.GetRenderWindow().Render()

    def _refresh_color(self):
        color = self.model_color
        fg = "white" if color.lightness() < 125 else "black"
        self.color_button.setStyleSheet(f"background-color: {color.name()}; color: {fg};")

    def choose_color(self):
        color = QColorDialog.getColor(self.model_color, self, "Model color")
        if not color.isValid():
            return
        self.model_color = color
        self._refresh_color()
        if self.model_actor is not None:
            self.model_actor.GetProperty().SetColor(*color.getRgbF()[:3])
            self._render()

    def open_stl(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open STL", str(self.last_dir), "STL (*.stl);;All Files (*)")
        if not path:
            return
        try:
            from stl.mesh import Mesh
            mesh = Mesh.from_file(path)
            vectors = np.asarray(mesh.vectors, dtype=float)
            if not len(vectors) or not np.isfinite(vectors).all():
                raise ValueError("STL is empty or contains non-finite vertices")
            self.model_vertices = vectors
            self.model_path = Path(path)
            self.last_dir = self.model_path.parent
            self._draw_stl(vectors)
            self.model_label.setText(f"{self.model_path.name} — {len(vectors):,} triangles")
            if self.radiation_mode:
                self.render_pattern()
        except Exception as exc:
            QMessageBox.critical(self, "STL load error", str(exc))

    @staticmethod
    def _triangle_polydata(triangles, scalar_values=None):
        from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkCellArray
        from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
        triangles = np.ascontiguousarray(triangles, dtype=np.float64)
        verts = triangles.reshape(-1, 3)
        from vtkmodules.vtkCommonCore import vtkPoints
        points = vtkPoints()
        points.SetData(numpy_to_vtk(verts, deep=True))
        poly = vtkPolyData()
        poly.SetPoints(points)
        n = len(triangles)
        connectivity = np.column_stack([np.full(n, 3, dtype=np.int64),
                                        np.arange(n * 3, dtype=np.int64).reshape(n, 3)]).ravel()
        cells = vtkCellArray()
        cells.SetCells(n, numpy_to_vtkIdTypeArray(connectivity, deep=True))
        poly.SetPolys(cells)
        if scalar_values is not None:
            scalars = numpy_to_vtk(np.asarray(scalar_values, dtype=np.float64).ravel(), deep=True)
            scalars.SetName("Relative Gain (dB)")
            poly.GetPointData().SetScalars(scalars)
        return poly

    def _draw_stl(self, vertices):
        from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper
        if self.model_actor is not None:
            self.renderer.RemoveActor(self.model_actor)
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(self._triangle_polydata(vertices))
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*self.model_color.getRgbF()[:3])
        self.renderer.AddActor(actor)
        self.model_actor = actor
        self._render(reset_camera=True)

    def refresh_frequencies(self, *_):
        if not self.radiation_mode:
            return
        current = self.frequency_combo.currentData()
        self.frequency_combo.clear()
        group = self.groups.get(self.dataset_combo.currentData())
        if group is None:
            return
        values = np.sort(group["flat"]["Freq"].dropna().unique())
        for freq in values:
            self.frequency_combo.addItem(f"{freq:g} MHz", float(freq))
        idx = self.frequency_combo.findData(current)
        if idx >= 0:
            self.frequency_combo.setCurrentIndex(idx)

    def _color_limits(self):
        vmin = self.color_min_spin.value()
        vmax = self.color_max_spin.value()
        if vmin >= vmax:
            raise ValueError("Color scale minimum must be less than maximum.")
        return vmin, vmax

    def update_color_scale(self, *_):
        """Apply independent scale limits to both surface colors and the scalar bar.

        Does not recalculate the geometry, smooth the measurement, or reset the camera.
        Values outside the color range saturate at its endpoints.
        """
        if not self.radiation_mode or not hasattr(self, "pattern_mapper"):
            return
        try:
            low, high = self._color_limits()
        except ValueError:
            self.status_label.setText("Color minimum must be less than maximum.")
            return
        self.pattern_lut.SetRange(low, high)
        self.pattern_lut.Build()
        self.pattern_mapper.SetScalarRange(low, high)
        self.pattern_mapper.Modified()
        if self.bar_actor is not None:
            self.bar_actor.SetLookupTable(self.pattern_lut)
            self.bar_actor.Modified()
        self._render()

    def render_pattern(self):
        if not self.radiation_mode:
            return
        group = self.groups.get(self.dataset_combo.currentData())
        freq = self.frequency_combo.currentData()
        if group is None or freq is None:
            self.status_label.setText("Select a loaded RF dataset and frequency.")
            return
        try:
            from scipy.ndimage import gaussian_filter
            from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper
            from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
            from vtkmodules.vtkCommonCore import vtkLookupTable
            import matplotlib
            df = group["flat"]
            selection = df.loc[np.isclose(df["Freq"].to_numpy(dtype=float), float(freq))]
            if selection.empty:
                raise ValueError("No data for selected frequency")
            # Conventions match the supplied RF script: Theta = elevation, Phi = azimuth.
            grid = selection.pivot_table(index="Theta", columns="Phi", values="PdB", aggfunc="mean")
            grid = grid.sort_index().sort_index(axis=1)
            if min(grid.shape) < 2:
                raise ValueError("Need >=2 distinct elevations and >=2 azimuths")
            elevations = grid.index.to_numpy(dtype=float)
            azimuths = grid.columns.to_numpy(dtype=float)
            full_azimuth = np.isclose(azimuths[-1] - azimuths[0], 360, atol=1.5)
            if full_azimuth:
                grid = grid.iloc[:, :-1]
                azimuths = grid.columns.to_numpy(dtype=float)
            grid = grid.interpolate(axis=0, method="index", limit_direction="both")
            grid = grid.interpolate(axis=1, method="index", limit_direction="both")
            if grid.isna().any().any():
                raise ValueError("Cannot interpolate missing grid samples")
            db = grid.to_numpy(dtype=float)
            smooth = gaussian_filter(db, sigma=self.sigma_spin.value(),
                         mode=("nearest", "wrap" if full_azimuth else "nearest"))
            rel = smooth - float(np.max(smooth))
            radius = 10 ** (np.maximum(rel, self.floor_spin.value()) / 20.0)
            if hasattr(self, "model_vertices"):
                size = float(np.ptp(self.model_vertices.reshape(-1, 3), axis=0).max())
                if size <= 0:
                    raise ValueError("Model dimensions are zero")
            else:
                size = 1.0
            radius *= size * self.scale_spin.value()
            th, ph = np.meshgrid(np.deg2rad(elevations), np.deg2rad(azimuths), indexing="ij")
            origin = np.array([x.value() for x in self.origin_spins])
            points = np.stack((radius * np.cos(th) * np.cos(ph),
                               radius * np.cos(th) * np.sin(ph),
                               radius * np.sin(th)), axis=-1) + origin
            if full_azimuth:
                points = np.concatenate([points, points[:, :1]], axis=1)
                rel = np.concatenate([rel, rel[:, :1]], axis=1)
            triangles = np.concatenate((np.stack((points[:-1,:-1], points[1:,:-1], points[1:,1:]), axis=-2),
                                        np.stack((points[:-1,:-1], points[1:,1:], points[:-1,1:]), axis=-2)), axis=0).reshape(-1,3,3)
            values = np.concatenate((np.stack((rel[:-1,:-1], rel[1:,:-1], rel[1:,1:]), axis=-1),
                                     np.stack((rel[:-1,:-1], rel[1:,1:], rel[:-1,1:]), axis=-1)),axis=0).reshape(-1,3)
            poly = self._triangle_polydata(triangles, values)
            lut = vtkLookupTable()
            lut.SetNumberOfTableValues(256)
            cmap = matplotlib.colormaps.get_cmap("jet")
            for i in range(256):
                lut.SetTableValue(i, *cmap(i/255))
            vmin, vmax = self._color_limits()
            lut.SetRange(vmin, vmax)
            lut.Build()
            mapper = vtkPolyDataMapper()
            mapper.SetInputData(poly)
            mapper.SetLookupTable(lut)
            mapper.SetScalarRange(vmin, vmax)
            mapper.SetScalarModeToUsePointData()
            actor = vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetOpacity(self.opacity_spin.value())
            if self.pattern_actor is not None:
                self.renderer.RemoveActor(self.pattern_actor)
            self.renderer.AddActor(actor)
            self.pattern_actor = actor
            self.pattern_mapper = mapper
            self.pattern_lut = lut
            if self.bar_actor is not None:
                self.renderer.RemoveActor2D(self.bar_actor)
            bar = vtkScalarBarActor()
            bar.SetLookupTable(lut)
            bar.SetTitle("Relative Gain (dB)")
            bar.SetNumberOfLabels(5)
            self.renderer.AddActor2D(bar)
            self.bar_actor = bar
            self._render(reset_camera=True)
            self.status_label.setText(f"{group['name']} | {freq:g} MHz | {len(triangles):,} triangles")
        except Exception as exc:
            QMessageBox.warning(self, "Radiation pattern", str(exc))

    def closeEvent(self, event):
        try:
            self.vtk_widget.Finalize()
            self.vtk_widget.GetRenderWindow().SetInteractor(None)
        except Exception:
            pass
        super().closeEvent(event)


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
        self.stl_viewers = []
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
        view_menu = self.menuBar().addMenu("&View")
        model_action = QAction("3D Model", self)
        model_action.triggered.connect(self.open_stl_viewer)
        view_menu.addAction(model_action)
        radiation_action = QAction("3D Model - Radiation Pattern", self)
        radiation_action.triggered.connect(self.open_radiation_viewer)
        view_menu.addAction(radiation_action)

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
        self.heatmap_controls = QWidget()
        heatmap_row = QHBoxLayout(self.heatmap_controls)
        heatmap_row.setContentsMargins(0, 0, 0, 0)
        heatmap_row.addWidget(QLabel("Heatmap dataset:"))
        self.heatmap_dataset_select = QComboBox()
        self.heatmap_dataset_select.currentIndexChanged.connect(self.update_plot)
        heatmap_row.addWidget(self.heatmap_dataset_select, 1)
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
        left.addWidget(QLabel("Phi Selection (across loaded datasets)"))
        self.phi_check_layout, phi_area = self._create_checkbox_area()
        left.addWidget(phi_area)
        phi_row = QHBoxLayout()
        for label, on in (("Select All", True), ("Clear All", False)):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, value=on: self.set_all_checks(value, "phi"))
            phi_row.addWidget(button)
        left.addLayout(phi_row)
        left_panel.setMinimumWidth(365)
        splitter.addWidget(left_panel)
        right = QWidget()
        self.stacklayout = QStackedLayout(right)
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
        self.update_heatmap_datasets()
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
        kind = self.plot_select.currentText()
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
        # pcolormesh supports irregular angular coordinate spacing.
        mesh = ax.pcolormesh(grid.columns.to_numpy(dtype=float),
                             grid.index.to_numpy(dtype=float),
                             np.ma.masked_invalid(grid.to_numpy(dtype=float)),
                             shading="auto", cmap="viridis")
        fig.colorbar(mesh, ax=ax, label="Power (dB)")
        ax.set_title(f"{group['name']} | {freq:g} MHz")
        ax.set_xlabel("Theta (degrees)")
        ax.set_ylabel("Phi (degrees)")
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
