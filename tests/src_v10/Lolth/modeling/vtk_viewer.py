import numpy as np
import pandas as pd
from pathlib import Path
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QDialog,QWidget,QLabel,QPushButton,QComboBox,QDoubleSpinBox,QColorDialog,QFileDialog,QMessageBox,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,QCheckBox,QGroupBox)

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
        self._camera_reset_pending = False
        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(35)
        self._render_timer.timeout.connect(self._flush_render)
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
            layout.addWidget(QLabel("Plot title"))
            self.plot_title_edit = QLineEdit("3D Antenna Radiation Pattern")
            self.plot_title_edit.editingFinished.connect(self.update_annotations)
            layout.addWidget(self.plot_title_edit)
            layout.addWidget(QLabel("Color bar title"))
            self.bar_title_edit = QLineEdit("Relative Gain (dB)")
            self.bar_title_edit.editingFinished.connect(self.update_annotations)
            layout.addWidget(self.bar_title_edit)
            layout.addWidget(QLabel("Radiation colormap"))
            self.cmap_combo = QComboBox()
            self.cmap_combo.addItems(["jet", "viridis", "plasma", "inferno", "magma", "cividis", "turbo", "coolwarm", "Spectral", "gray"])
            self.cmap_combo.currentTextChanged.connect(self.update_colormap)
            layout.addWidget(self.cmap_combo)
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
        self._render()

    def _render(self, reset_camera=False):
        """Coalesce updates, avoiding a heavy GL render inside click handlers."""
        self._camera_reset_pending |= bool(reset_camera)
        if self._initialized:
            self._render_timer.start()

    def _flush_render(self):
        if not self._initialized or not self.isVisible():
            return
        if self._camera_reset_pending:
            self.renderer.ResetCamera()
        self._camera_reset_pending = False
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
            # Render the STL first; RF geometry remains explicitly user-controlled
            # via the Render radiation pattern button.
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
        self.frequency_combo.blockSignals(True)
        self.frequency_combo.clear()
        group = self.groups.get(self.dataset_combo.currentData())
        if group is None:
            self.frequency_combo.blockSignals(False)
            return
        values = group.get("frequency_options")
        if values is None:
            values = np.sort(group["flat"]["Freq"].dropna().unique())
        for freq in values:
            self.frequency_combo.addItem(f"{freq:g} MHz", float(freq))
        idx = self.frequency_combo.findData(current)
        if idx >= 0:
            self.frequency_combo.setCurrentIndex(idx)
        self.frequency_combo.blockSignals(False)

    def _color_limits(self):
        vmin = self.color_min_spin.value()
        vmax = self.color_max_spin.value()
        if vmin >= vmax:
            raise ValueError("Color scale minimum must be less than maximum.")
        return vmin, vmax

    def update_annotations(self):
        """Update titles without regenerating mesh geometry or resetting camera."""
        if not self.radiation_mode:
            return
        if self.bar_actor is not None:
            self.bar_actor.SetTitle(self.bar_title_edit.text().strip())
            self.bar_actor.Modified()
        if hasattr(self, "title_actor"):
            self.title_actor.SetInput(self.plot_title_edit.text().strip())
            self.title_actor.Modified()
        self._render()

    def update_colormap(self, *_):
        """Update VTK's LUT while preserving geometry and scalar range."""
        if not self.radiation_mode or not hasattr(self, "pattern_lut"):
            return
        import matplotlib
        cmap = matplotlib.colormaps.get_cmap(self.cmap_combo.currentText())
        for i in range(256):
            self.pattern_lut.SetTableValue(i, *cmap(i / 255.0))
        self.pattern_lut.Build()
        self.pattern_lut.Modified()
        self.pattern_mapper.Modified()
        if self.bar_actor is not None:
            self.bar_actor.Modified()
        self._render()

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
            # Conventions match the supplied RF script: Phi = elevation, Theta = azimuth.
            grid = selection.pivot_table(index="Phi", columns="Theta", values="PdB", aggfunc="mean")
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
            cmap = matplotlib.colormaps.get_cmap(self.cmap_combo.currentText())
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
            bar.SetTitle(self.bar_title_edit.text().strip())
            bar.SetNumberOfLabels(5)
            self.renderer.AddActor2D(bar)
            self.bar_actor = bar
            if not hasattr(self, "title_actor"):
                from vtkmodules.vtkRenderingCore import vtkTextActor
                self.title_actor = vtkTextActor()
                self.title_actor.GetTextProperty().SetFontSize(22)
                self.title_actor.GetTextProperty().SetColor(0.1, 0.1, 0.1)
                self.title_actor.GetTextProperty().SetJustificationToCentered()
                self.title_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
                self.title_actor.SetPosition(0.47, 0.955)
                self.renderer.AddActor2D(self.title_actor)
            self.update_annotations()
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
