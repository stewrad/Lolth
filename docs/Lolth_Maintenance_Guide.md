# Lolth: a beginner's guide to maintaining and extending the GUI

**Based on modular Lolth v14.** You do not need to know much PyQt6 to make small changes. The safest rule is: **put interface controls in the GUI, calculations in `processing/`, and drawing in `plotting/` or `modeling/`.**

## 1. Run the application

From the folder containing `src`:

```bash
pip install PyQt6 vtk==9.4.2 numpy pandas scipy matplotlib numpy-stl
PYTHONPATH=src python -m Lolth
```

`__main__.py` starts Qt and opens `MainWindow`. On Linux it defaults to the `xcb` Qt platform. **Keep VTK at 9.4.2 and preserve the existing `QOpenGLWidget` integration** unless you deliberately retest the 3D windows; earlier embedding approaches crashed.

## 2. Find the right file

```text
src/Lolth/
├── __main__.py                 Starts the application
├── main_window.py              Menus, left pane, checkboxes, datasets
├── file_reading/
│   ├── load_dialog.py          File grouping and import options
│   └── loader.py               Reads TXT/PKL; normalizes measurements
├── processing/
│   ├── frequency.py            Bandwidth-median processing
│   ├── resample.py             0.5° → 1° angular resampling
│   ├── shift.py                Shift and wrap dataset angles
│   └── cdf.py                  CDF statistics
├── plotting/
│   ├── charts.py               Linear, polar, heatmap and CDF plots
│   ├── coordinates.py          Phi/Theta display conversions
│   └── export.py               Excel CDF workbook export
└── modeling/
    └── vtk_viewer.py           STL and 3D radiation-pattern dialogs
```

**Examples:** New checkbox or menu → `main_window.py`. New import option → `load_dialog.py`. New numeric filter → `processing/`. Change the CDF appearance → `plotting/charts.py`. Add a 3D control → `modeling/vtk_viewer.py`.

## 3. Understand the basic flow

1. **File → Load and group files** opens `DatasetLoadDialog`. **Scan groups** calls the loader, and the dialog applies chosen frequency/resampling settings.
2. `main_window.py` stores each loaded dataset in `self.groups` with a stable ID, display name, color, visibility and measurement table (`group["flat"]`).
3. Frequency, Phi and AA/AB/BA/BB controls determine which rows `filtered_data()` returns.
4. `PlotMixin` in `plotting/charts.py` draws the active 2D plot. Test/Synthetic roles determine the pair for CDF comparisons.
5. The **3D Plots** menu opens `EmbeddedVTKDialog`, which uses VTK rather than Matplotlib.

**Important data names:** The original files use `A1` for the −180°…180° angle and `E1` for the −90°…90° angle. The GUI also uses their aliases `Theta` and `Phi`, respectively. Measurements include `Freq` (MHz), `P` (`AA`/`AB`/`BA`/`BB`), `I`, `Q`, and `PdB` (or legacy `PdBsm`). Do not discard `A1`, `E1` or `P` when processing data; legacy nested PKL files rely on those fields.

## 4. Three PyQt6 ideas you need

- **Widget:** A visible control, such as `QCheckBox`, `QComboBox` or `QPushButton`.
- **Layout:** Tells Qt where widgets go (`QVBoxLayout` stacks vertically; `QHBoxLayout` places them side by side).
- **Signal:** Connects an action to code. For example:

```python
checkbox = QCheckBox("Show grid")
checkbox.toggled.connect(self.update_plot)
layout.addWidget(checkbox)
```

Here, checking the box requests a redraw. `MainWindow` uses a short `QTimer` to combine rapid changes, rather than immediately redrawing for every click. **Use `self.update_plot()` to request a 2D refresh**, not repeated direct calls to plotting methods.

## 5. Recipe: add a feature safely

**Example: an optional power offset before plotting**

1. Add a checkbox and numeric input to `main_window.py` near the existing plot controls.
2. Store their values on `self` and connect changes to `self.update_plot`.
3. Put the calculation in a small function under `processing/` (for example, a new `power.py`).
4. In `plotting/charts.py`, apply that calculation to the values being drawn **without modifying `group["flat"]`**, unless permanent dataset editing is intentional.
5. Run the app and compare the same dataset with the setting on and off. Verify linear, polar, heatmap and CDF behavior where relevant.

For a **new plot type**, add its name to the Plot Type dropdown in `main_window.py`, create the plot method in `PlotMixin`, and add a branch to `_paint_selected_plot()` in `plotting/charts.py`. For a **new import format**, add parsing in `file_reading/loader.py` and normalize it to the same columns before passing it to the rest of the app.

## 6. Common mistakes to avoid

- **Missing imports:** If you add a widget such as `QListWidgetItem`, import it from `PyQt6.QtWidgets`.
- **Wrong method signatures:** Methods called as `self.method(...)` normally need `self` as their first parameter, unless marked `@staticmethod`.
- **Misnamed columns or array shapes:** Legacy PKLs may hold `(4, N)` arrays inside a DataFrame; do not assume every input is already a flat table. Test both TXT and PKL after changes to `loader.py`.
- **Accidentally clearing selections:** `populate_shared_selections(clear=True)` clears active selections. Do not call it for ordinary angle shifts; v14 tracks each dataset's Phi shift so chosen cuts stay visible.
- **Changing the display instead of the data:** `plotting/coordinates.py` affects display coordinates; `processing/shift.py` edits loaded angular values. Decide which behavior you actually want.
- **Freezing the interface:** Large parsing or drawing operations block the UI. Prefer the existing redraw timer and avoid unnecessary full-data scans.

## 7. Five-minute check after every change

- Launch with `PYTHONPATH=src python -m Lolth` from the correct directory.
- Load a small TXT and a legacy PKL. Check frequency, A1/Theta, E1/Phi and polarization values.
- Plot one frequency/Phi cut, then change the plot type and coordinate checkbox.
- Shift one dataset; confirm its curve moves **without clearing selections or shifting other datasets**.
- Test CDF export and open the workbook's three sheets.
- If you touched `modeling/vtk_viewer.py`, test both 3D popup windows on the target Linux machine.

**Practical habit:** Make one small change at a time, keep a working ZIP or Git commit, and use error tracebacks to locate the *first line in `src/Lolth/`* that failed. That is usually the fastest place to start debugging.
