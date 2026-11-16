# Lolth modular RF GUI

Run from the directory containing `src`:

```bash
PYTHONPATH=src python -m Lolth
```

Dependencies (VTK compatibility as in the working pcp_10–14 baseline):

```bash
pip install PyQt6 vtk==9.4.2 numpy pandas scipy matplotlib numpy-stl
```

Modules:
- `main_window.py`: application window, dataset panel, selection orchestration
- `file_reading/loader.py`: RF `.txt` reader and flat DataFrame `.pkl` reader
- `file_reading/load_dialog.py`: file grouping, frequency selection, 2× resample option
- `processing/resample.py`: 0.5° to 1° local I/Q medians, PdB recomputation
- `processing/frequency.py`: existing across-frequency bandwidth median
- `processing/cdf.py`: empirical CDF statistics
- `plotting/charts.py`: 2D linear/polar/heatmap/CDF plotting
- `plotting/export.py`: CSV/XLSX export
- `modeling/vtk_viewer.py`: native VTK 3D STL/radiation dialogs

Use File → Load and group files, then Scan groups. Choose a group and check
"Resample oversampled 0.5° angular grid to 1°" to reduce the angular grid
before frequency-median processing. The 3D viewer inherits the proven
QOpenGLWidget integration.

Data contract: `Freq` (MHz), `Phi` (azimuth deg), `Theta` (elevation deg),
`I`, `Q`, `PdB`. Text inputs use the example nine-field `A` / `B` rows.
Pickle input currently supports flattened DataFrames; nested-object pickle
structures from older custom loaders need an adapter.

This package was syntax-checked and file parsing / small-grid resampling were
smoke-tested. Full PyQt6 / VTK runtime interaction has not been tested here.

### CDF export

File → Export CDF data saves **one Excel workbook** (`cdf_plot_data.xlsx`) with three sheets: CDF Curves, Curve Statistics, and Overall Statistics. The exporter uses Python standard library ZIP/XML generation; no `artifact_tool`, `openpyxl`, or `xlsxwriter` installation is needed.

### Polarization selection
The left-panel P selector filters AA / AB / BA / BB for linear, polar, and CDF plots. Heatmap uses the separate P dropdown to show exactly one polarization per plot. Legacy pickles retain their P values; text measurements use the two quoted channel labels. CDF matches only the same polarization across Test and Synthetic.

### Angular dataset shifts and presentation scaling

**Edit → Shift Dataset Angles…** applies signed azimuth (A1/Theta) and
 elevation (E1/Phi) offsets to one selected loaded dataset. Azimuth wraps
 to [-180, 180); elevation is shifted without clipping. Angle-selection
 checkboxes are cleared after shifting; reselect the desired cuts.

**3D Plots** replaces the former View menu (both viewer actions preserved).
The CDF green/yellow/red regions now resize automatically when the x-axis
limits are changed using Matplotlib's navigation tools or axis settings.

The text reader accepts all four first/second channel pairs: AA, AB, BA, BB.
