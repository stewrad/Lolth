# Lolth v14 — Line-by-Line Source Code Guide

**Audience:** A maintainer who knows basic Python but is new to PyQt6, Matplotlib, and VTK.

**Version:** Based on the actual `Lolth_modular_preserved_shift_v14.zip` source. Line numbers refer to that version and will move if you edit the files.

## How to use this guide

1. Find the module whose job matches the feature you want to change.
2. Use the numbered source-code table to locate the exact statement.
3. Read the explanation alongside the statement; continuation lines are explained as parts of the enclosing call or expression.
4. Test the affected feature after editing. The code shown is the actual source; explanations are paraphrases, not executable code.

**Common PyQt6 vocabulary:** A *widget* is a button, label, dropdown, or window. A *layout* places widgets. A *signal* is an event, such as a button click. `.connect(...)` tells Qt what Python function to run after that event. A *callback* is that function. `self` refers to the current object. A *mixin* supplies related methods to another class through inheritance. A *DataFrame* is a labeled table. A *renderer* turns geometry and colors into an interactive 3D view.

**Application flow:** `__main__.py` starts Qt → `main_window.py` builds controls → `file_reading` loads datasets → `processing` transforms the data → `plotting/charts.py` draws 2D charts → `modeling/vtk_viewer.py` draws 3D geometry. The CDF exporter is in `plotting/export.py`.

**Data conventions:** `E1`/`Phi` represent the −90°…+90° scan; `A1`/`Theta` represent the −180°…+180° scan. `P` contains polarization labels such as AA and AB. `Freq` is in MHz and `PdB` is power in dB. Original fields are retained while plotting aliases help the UI.

---

## `src/Lolth/__main__.py`

Application bootstrap: configure Qt and launch the main window.

**Code landmarks:** `main` (line 7, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>import&nbsp;os,sys</code> | Loads the named Python package/module for use in this file. |
| 2 | <code>if&nbsp;sys.platform.startswith('linux'):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 3 | <code>&nbsp;&nbsp;&nbsp;&nbsp;os.environ.setdefault('QT_QPA_PLATFORM','xcb')</code> | Finishes this expression or function-call argument sequence. |
| 4 | <code>from&nbsp;PyQt6.QtWidgets&nbsp;import&nbsp;QApplication</code> | Imports specific classes or functions from the named module so this file can use them. |
| 5 | <code>from&nbsp;.main_window&nbsp;import&nbsp;MainWindow</code> | Imports specific classes or functions from the named module so this file can use them. |
| 6 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 7 | <code>def&nbsp;main():</code> | Defines the named function/method; indented lines below form its body. |
| 8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;app=QApplication(sys.argv)</code> | Assigns the expression on the right to `app` for later use. |
| 9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;app.setStyle('Fusion')</code> | Finishes this expression or function-call argument sequence. |
| 10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;window=MainWindow()</code> | Assigns the expression on the right to `window` for later use. |
| 11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;window.show()</code> | Displays the window/widget or requests its display. |
| 12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;app.exec()</code> | Returns this computed value to the caller; the function ends here. |
| 13 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 14 | <code>if&nbsp;__name__=='__main__':</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;sys.exit(main())</code> | Finishes this expression or function-call argument sequence. |


## `src/Lolth/main_window.py`

Main application window: menus, dataset state, filtering controls, user interactions and redraw scheduling.

**Code landmarks:** `MainWindow` (line 17, class), `__init__` (line 18, function), `_build_menu` (line 45, function), `open_shift_dialog` (line 67, function), `apply` (line 105, function), `open_stl_viewer` (line 134, function), `open_radiation_viewer` (line 142, function), `_build_ui` (line 150, function), `_on_plot_coordinate_mode_changed` (line 264, function), `open_files` (line 272, function), `_add_group_editor` (line 293, function), `rename_group` (line 333, function), `set_visibility` (line 338, function), `choose_color` (line 342, function), `set_role` (line 349, function), `remove_group` (line 362, function), `_create_checkbox_area` (line 372, function), `_populate_checks` (line 384, function), `selected_pair` (line 398, function), `populate_shared_selections` (line 403, function), `set_all_checks` (line 426, function), `selected_filters` (line 434, function), `selected_polarizations` (line 438, function), `filtered_data` (line 441, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>import&nbsp;os</code> | Loads the named Python package/module for use in this file. |
| 2 | <code>import&nbsp;sys</code> | Loads the named Python package/module for use in this file. |
| 3 | <code>from&nbsp;pathlib&nbsp;import&nbsp;Path</code> | Imports specific classes or functions from the named module so this file can use them. |
| 4 | <code>import&nbsp;numpy&nbsp;as&nbsp;np</code> | Loads the named Python package/module for use in this file. |
| 5 | <code>import&nbsp;pandas&nbsp;as&nbsp;pd</code> | Loads the named Python package/module for use in this file. |
| 6 | <code>import&nbsp;matplotlib.pyplot&nbsp;as&nbsp;plt</code> | Loads the named Python package/module for use in this file. |
| 7 | <code>from&nbsp;matplotlib.figure&nbsp;import&nbsp;Figure</code> | Imports specific classes or functions from the named module so this file can use them. |
| 8 | <code>from&nbsp;matplotlib.backends.backend_qtagg&nbsp;import&nbsp;FigureCanvasQTAgg,NavigationToolbar2QT</code> | Imports specific classes or functions from the named module so this file can use them. |
| 9 | <code>from&nbsp;PyQt6.QtCore&nbsp;import&nbsp;Qt,QTimer,QSignalBlocker</code> | Imports specific classes or functions from the named module so this file can use them. |
| 10 | <code>from&nbsp;PyQt6.QtGui&nbsp;import&nbsp;QAction,QColor</code> | Imports specific classes or functions from the named module so this file can use them. |
| 11 | <code>from&nbsp;PyQt6.QtWidgets&nbsp;import&nbsp;(QApplication,QMainWindow,QWidget,QLabel,QLineEdit,QPushButton,QListWidget,QListWidgetItem,QComboBox,QCheckBox,QGroupBox,QFileDialog,QMessageBox,QScrollArea,QVBoxLayout,QHBoxLayout,QStackedLayout,QDialog,QSplitter,QColorDialog,QDoubleSpinBox,QFormLayout)</code> | Imports specific classes or functions from the named module so this file can use them. |
| 12 | <code>from&nbsp;.modeling.vtk_viewer&nbsp;import&nbsp;EmbeddedVTKDialog</code> | Imports specific classes or functions from the named module so this file can use them. |
| 13 | <code>from&nbsp;.file_reading.load_dialog&nbsp;import&nbsp;DatasetLoadDialog</code> | Imports specific classes or functions from the named module so this file can use them. |
| 14 | <code>from&nbsp;.plotting.charts&nbsp;import&nbsp;PlotMixin</code> | Imports specific classes or functions from the named module so this file can use them. |
| 15 | <code>from&nbsp;.plotting.export&nbsp;import&nbsp;CDFExportMixin</code> | Imports specific classes or functions from the named module so this file can use them. |
| 16 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 17 | <code>class&nbsp;MainWindow(PlotMixin,&nbsp;CDFExportMixin,&nbsp;QMainWindow):</code> | Starts a class definition; any base classes in parentheses supply inherited behavior. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;__init__(self):</code> | Defines the named function/method; indented lines below form its body. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;super().__init__()</code> | Finishes this expression or function-call argument sequence. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.setWindowTitle("RF&nbsp;Dataset&nbsp;Comparison")</code> | Sets the title shown in a popup or main window border. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.resize(1480,&nbsp;880)</code> | Sets the starting dimensions of the window or widget. |
| 22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.last_dir&nbsp;=&nbsp;Path.cwd()</code> | Stores or updates `self.last_dir` on the current object so other methods can use it. |
| 23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.groups&nbsp;=&nbsp;{}&nbsp;&nbsp;#&nbsp;Unlimited&nbsp;dataset&nbsp;count,&nbsp;stable&nbsp;UUID&nbsp;keys</code> | Stores or updates `self.groups` on the current object so other methods can use it. |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.group_widgets&nbsp;=&nbsp;{}</code> | Stores or updates `self.group_widgets` on the current object so other methods can use it. |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.freq_checks&nbsp;=&nbsp;{}</code> | Stores or updates `self.freq_checks` on the current object so other methods can use it. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.phi_checks&nbsp;=&nbsp;{}</code> | Stores or updates `self.phi_checks` on the current object so other methods can use it. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.p_checks&nbsp;=&nbsp;{}</code> | Stores or updates `self.p_checks` on the current object so other methods can use it. |
| 28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.line_styles&nbsp;=&nbsp;["-",&nbsp;"--",&nbsp;"-.",&nbsp;":"]</code> | Stores or updates `self.line_styles` on the current object so other methods can use it. |
| 29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_paired&nbsp;=&nbsp;pd.DataFrame()</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_summary&nbsp;=&nbsp;pd.DataFrame()</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_plot_data&nbsp;=&nbsp;pd.DataFrame()</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_p75&nbsp;=&nbsp;None</code> | Stores or updates `self.cdf_overall_p75` on the current object so other methods can use it. |
| 33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stl_viewers&nbsp;=&nbsp;[]</code> | Stores or updates `self.stl_viewers` on the current object so other methods can use it. |
| 34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._build_menu()</code> | Finishes this expression or function-call argument sequence. |
| 35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._build_ui()</code> | Finishes this expression or function-call argument sequence. |
| 36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;UI&nbsp;signals&nbsp;only&nbsp;schedule&nbsp;a&nbsp;redraw;&nbsp;rapid&nbsp;user&nbsp;input&nbsp;is&nbsp;consolidated.</code> | Developer comment: UI signals only schedule a redraw; rapid user input is consolidated. |
| 37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._plot_timer&nbsp;=&nbsp;QTimer(self)</code> | Creates a Qt timer, used to schedule work without blocking immediate UI interaction. |
| 38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._plot_timer.setSingleShot(True)</code> | Configures whether the timer runs only once per start. |
| 39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._plot_timer.setInterval(85)</code> | Sets the timer interval in milliseconds. |
| 40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._plot_timer.timeout.connect(self._paint_selected_plot)</code> | Connects the `self._plot_timer.timeout` Qt signal to the callback inside `.connect(...)`. |
| 41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._plot_pending&nbsp;=&nbsp;False</code> | Stores or updates `self._plot_pending` on the current object so other methods can use it. |
| 42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_select.currentTextChanged.connect(self.update_plot)</code> | Connects the `self.plot_select.currentTextChanged` Qt signal to the callback inside `.connect(...)`. |
| 43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 44 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_build_menu(self):</code> | Defines the named function/method; indented lines below form its body. |
| 46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;menu&nbsp;=&nbsp;self.menuBar().addMenu("&File")</code> | Assigns the expression on the right to `menu` for later use. |
| 47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action&nbsp;=&nbsp;QAction("Load&nbsp;and&nbsp;group&nbsp;files…",&nbsp;self)</code> | Defines a menu item or keyboard-triggerable action. |
| 48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action.setShortcut("Ctrl+O")</code> | Finishes this expression or function-call argument sequence. |
| 49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action.triggered.connect(self.open_files)</code> | Connects the `action.triggered` Qt signal to the callback inside `.connect(...)`. |
| 50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;menu.addAction(action)</code> | Finishes this expression or function-call argument sequence. |
| 51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;export_action&nbsp;=&nbsp;QAction("Export&nbsp;CDF&nbsp;data…",&nbsp;self)</code> | Defines a menu item or keyboard-triggerable action. |
| 52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;export_action.setShortcut("Ctrl+Shift+E")</code> | Finishes this expression or function-call argument sequence. |
| 53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;export_action.triggered.connect(self.export_cdf_data)</code> | Connects the `export_action.triggered` Qt signal to the callback inside `.connect(...)`. |
| 54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;menu.addAction(export_action)</code> | Finishes this expression or function-call argument sequence. |
| 55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;view_menu&nbsp;=&nbsp;self.menuBar().addMenu("&3D&nbsp;Plots")</code> | Assigns the expression on the right to `view_menu` for later use. |
| 56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model_action&nbsp;=&nbsp;QAction("3D&nbsp;Model",&nbsp;self)</code> | Defines a menu item or keyboard-triggerable action. |
| 57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model_action.triggered.connect(self.open_stl_viewer)</code> | Connects the `model_action.triggered` Qt signal to the callback inside `.connect(...)`. |
| 58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;view_menu.addAction(model_action)</code> | Finishes this expression or function-call argument sequence. |
| 59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;radiation_action&nbsp;=&nbsp;QAction("3D&nbsp;Model&nbsp;-&nbsp;Radiation&nbsp;Pattern",&nbsp;self)</code> | Defines a menu item or keyboard-triggerable action. |
| 60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;radiation_action.triggered.connect(self.open_radiation_viewer)</code> | Connects the `radiation_action.triggered` Qt signal to the callback inside `.connect(...)`. |
| 61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;view_menu.addAction(radiation_action)</code> | Finishes this expression or function-call argument sequence. |
| 62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;edit_menu&nbsp;=&nbsp;self.menuBar().addMenu("&Edit")</code> | Assigns the expression on the right to `edit_menu` for later use. |
| 63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift_action&nbsp;=&nbsp;QAction("Shift&nbsp;Dataset&nbsp;Angles…",&nbsp;self)</code> | Defines a menu item or keyboard-triggerable action. |
| 64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift_action.triggered.connect(self.open_shift_dialog)</code> | Connects the `shift_action.triggered` Qt signal to the callback inside `.connect(...)`. |
| 65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;edit_menu.addAction(shift_action)</code> | Finishes this expression or function-call argument sequence. |
| 66 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;open_shift_dialog(self):</code> | Defines the named function/method; indented lines below form its body. |
| 68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Apply&nbsp;signed&nbsp;offsets&nbsp;to&nbsp;one&nbsp;dataset;&nbsp;values&nbsp;are&nbsp;degrees."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self.groups:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QMessageBox.information(self,&nbsp;"Shift&nbsp;Dataset",&nbsp;"Load&nbsp;a&nbsp;dataset&nbsp;first.")</code> | Displays an informational, warning, or error popup to the user. |
| 71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;.processing.shift&nbsp;import&nbsp;shift_dataset_angles</code> | Imports specific classes or functions from the named module so this file can use them. |
| 73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog&nbsp;=&nbsp;QDialog(self)</code> | Creates a popup dialog window for a focused action. |
| 74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog.setWindowTitle("Shift&nbsp;Dataset&nbsp;Angles")</code> | Sets the title shown in a popup or main window border. |
| 75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog.setMinimumWidth(340)</code> | Finishes this expression or function-call argument sequence. |
| 76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout&nbsp;=&nbsp;QVBoxLayout(dialog)</code> | Creates a layout stacking items vertically. |
| 77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form&nbsp;=&nbsp;QFormLayout()</code> | Creates a form layout pairing labels and input controls. |
| 78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dataset&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;key,&nbsp;group&nbsp;in&nbsp;self.groups.items():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dataset.addItem(group["name"],&nbsp;key)</code> | Adds an option to a selection widget, sometimes with hidden application data. |
| 81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form.addRow("Dataset",&nbsp;dataset)</code> | Adds a labeled field or row to the form. |
| 82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;az&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;el&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;spin&nbsp;in&nbsp;(az,&nbsp;el):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;spin.setRange(-360.0,&nbsp;360.0)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;spin.setDecimals(3)</code> | Finishes this expression or function-call argument sequence. |
| 87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;spin.setSingleStep(1.0)</code> | Finishes this expression or function-call argument sequence. |
| 88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;spin.setSuffix("°")</code> | Finishes this expression or function-call argument sequence. |
| 89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form.addRow("Azimuth&nbsp;/&nbsp;Theta&nbsp;shift",&nbsp;az)</code> | Adds a labeled field or row to the form. |
| 90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form.addRow("Elevation&nbsp;/&nbsp;Phi&nbsp;shift",&nbsp;el)</code> | Adds a labeled field or row to the form. |
| 91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addLayout(form)</code> | Nests one layout inside another layout. |
| 92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;note&nbsp;=&nbsp;QLabel("Moves&nbsp;the&nbsp;selected&nbsp;dataset&nbsp;while&nbsp;preserving&nbsp;current&nbsp;2D&nbsp;plot&nbsp;"</code> | Creates a text label shown in the interface. |
| 93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"selections.&nbsp;Theta&nbsp;wraps&nbsp;over&nbsp;360°&nbsp;and&nbsp;Phi&nbsp;over&nbsp;180°.&nbsp;"</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"The&nbsp;original&nbsp;E1/A1&nbsp;columns&nbsp;remain&nbsp;synchronized.")</code> | Finishes this expression or function-call argument sequence. |
| 95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;note.setWordWrap(True)</code> | Finishes this expression or function-call argument sequence. |
| 96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(note)</code> | Inserts the specified widget into the surrounding layout. |
| 97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buttons&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;apply_button&nbsp;=&nbsp;QPushButton("Apply&nbsp;Shift")</code> | Creates a clickable button. |
| 99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cancel_button&nbsp;=&nbsp;QPushButton("Cancel")</code> | Creates a clickable button. |
| 100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buttons.addWidget(apply_button)</code> | Inserts the specified widget into the surrounding layout. |
| 101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buttons.addWidget(cancel_button)</code> | Inserts the specified widget into the surrounding layout. |
| 102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addLayout(buttons)</code> | Nests one layout inside another layout. |
| 103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cancel_button.clicked.connect(dialog.reject)</code> | Connects the `cancel_button.clicked` Qt signal to the callback inside `.connect(...)`. |
| 104 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;apply():</code> | Defines the named function/method; indented lines below form its body. |
| 106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key&nbsp;=&nbsp;dataset.currentData()</code> | Assigns the expression on the right to `key` for later use. |
| 107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group&nbsp;=&nbsp;self.groups.get(key)</code> | Assigns the expression on the right to `group` for later use. |
| 108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;group&nbsp;is&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;az_delta,&nbsp;el_delta&nbsp;=&nbsp;az.value(),&nbsp;el.value()</code> | Assigns the expression on the right to `az_delta, el_delta` for later use. |
| 111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;az_delta&nbsp;and&nbsp;not&nbsp;el_delta:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog.accept()</code> | Finishes this expression or function-call argument sequence. |
| 113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Anchor&nbsp;the&nbsp;shared&nbsp;Phi&nbsp;selector&nbsp;to&nbsp;the&nbsp;dataset's&nbsp;original&nbsp;cuts.</code> | Developer comment: Anchor the shared Phi selector to the dataset's original cuts. |
| 115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Each&nbsp;dataset&nbsp;keeps&nbsp;its&nbsp;own&nbsp;cumulative&nbsp;offset:&nbsp;checked&nbsp;labels</code> | Developer comment: Each dataset keeps its own cumulative offset: checked labels |
| 116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;continue&nbsp;to&nbsp;follow&nbsp;shifted&nbsp;samples&nbsp;without&nbsp;changing&nbsp;the&nbsp;cuts</code> | Developer comment: continue to follow shifted samples without changing the cuts |
| 117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;selected&nbsp;in&nbsp;other&nbsp;datasets.</code> | Developer comment: selected in other datasets. |
| 118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"phi_options"&nbsp;not&nbsp;in&nbsp;group:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group["phi_options"]&nbsp;=&nbsp;np.sort(group["flat"]["Phi"].dropna().unique())</code> | Gets the distinct values in a column, useful for frequency or angle choices. |
| 120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift_dataset_angles(group["flat"],&nbsp;az_delta,&nbsp;el_delta)</code> | Finishes this expression or function-call argument sequence. |
| 121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group["phi_shift_offset"]&nbsp;=&nbsp;(</code> | Opens or closes a multi-line expression or collection. |
| 122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;float(group.get("phi_shift_offset",&nbsp;0.0))&nbsp;+&nbsp;el_delta</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)&nbsp;%&nbsp;180.0</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;No&nbsp;call&nbsp;to&nbsp;populate_shared_selections(clear=True):&nbsp;keep&nbsp;every</code> | Developer comment: No call to populate_shared_selections(clear=True): keep every |
| 125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;frequency/Phi/polarization&nbsp;checkbox&nbsp;and&nbsp;every&nbsp;other&nbsp;dataset.</code> | Developer comment: frequency/Phi/polarization checkbox and every other dataset. |
| 126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.statusBar().showMessage(</code> | Opens or closes a multi-line expression or collection. |
| 128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f"Shifted&nbsp;{group['name']}:&nbsp;azimuth&nbsp;{az_delta:+g}°,&nbsp;elevation&nbsp;{el_delta:+g}°")</code> | Finishes this expression or function-call argument sequence. |
| 129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog.accept()</code> | Finishes this expression or function-call argument sequence. |
| 130 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;apply_button.clicked.connect(apply)</code> | Connects the `apply_button.clicked` Qt signal to the callback inside `.connect(...)`. |
| 132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog.exec()</code> | Opens a modal dialog or starts an event loop, depending on the object. |
| 133 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;open_stl_viewer(self):</code> | Defines the named function/method; indented lines below form its body. |
| 135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup&nbsp;=&nbsp;EmbeddedVTKDialog(self,&nbsp;radiation=False)</code> | Assigns the expression on the right to `popup` for later use. |
| 136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,&nbsp;True)</code> | Finishes this expression or function-call argument sequence. |
| 137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup.destroyed.connect(lambda&nbsp;*_:&nbsp;self.stl_viewers.remove(popup)</code> | Connects the `popup.destroyed` Qt signal to the callback inside `.connect(...)`. |
| 138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;popup&nbsp;in&nbsp;self.stl_viewers&nbsp;else&nbsp;None)</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stl_viewers.append(popup)</code> | Finishes this expression or function-call argument sequence. |
| 140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup.show()</code> | Displays the window/widget or requests its display. |
| 141 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;open_radiation_viewer(self):</code> | Defines the named function/method; indented lines below form its body. |
| 143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup&nbsp;=&nbsp;EmbeddedVTKDialog(self,&nbsp;radiation=True)</code> | Assigns the expression on the right to `popup` for later use. |
| 144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,&nbsp;True)</code> | Finishes this expression or function-call argument sequence. |
| 145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup.destroyed.connect(lambda&nbsp;*_:&nbsp;self.stl_viewers.remove(popup)</code> | Connects the `popup.destroyed` Qt signal to the callback inside `.connect(...)`. |
| 146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;popup&nbsp;in&nbsp;self.stl_viewers&nbsp;else&nbsp;None)</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stl_viewers.append(popup)</code> | Finishes this expression or function-call argument sequence. |
| 148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup.show()</code> | Displays the window/widget or requests its display. |
| 149 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_build_ui(self):</code> | Defines the named function/method; indented lines below form its body. |
| 151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;splitter&nbsp;=&nbsp;QSplitter(Qt.Orientation.Horizontal)</code> | Assigns the expression on the right to `splitter` for later use. |
| 152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left_panel&nbsp;=&nbsp;QWidget()</code> | Assigns the expression on the right to `left_panel` for later use. |
| 153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left&nbsp;=&nbsp;QVBoxLayout(left_panel)</code> | Creates a layout stacking items vertically. |
| 154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;add&nbsp;=&nbsp;QPushButton("Load&nbsp;/&nbsp;Group&nbsp;Files…")</code> | Creates a clickable button. |
| 155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;add.clicked.connect(self.open_files)</code> | Connects the `add.clicked` Qt signal to the callback inside `.connect(...)`. |
| 156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(add)</code> | Inserts the specified widget into the surrounding layout. |
| 157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(QLabel("Datasets&nbsp;(rename,&nbsp;recolor,&nbsp;show/hide,&nbsp;assign&nbsp;CDF&nbsp;roles):"))</code> | Creates a text label shown in the interface. |
| 158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Only&nbsp;the&nbsp;dataset&nbsp;cards&nbsp;scroll:&nbsp;the&nbsp;selectors&nbsp;stay&nbsp;pinned&nbsp;to&nbsp;the&nbsp;bottom&nbsp;left.</code> | Developer comment: Only the dataset cards scroll: the selectors stay pinned to the bottom left. |
| 159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dataset_scroll&nbsp;=&nbsp;QScrollArea()</code> | Assigns the expression on the right to `dataset_scroll` for later use. |
| 160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dataset_scroll.setWidgetResizable(True)</code> | Finishes this expression or function-call argument sequence. |
| 161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dataset_scroll.setMinimumHeight(120)</code> | Finishes this expression or function-call argument sequence. |
| 162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_holder&nbsp;=&nbsp;QWidget()</code> | Stores or updates `self.dataset_holder` on the current object so other methods can use it. |
| 163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_layout&nbsp;=&nbsp;QVBoxLayout(self.dataset_holder)</code> | Creates a layout stacking items vertically. |
| 164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_layout.setContentsMargins(0,&nbsp;0,&nbsp;0,&nbsp;0)</code> | Finishes this expression or function-call argument sequence. |
| 165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_layout.setAlignment(Qt.AlignmentFlag.AlignTop)</code> | Finishes this expression or function-call argument sequence. |
| 166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dataset_scroll.setWidget(self.dataset_holder)</code> | Finishes this expression or function-call argument sequence. |
| 167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(dataset_scroll,&nbsp;1)</code> | Inserts the specified widget into the surrounding layout. |
| 168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(QLabel("Plot&nbsp;Type"))</code> | Creates a text label shown in the interface. |
| 169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_select&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_select.addItems(["Linear&nbsp;Plot",&nbsp;"Polar&nbsp;Plot",&nbsp;"CDF",&nbsp;"Heatmap"])</code> | Adds several options to a dropdown in one operation. |
| 171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(self.plot_select)</code> | Inserts the specified widget into the surrounding layout. |
| 172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Presentation-only&nbsp;coordinate&nbsp;convention.&nbsp;Internal&nbsp;columns&nbsp;remain</code> | Developer comment: Presentation-only coordinate convention. Internal columns remain |
| 173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Theta&nbsp;(azimuth)&nbsp;and&nbsp;Phi&nbsp;(elevation)&nbsp;for&nbsp;all&nbsp;processing&nbsp;operations.</code> | Developer comment: Theta (azimuth) and Phi (elevation) for all processing operations. |
| 174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_phi_theta&nbsp;=&nbsp;QCheckBox("Plot&nbsp;Phi-Theta")</code> | Creates a checkbox the user can toggle on or off. |
| 175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_phi_theta.setChecked(True)&nbsp;&nbsp;#&nbsp;Retain&nbsp;the&nbsp;original&nbsp;plot&nbsp;appearance.</code> | Sets whether this checkbox is initially or currently selected. |
| 176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_phi_theta.setToolTip(</code> | Opens or closes a multi-line expression or collection. |
| 177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Checked:&nbsp;use&nbsp;measured&nbsp;Phi/Theta&nbsp;scan&nbsp;coordinates.&nbsp;"</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Unchecked:&nbsp;transform&nbsp;scan&nbsp;directions&nbsp;into&nbsp;Azimuth/Elevation.&nbsp;"</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Raw&nbsp;RF&nbsp;samples&nbsp;are&nbsp;not&nbsp;modified."</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | Opens or closes a multi-line expression or collection. |
| 181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_phi_theta.toggled.connect(self._on_plot_coordinate_mode_changed)</code> | Connects the `self.plot_phi_theta.toggled` Qt signal to the callback inside `.connect(...)`. |
| 182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(self.plot_phi_theta)</code> | Inserts the specified widget into the surrounding layout. |
| 183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_controls&nbsp;=&nbsp;QWidget()</code> | Stores or updates `self.heatmap_controls` on the current object so other methods can use it. |
| 184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heatmap_row&nbsp;=&nbsp;QHBoxLayout(self.heatmap_controls)</code> | Creates a layout arranging items horizontally. |
| 185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heatmap_row.setContentsMargins(0,&nbsp;0,&nbsp;0,&nbsp;0)</code> | Finishes this expression or function-call argument sequence. |
| 186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heatmap_row.addWidget(QLabel("Heatmap&nbsp;dataset:"))</code> | Creates a text label shown in the interface. |
| 187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_dataset_select&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_dataset_select.currentIndexChanged.connect(self.update_plot)</code> | Connects the `self.heatmap_dataset_select.currentIndexChanged` Qt signal to the callback inside `.connect(...)`. |
| 189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heatmap_row.addWidget(self.heatmap_dataset_select,&nbsp;1)</code> | Inserts the specified widget into the surrounding layout. |
| 190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_p_select&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_p_select.addItems(["AA",&nbsp;"AB",&nbsp;"BA",&nbsp;"BB"])</code> | Adds several options to a dropdown in one operation. |
| 192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_p_select.currentTextChanged.connect(self.update_plot)</code> | Connects the `self.heatmap_p_select.currentTextChanged` Qt signal to the callback inside `.connect(...)`. |
| 193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heatmap_row.addWidget(QLabel("P:"))</code> | Creates a text label shown in the interface. |
| 194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heatmap_row.addWidget(self.heatmap_p_select)</code> | Inserts the specified widget into the surrounding layout. |
| 195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(self.heatmap_controls)</code> | Inserts the specified widget into the surrounding layout. |
| 196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_controls.setVisible(False)</code> | Shows or hides the widget. |
| 197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.match_label&nbsp;=&nbsp;QLabel("Load&nbsp;datasets&nbsp;to&nbsp;begin.")</code> | Creates a text label shown in the interface. |
| 198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.match_label.setWordWrap(True)</code> | Finishes this expression or function-call argument sequence. |
| 199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(self.match_label)</code> | Inserts the specified widget into the surrounding layout. |
| 200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(QLabel("Frequency&nbsp;Selection&nbsp;(across&nbsp;loaded&nbsp;datasets)"))</code> | Creates a text label shown in the interface. |
| 201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.freq_check_layout,&nbsp;freq_area&nbsp;=&nbsp;self._create_checkbox_area()</code> | Stores or updates `self.freq_check_layout, freq_area` on the current object so other methods can use it. |
| 202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(freq_area)</code> | Inserts the specified widget into the surrounding layout. |
| 203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;freq_row&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;label,&nbsp;on&nbsp;in&nbsp;(("Select&nbsp;All",&nbsp;True),&nbsp;("Clear&nbsp;All",&nbsp;False)):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;button&nbsp;=&nbsp;QPushButton(label)</code> | Creates a clickable button. |
| 206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;button.clicked.connect(lambda&nbsp;checked=False,&nbsp;value=on:&nbsp;self.set_all_checks(value,&nbsp;"freq"))</code> | Connects the `button.clicked` Qt signal to the callback inside `.connect(...)`. |
| 207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;freq_row.addWidget(button)</code> | Inserts the specified widget into the surrounding layout. |
| 208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addLayout(freq_row)</code> | Nests one layout inside another layout. |
| 209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.phi_selection_label&nbsp;=&nbsp;QLabel("Phi&nbsp;Selection&nbsp;(across&nbsp;loaded&nbsp;datasets)")</code> | Creates a text label shown in the interface. |
| 210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(self.phi_selection_label)</code> | Inserts the specified widget into the surrounding layout. |
| 211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.phi_check_layout,&nbsp;phi_area&nbsp;=&nbsp;self._create_checkbox_area()</code> | Stores or updates `self.phi_check_layout, phi_area` on the current object so other methods can use it. |
| 212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(phi_area)</code> | Inserts the specified widget into the surrounding layout. |
| 213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi_row&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;label,&nbsp;on&nbsp;in&nbsp;(("Select&nbsp;All",&nbsp;True),&nbsp;("Clear&nbsp;All",&nbsp;False)):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;button&nbsp;=&nbsp;QPushButton(label)</code> | Creates a clickable button. |
| 216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;button.clicked.connect(lambda&nbsp;checked=False,&nbsp;value=on:&nbsp;self.set_all_checks(value,&nbsp;"phi"))</code> | Connects the `button.clicked` Qt signal to the callback inside `.connect(...)`. |
| 217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi_row.addWidget(button)</code> | Inserts the specified widget into the surrounding layout. |
| 218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addLayout(phi_row)</code> | Nests one layout inside another layout. |
| 219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(QLabel("Polarization&nbsp;Selection&nbsp;(P)"))</code> | Creates a text label shown in the interface. |
| 220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;p_row&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;pol&nbsp;in&nbsp;("AA",&nbsp;"AB",&nbsp;"BA",&nbsp;"BB"):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox&nbsp;=&nbsp;QCheckBox(pol)</code> | Creates a checkbox the user can toggle on or off. |
| 223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox.setChecked(True)</code> | Sets whether this checkbox is initially or currently selected. |
| 224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox.toggled.connect(self.update_plot)</code> | Connects the `checkbox.toggled` Qt signal to the callback inside `.connect(...)`. |
| 225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.p_checks[pol]&nbsp;=&nbsp;checkbox</code> | Stores or updates `self.p_checks[pol]` on the current object so other methods can use it. |
| 226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;p_row.addWidget(checkbox)</code> | Inserts the specified widget into the surrounding layout. |
| 227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addLayout(p_row)</code> | Nests one layout inside another layout. |
| 228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left_panel.setMinimumWidth(365)</code> | Finishes this expression or function-call argument sequence. |
| 229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;splitter.addWidget(left_panel)</code> | Inserts the specified widget into the surrounding layout. |
| 230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right&nbsp;=&nbsp;QWidget()</code> | Assigns the expression on the right to `right` for later use. |
| 231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right_layout&nbsp;=&nbsp;QVBoxLayout(right)</code> | Creates a layout stacking items vertically. |
| 232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right_layout.setContentsMargins(0,&nbsp;0,&nbsp;0,&nbsp;0)</code> | Finishes this expression or function-call argument sequence. |
| 233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_label&nbsp;=&nbsp;QLabel("Overall&nbsp;\|ΔdB\|&nbsp;P75:&nbsp;—")</code> | Creates a text label shown in the interface. |
| 234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_label.setAlignment(Qt.AlignmentFlag.AlignRight)</code> | Finishes this expression or function-call argument sequence. |
| 235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_label.setStyleSheet("font-weight:&nbsp;600;&nbsp;padding:&nbsp;5px&nbsp;12px;")</code> | Finishes this expression or function-call argument sequence. |
| 236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_label.hide()</code> | Finishes this expression or function-call argument sequence. |
| 237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right_layout.addWidget(self.cdf_overall_label)</code> | Inserts the specified widget into the surrounding layout. |
| 238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;plot_stack_holder&nbsp;=&nbsp;QWidget()</code> | Assigns the expression on the right to `plot_stack_holder` for later use. |
| 239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stacklayout&nbsp;=&nbsp;QStackedLayout(plot_stack_holder)</code> | Stores or updates `self.stacklayout` on the current object so other methods can use it. |
| 240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stacklayout.setContentsMargins(0,&nbsp;0,&nbsp;0,&nbsp;0)</code> | Finishes this expression or function-call argument sequence. |
| 241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right_layout.addWidget(plot_stack_holder,&nbsp;1)</code> | Inserts the specified widget into the surrounding layout. |
| 242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_pages&nbsp;=&nbsp;{}</code> | Stores or updates `self.plot_pages` on the current object so other methods can use it. |
| 243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.toolbars&nbsp;=&nbsp;{}</code> | Stores or updates `self.toolbars` on the current object so other methods can use it. |
| 244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.linear_canvas&nbsp;=&nbsp;FigureCanvasQTAgg(Figure())</code> | Stores or updates `self.linear_canvas` on the current object so other methods can use it. |
| 245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.polar_canvas&nbsp;=&nbsp;FigureCanvasQTAgg(Figure())</code> | Stores or updates `self.polar_canvas` on the current object so other methods can use it. |
| 246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_canvas&nbsp;=&nbsp;FigureCanvasQTAgg(Figure())</code> | Stores or updates `self.cdf_canvas` on the current object so other methods can use it. |
| 247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_canvas&nbsp;=&nbsp;FigureCanvasQTAgg(Figure())</code> | Stores or updates `self.heatmap_canvas` on the current object so other methods can use it. |
| 248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;canvas&nbsp;in&nbsp;(self.linear_canvas,&nbsp;self.polar_canvas,&nbsp;self.cdf_canvas,&nbsp;self.heatmap_canvas):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;page&nbsp;=&nbsp;QWidget()</code> | Assigns the expression on the right to `page` for later use. |
| 250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout&nbsp;=&nbsp;QVBoxLayout(page)</code> | Creates a layout stacking items vertically. |
| 251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.setContentsMargins(0,&nbsp;0,&nbsp;0,&nbsp;0)</code> | Finishes this expression or function-call argument sequence. |
| 252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;toolbar&nbsp;=&nbsp;NavigationToolbar2QT(canvas,&nbsp;page)</code> | Assigns the expression on the right to `toolbar` for later use. |
| 253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(toolbar)</code> | Inserts the specified widget into the surrounding layout. |
| 254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(canvas,&nbsp;1)</code> | Inserts the specified widget into the surrounding layout. |
| 255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_pages[canvas]&nbsp;=&nbsp;page</code> | Stores or updates `self.plot_pages[canvas]` on the current object so other methods can use it. |
| 256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.toolbars[canvas]&nbsp;=&nbsp;toolbar</code> | Stores or updates `self.toolbars[canvas]` on the current object so other methods can use it. |
| 257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stacklayout.addWidget(page)</code> | Inserts the specified widget into the surrounding layout. |
| 258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;splitter.addWidget(right)</code> | Inserts the specified widget into the surrounding layout. |
| 259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;splitter.setStretchFactor(0,&nbsp;0)</code> | Finishes this expression or function-call argument sequence. |
| 260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;splitter.setStretchFactor(1,&nbsp;1)</code> | Finishes this expression or function-call argument sequence. |
| 261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;splitter.setSizes([410,&nbsp;1060])</code> | Finishes this expression or function-call argument sequence. |
| 262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.setCentralWidget(splitter)</code> | Finishes this expression or function-call argument sequence. |
| 263 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_on_plot_coordinate_mode_changed(self,&nbsp;*_):</code> | Defines the named function/method; indented lines below form its body. |
| 265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Replot&nbsp;transformed&nbsp;scan&nbsp;positions&nbsp;without&nbsp;modifying&nbsp;original&nbsp;RF&nbsp;data."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.plot_phi_theta.isChecked():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.phi_selection_label.setText("Phi&nbsp;Selection&nbsp;(across&nbsp;loaded&nbsp;datasets)")</code> | Updates text shown in an existing widget. |
| 268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.phi_selection_label.setText("Elevation&nbsp;Selection&nbsp;(across&nbsp;loaded&nbsp;datasets)")</code> | Updates text shown in an existing widget. |
| 270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 271 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;open_files(self):</code> | Defines the named function/method; indented lines below form its body. |
| 273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;paths,&nbsp;_&nbsp;=&nbsp;QFileDialog.getOpenFileNames(</code> | Opens a file picker or a save-file picker. |
| 274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,&nbsp;"Select&nbsp;RF&nbsp;files",&nbsp;str(self.last_dir),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"RF&nbsp;Data&nbsp;(*.txt&nbsp;*.pkl);;All&nbsp;Files&nbsp;(*)")</code> | Finishes this expression or function-call argument sequence. |
| 276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;paths:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;popup&nbsp;=&nbsp;DatasetLoadDialog(paths,&nbsp;self)</code> | Assigns the expression on the right to `popup` for later use. |
| 279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;popup.exec()&nbsp;!=&nbsp;QDialog.DialogCode.Accepted:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.last_dir&nbsp;=&nbsp;Path(paths[-1]).parent</code> | Stores or updates `self.last_dir` on the current object so other methods can use it. |
| 282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;group&nbsp;in&nbsp;popup.result_groups:</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;palette&nbsp;=&nbsp;plt.get_cmap("tab20")</code> | Assigns the expression on the right to `palette` for later use. |
| 284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rgb&nbsp;=&nbsp;palette(len(self.groups)&nbsp;%&nbsp;20)</code> | Assigns the expression on the right to `rgb` for later use. |
| 285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group["color"]&nbsp;=&nbsp;QColor.fromRgbF(*rgb[:3]).name()</code> | Assigns the expression on the right to `group["color"]` for later use. |
| 286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.groups[group["id"]]&nbsp;=&nbsp;group</code> | Stores or updates `self.groups[group["id"]]` on the current object so other methods can use it. |
| 287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._add_group_editor(group["id"])</code> | Finishes this expression or function-call argument sequence. |
| 288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.populate_shared_selections(clear=True)</code> | Stores or updates `self.populate_shared_selections(clear` on the current object so other methods can use it. |
| 289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_heatmap_datasets()</code> | Finishes this expression or function-call argument sequence. |
| 290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.statusBar().showMessage(f"Added&nbsp;{len(popup.result_groups)}&nbsp;datasets;&nbsp;frequency/Phi&nbsp;selections&nbsp;cleared")</code> | Finishes this expression or function-call argument sequence. |
| 292 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_add_group_editor(self,&nbsp;key):</code> | Defines the named function/method; indented lines below form its body. |
| 294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group&nbsp;=&nbsp;self.groups[key]</code> | Assigns the expression on the right to `group` for later use. |
| 295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;box&nbsp;=&nbsp;QGroupBox()</code> | Assigns the expression on the right to `box` for later use. |
| 296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outer&nbsp;=&nbsp;QVBoxLayout(box)</code> | Creates a layout stacking items vertically. |
| 297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;visible&nbsp;=&nbsp;QCheckBox()</code> | Creates a checkbox the user can toggle on or off. |
| 299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;visible.setChecked(True)</code> | Sets whether this checkbox is initially or currently selected. |
| 300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;visible.setToolTip("Show&nbsp;dataset&nbsp;on&nbsp;linear&nbsp;and&nbsp;polar&nbsp;plots")</code> | Finishes this expression or function-call argument sequence. |
| 301 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;visible.toggled.connect(lambda&nbsp;checked,&nbsp;k=key:&nbsp;self.set_visibility(k,&nbsp;checked))</code> | Connects the `visible.toggled` Qt signal to the callback inside `.connect(...)`. |
| 302 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name_edit&nbsp;=&nbsp;QLineEdit(group["name"])</code> | Creates a single-line text input. |
| 303 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name_edit.setToolTip("Editable&nbsp;dataset&nbsp;name")</code> | Finishes this expression or function-call argument sequence. |
| 304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name_edit.textChanged.connect(lambda&nbsp;text,&nbsp;k=key:&nbsp;self.rename_group(k,&nbsp;text))</code> | Connects the `name_edit.textChanged` Qt signal to the callback inside `.connect(...)`. |
| 305 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color&nbsp;=&nbsp;QPushButton("Color")</code> | Creates a clickable button. |
| 306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color.setStyleSheet(f"background-color:&nbsp;{group['color']};")</code> | Finishes this expression or function-call argument sequence. |
| 307 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color.clicked.connect(lambda&nbsp;checked=False,&nbsp;k=key:&nbsp;self.choose_color(k))</code> | Connects the `color.clicked` Qt signal to the callback inside `.connect(...)`. |
| 308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(visible)</code> | Inserts the specified widget into the surrounding layout. |
| 309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(name_edit,&nbsp;1)</code> | Inserts the specified widget into the surrounding layout. |
| 310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(color)</code> | Inserts the specified widget into the surrounding layout. |
| 311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outer.addLayout(row)</code> | Nests one layout inside another layout. |
| 312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row2&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row2.addWidget(QLabel("CDF&nbsp;role:"))</code> | Creates a text label shown in the interface. |
| 314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;role&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;role.addItems(["None",&nbsp;"Test",&nbsp;"Synthetic"])</code> | Adds several options to a dropdown in one operation. |
| 316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;role.currentTextChanged.connect(lambda&nbsp;text,&nbsp;k=key:&nbsp;self.set_role(k,&nbsp;text))</code> | Connects the `role.currentTextChanged` Qt signal to the callback inside `.connect(...)`. |
| 317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row2.addWidget(role,&nbsp;1)</code> | Inserts the specified widget into the surrounding layout. |
| 318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;remove&nbsp;=&nbsp;QPushButton("Remove")</code> | Creates a clickable button. |
| 319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;remove.clicked.connect(lambda&nbsp;checked=False,&nbsp;k=key:&nbsp;self.remove_group(k))</code> | Connects the `remove.clicked` Qt signal to the callback inside `.connect(...)`. |
| 320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row2.addWidget(remove)</code> | Inserts the specified widget into the surrounding layout. |
| 321 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outer.addLayout(row2)</code> | Nests one layout inside another layout. |
| 322 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;files&nbsp;=&nbsp;QLabel(f"{len(group['paths'])}&nbsp;file(s)&nbsp;\|&nbsp;"</code> | Creates a text label shown in the interface. |
| 323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f"{len(group['flat']):,}&nbsp;samples&nbsp;\|&nbsp;"</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f"{len(group['frequencies'])}&nbsp;frequencies")</code> | Finishes this expression or function-call argument sequence. |
| 325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;files.setToolTip("\\n".join(group["paths"]))</code> | Finishes this expression or function-call argument sequence. |
| 326 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outer.addWidget(files)</code> | Inserts the specified widget into the surrounding layout. |
| 327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;group["bandwidth"]&nbsp;&gt;&nbsp;0:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outer.addWidget(QLabel(f"Frequency&nbsp;median:&nbsp;{group['bandwidth']:g}&nbsp;{group['unit']}"))</code> | Creates a text label shown in the interface. |
| 329 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_layout.addWidget(box)</code> | Inserts the specified widget into the surrounding layout. |
| 330 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.group_widgets[key]&nbsp;=&nbsp;dict(box=box,&nbsp;name=name_edit,&nbsp;color=color,</code> | Stores or updates `self.group_widgets[key]` on the current object so other methods can use it. |
| 331 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;role=role,&nbsp;visible=visible)</code> | Assigns the expression on the right to `role` for later use. |
| 332 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;rename_group(self,&nbsp;key,&nbsp;text):</code> | Defines the named function/method; indented lines below form its body. |
| 334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.groups[key]["name"]&nbsp;=&nbsp;text.strip()&nbsp;or&nbsp;"Unnamed&nbsp;dataset"</code> | Stores or updates `self.groups[key]["name"]` on the current object so other methods can use it. |
| 335 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_heatmap_datasets()</code> | Finishes this expression or function-call argument sequence. |
| 336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 337 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;set_visibility(self,&nbsp;key,&nbsp;checked):</code> | Defines the named function/method; indented lines below form its body. |
| 339 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.groups[key]["visible"]&nbsp;=&nbsp;checked</code> | Stores or updates `self.groups[key]["visible"]` on the current object so other methods can use it. |
| 340 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 341 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;choose_color(self,&nbsp;key):</code> | Defines the named function/method; indented lines below form its body. |
| 343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color&nbsp;=&nbsp;QColorDialog.getColor(QColor(self.groups[key]["color"]),&nbsp;self,&nbsp;"Dataset&nbsp;plot&nbsp;color")</code> | Opens Qt’s color picker. |
| 344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;color.isValid():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 345 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.groups[key]["color"]&nbsp;=&nbsp;color.name()</code> | Stores or updates `self.groups[key]["color"]` on the current object so other methods can use it. |
| 346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.group_widgets[key]["color"].setStyleSheet(f"background-color:&nbsp;{color.name()};")</code> | Finishes this expression or function-call argument sequence. |
| 347 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 348 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;set_role(self,&nbsp;key,&nbsp;role):</code> | Defines the named function/method; indented lines below form its body. |
| 350 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;role&nbsp;!=&nbsp;"None":</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 351 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;other_key,&nbsp;other&nbsp;in&nbsp;self.groups.items():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 352 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;other_key&nbsp;!=&nbsp;key&nbsp;and&nbsp;other["role"]&nbsp;==&nbsp;role:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 353 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;other["role"]&nbsp;=&nbsp;"None"</code> | Assigns the expression on the right to `other["role"]` for later use. |
| 354 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;widget&nbsp;=&nbsp;self.group_widgets[other_key]["role"]</code> | Assigns the expression on the right to `widget` for later use. |
| 355 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;widget.blockSignals(True)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 356 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;widget.setCurrentText("None")</code> | Changes the current visible/selected item in a Qt control. |
| 357 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;widget.blockSignals(False)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 358 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.groups[key]["role"]&nbsp;=&nbsp;role</code> | Stores or updates `self.groups[key]["role"]` on the current object so other methods can use it. |
| 359 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.populate_shared_selections()</code> | Finishes this expression or function-call argument sequence. |
| 360 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 361 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 362 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;remove_group(self,&nbsp;key):</code> | Defines the named function/method; indented lines below form its body. |
| 363 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;widget&nbsp;=&nbsp;self.group_widgets.pop(key)["box"]</code> | Assigns the expression on the right to `widget` for later use. |
| 364 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_layout.removeWidget(widget)</code> | Finishes this expression or function-call argument sequence. |
| 365 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;widget.deleteLater()</code> | Finishes this expression or function-call argument sequence. |
| 366 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;del&nbsp;self.groups[key]</code> | Finishes this expression or function-call argument sequence. |
| 367 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.populate_shared_selections()</code> | Finishes this expression or function-call argument sequence. |
| 368 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_heatmap_datasets()</code> | Finishes this expression or function-call argument sequence. |
| 369 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 370 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 371 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | Decorator: this method does not receive an automatic `self` argument. |
| 372 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_create_checkbox_area():</code> | Defines the named function/method; indented lines below form its body. |
| 373 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;widget&nbsp;=&nbsp;QWidget()</code> | Assigns the expression on the right to `widget` for later use. |
| 374 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout&nbsp;=&nbsp;QVBoxLayout(widget)</code> | Creates a layout stacking items vertically. |
| 375 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.setAlignment(Qt.AlignmentFlag.AlignTop)</code> | Finishes this expression or function-call argument sequence. |
| 376 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.setContentsMargins(4,&nbsp;4,&nbsp;4,&nbsp;4)</code> | Finishes this expression or function-call argument sequence. |
| 377 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scroll&nbsp;=&nbsp;QScrollArea()</code> | Assigns the expression on the right to `scroll` for later use. |
| 378 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scroll.setWidgetResizable(True)</code> | Finishes this expression or function-call argument sequence. |
| 379 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scroll.setMinimumHeight(95)</code> | Finishes this expression or function-call argument sequence. |
| 380 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scroll.setMaximumHeight(160)</code> | Finishes this expression or function-call argument sequence. |
| 381 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scroll.setWidget(widget)</code> | Finishes this expression or function-call argument sequence. |
| 382 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;layout,&nbsp;scroll</code> | Returns this computed value to the caller; the function ends here. |
| 383 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 384 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_populate_checks(self,&nbsp;layout,&nbsp;mapping,&nbsp;values,&nbsp;suffix,&nbsp;clear=False):</code> | Defines the named function/method; indented lines below form its body. |
| 385 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;previous&nbsp;=&nbsp;{}&nbsp;if&nbsp;clear&nbsp;else&nbsp;{key:&nbsp;checkbox.isChecked()&nbsp;for&nbsp;key,&nbsp;checkbox&nbsp;in&nbsp;mapping.items()}</code> | Assigns the expression on the right to `previous` for later use. |
| 386 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;while&nbsp;layout.count():</code> | Repeats the indented block while the condition remains true. |
| 387 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;child&nbsp;=&nbsp;layout.takeAt(0)</code> | Assigns the expression on the right to `child` for later use. |
| 388 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;child.widget():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 389 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;child.widget().deleteLater()</code> | Finishes this expression or function-call argument sequence. |
| 390 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapping.clear()</code> | Finishes this expression or function-call argument sequence. |
| 391 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;value&nbsp;in&nbsp;values:</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 392 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox&nbsp;=&nbsp;QCheckBox(f"{value:g}{suffix}")</code> | Creates a checkbox the user can toggle on or off. |
| 393 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox.setChecked(previous.get(value,&nbsp;False))</code> | Sets whether this checkbox is initially or currently selected. |
| 394 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox.toggled.connect(self.update_plot)</code> | Connects the `checkbox.toggled` Qt signal to the callback inside `.connect(...)`. |
| 395 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(checkbox)</code> | Inserts the specified widget into the surrounding layout. |
| 396 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapping[value]&nbsp;=&nbsp;checkbox</code> | Assigns the expression on the right to `mapping[value]` for later use. |
| 397 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 398 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;selected_pair(self):</code> | Defines the named function/method; indented lines below form its body. |
| 399 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test&nbsp;=&nbsp;next((x&nbsp;for&nbsp;x&nbsp;in&nbsp;self.groups.values()&nbsp;if&nbsp;x["role"]&nbsp;==&nbsp;"Test"),&nbsp;None)</code> | Finishes this expression or function-call argument sequence. |
| 400 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;synthetic&nbsp;=&nbsp;next((x&nbsp;for&nbsp;x&nbsp;in&nbsp;self.groups.values()&nbsp;if&nbsp;x["role"]&nbsp;==&nbsp;"Synthetic"),&nbsp;None)</code> | Finishes this expression or function-call argument sequence. |
| 401 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;test,&nbsp;synthetic</code> | Returns this computed value to the caller; the function ends here. |
| 402 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 403 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;populate_shared_selections(self,&nbsp;clear=False):</code> | Defines the named function/method; indented lines below form its body. |
| 404 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;active&nbsp;=&nbsp;[x&nbsp;for&nbsp;x&nbsp;in&nbsp;self.groups.values()&nbsp;if&nbsp;x["visible"]]</code> | Assigns the expression on the right to `active` for later use. |
| 405 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Cache&nbsp;unique&nbsp;selectors&nbsp;per&nbsp;dataset:&nbsp;avoid&nbsp;scanning&nbsp;millions&nbsp;of&nbsp;rows</code> | Developer comment: Cache unique selectors per dataset: avoid scanning millions of rows |
| 406 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;whenever&nbsp;a&nbsp;CDF&nbsp;role&nbsp;or&nbsp;dataset&nbsp;visibility&nbsp;is&nbsp;changed.</code> | Developer comment: whenever a CDF role or dataset visibility is changed. |
| 407 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;group&nbsp;in&nbsp;self.groups.values():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 408 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"frequency_options"&nbsp;not&nbsp;in&nbsp;group:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 409 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group["frequency_options"]&nbsp;=&nbsp;np.sort(group["flat"]["Freq"].dropna().unique())</code> | Gets the distinct values in a column, useful for frequency or angle choices. |
| 410 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"phi_options"&nbsp;not&nbsp;in&nbsp;group:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 411 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group["phi_options"]&nbsp;=&nbsp;np.sort(group["flat"]["Phi"].dropna().unique())</code> | Gets the distinct values in a column, useful for frequency or angle choices. |
| 412 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;freqs&nbsp;=&nbsp;sorted(set().union(*(set(x["frequency_options"])&nbsp;for&nbsp;x&nbsp;in&nbsp;active)))&nbsp;if&nbsp;active&nbsp;else&nbsp;[]</code> | Assigns the expression on the right to `freqs` for later use. |
| 413 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phis&nbsp;=&nbsp;sorted(set().union(*(set(x["phi_options"])&nbsp;for&nbsp;x&nbsp;in&nbsp;active)))&nbsp;if&nbsp;active&nbsp;else&nbsp;[]</code> | Assigns the expression on the right to `phis` for later use. |
| 414 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._populate_checks(self.freq_check_layout,&nbsp;self.freq_checks,&nbsp;freqs,&nbsp;"&nbsp;MHz",&nbsp;clear)</code> | Finishes this expression or function-call argument sequence. |
| 415 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._populate_checks(self.phi_check_layout,&nbsp;self.phi_checks,&nbsp;phis,&nbsp;"°",&nbsp;clear)</code> | Finishes this expression or function-call argument sequence. |
| 416 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test,&nbsp;synth&nbsp;=&nbsp;self.selected_pair()</code> | Assigns the expression on the right to `test, synth` for later use. |
| 417 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;test&nbsp;is&nbsp;not&nbsp;None&nbsp;and&nbsp;synth&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 418 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;matched_f&nbsp;=&nbsp;set(test["frequency_options"])&nbsp;&&nbsp;set(synth["frequency_options"])</code> | Assigns the expression on the right to `matched_f` for later use. |
| 419 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;matched_p&nbsp;=&nbsp;set(test["phi_options"])&nbsp;&&nbsp;set(synth["phi_options"])</code> | Assigns the expression on the right to `matched_p` for later use. |
| 420 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.match_label.setText(f"CDF&nbsp;pair:&nbsp;{test['name']}&nbsp;−&nbsp;{synth['name']}\\n"</code> | Updates text shown in an existing widget. |
| 421 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f"{len(matched_f)}&nbsp;common&nbsp;frequencies,&nbsp;{len(matched_p)}&nbsp;common&nbsp;phi&nbsp;values")</code> | Finishes this expression or function-call argument sequence. |
| 422 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 423 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.match_label.setText(f"{len(self.groups)}&nbsp;datasets&nbsp;loaded.&nbsp;"</code> | Updates text shown in an existing widget. |
| 424 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Assign&nbsp;Test&nbsp;and&nbsp;Synthetic&nbsp;roles&nbsp;to&nbsp;enable&nbsp;CDF.")</code> | Finishes this expression or function-call argument sequence. |
| 425 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 426 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;set_all_checks(self,&nbsp;checked,&nbsp;selection):</code> | Defines the named function/method; indented lines below form its body. |
| 427 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checks&nbsp;=&nbsp;self.freq_checks&nbsp;if&nbsp;selection&nbsp;==&nbsp;"freq"&nbsp;else&nbsp;self.phi_checks</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 428 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;checkbox&nbsp;in&nbsp;checks.values():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 429 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox.blockSignals(True)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 430 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox.setChecked(checked)</code> | Sets whether this checkbox is initially or currently selected. |
| 431 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;checkbox.blockSignals(False)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 432 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_plot()</code> | Requests a refreshed visualization after the state changes. |
| 433 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 434 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;selected_filters(self):</code> | Defines the named function/method; indented lines below form its body. |
| 435 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;([f&nbsp;for&nbsp;f,&nbsp;c&nbsp;in&nbsp;self.freq_checks.items()&nbsp;if&nbsp;c.isChecked()],</code> | Returns this computed value to the caller; the function ends here. |
| 436 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[p&nbsp;for&nbsp;p,&nbsp;c&nbsp;in&nbsp;self.phi_checks.items()&nbsp;if&nbsp;c.isChecked()])</code> | Finishes this expression or function-call argument sequence. |
| 437 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 438 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;selected_polarizations(self):</code> | Defines the named function/method; indented lines below form its body. |
| 439 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;[p&nbsp;for&nbsp;p,&nbsp;cb&nbsp;in&nbsp;self.p_checks.items()&nbsp;if&nbsp;cb.isChecked()]</code> | Returns this computed value to the caller; the function ends here. |
| 440 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 441 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;filtered_data(self,&nbsp;group):</code> | Defines the named function/method; indented lines below form its body. |
| 442 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;freqs,&nbsp;phis&nbsp;=&nbsp;self.selected_filters()</code> | Assigns the expression on the right to `freqs, phis` for later use. |
| 443 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat&nbsp;=&nbsp;group["flat"]</code> | Assigns the expression on the right to `flat` for later use. |
| 444 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;freqs&nbsp;or&nbsp;not&nbsp;phis&nbsp;or&nbsp;not&nbsp;self.selected_polarizations():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 445 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;flat.iloc[0:0]</code> | Returns this computed value to the caller; the function ends here. |
| 446 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi_offset&nbsp;=&nbsp;float(group.get("phi_shift_offset",&nbsp;0.0))</code> | Assigns the expression on the right to `phi_offset` for later use. |
| 447 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;phi_offset:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 448 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;A&nbsp;displayed/checked&nbsp;Phi&nbsp;cut&nbsp;is&nbsp;an&nbsp;anchor&nbsp;from&nbsp;before&nbsp;this</code> | Developer comment: A displayed/checked Phi cut is an anchor from before this |
| 449 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;dataset&nbsp;was&nbsp;shifted.&nbsp;Follow&nbsp;it&nbsp;to&nbsp;its&nbsp;wrapped&nbsp;new&nbsp;coordinate.</code> | Developer comment: dataset was shifted. Follow it to its wrapped new coordinate. |
| 450 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Round&nbsp;to&nbsp;avoid&nbsp;floating-point&nbsp;mismatches&nbsp;on&nbsp;fractional&nbsp;shifts.</code> | Developer comment: Round to avoid floating-point mismatches on fractional shifts. |
| 451 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shifted_phis&nbsp;=&nbsp;np.round(</code> | Opens or closes a multi-line expression or collection. |
| 452 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(np.asarray(phis,&nbsp;dtype=float)&nbsp;+&nbsp;phi_offset&nbsp;+&nbsp;90.0)</code> | Converts input data to a NumPy array. |
| 453 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%&nbsp;180.0&nbsp;-&nbsp;90.0,&nbsp;8</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 454 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | Opens or closes a multi-line expression or collection. |
| 455 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi_mask&nbsp;=&nbsp;np.round(flat["Phi"].to_numpy(dtype=float),&nbsp;8)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 456 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi_mask&nbsp;=&nbsp;np.isin(phi_mask,&nbsp;shifted_phis)</code> | Creates a Boolean filter selecting rows whose values are in the chosen set. |
| 457 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 458 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi_mask&nbsp;=&nbsp;flat["Phi"].isin(phis)</code> | Creates a Boolean filter selecting rows whose values are in the chosen set. |
| 459 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;flat.loc[flat["Freq"].isin(freqs)&nbsp;&&nbsp;phi_mask</code> | Returns this computed value to the caller; the function ends here. |
| 460 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&&nbsp;flat["P"].isin(self.selected_polarizations())]</code> | Creates a Boolean filter selecting rows whose values are in the chosen set. |
| 461 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |


## `src/Lolth/__init__.py`

Package marker file; Python treats this directory as an importable package.

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>"""Lolth&nbsp;RF&nbsp;dataset&nbsp;analysis&nbsp;application."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |


## `src/Lolth/file_reading/__init__.py`

Package marker file; Python treats this directory as an importable package.

This file is empty on purpose: it marks the package directory. There are no executable lines to explain.


## `src/Lolth/file_reading/load_dialog.py`

Load popup: group chosen files, inspect available frequencies, and set import-time options.

**Code landmarks:** `FrequencyPicker` (line 11, class), `__init__` (line 13, function), `make_item` (line 43, function), `move` (line 48, function), `selected_frequencies` (line 54, function), `DatasetLoadDialog` (line 58, class), `__init__` (line 60, function), `assignments` (line 104, function), `scan_groups` (line 113, function), `accept` (line 167, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>"""File&nbsp;grouping,&nbsp;frequency&nbsp;scanning,&nbsp;and&nbsp;ingest&nbsp;processing&nbsp;UI."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 2 | <code>from&nbsp;pathlib&nbsp;import&nbsp;Path</code> | Imports specific classes or functions from the named module so this file can use them. |
| 3 | <code>from&nbsp;uuid&nbsp;import&nbsp;uuid4</code> | Imports specific classes or functions from the named module so this file can use them. |
| 4 | <code>from&nbsp;PyQt6.QtCore&nbsp;import&nbsp;Qt</code> | Imports specific classes or functions from the named module so this file can use them. |
| 5 | <code>from&nbsp;PyQt6.QtWidgets&nbsp;import&nbsp;(QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QTableWidget,QTableWidgetItem,QLineEdit,QPushButton,QScrollArea,QGroupBox,QDoubleSpinBox,QCheckBox,QComboBox,QMessageBox,QDialogButtonBox,QHeaderView,QListWidget,QListWidgetItem)</code> | Imports specific classes or functions from the named module so this file can use them. |
| 6 | <code>from&nbsp;.&nbsp;import&nbsp;loader&nbsp;as&nbsp;fl</code> | Imports specific classes or functions from the named module so this file can use them. |
| 7 | <code>from&nbsp;.loader&nbsp;import&nbsp;normalized_flat</code> | Imports specific classes or functions from the named module so this file can use them. |
| 8 | <code>from&nbsp;..processing.frequency&nbsp;import&nbsp;process_frequency_median</code> | Imports specific classes or functions from the named module so this file can use them. |
| 9 | <code>from&nbsp;..processing.resample&nbsp;import&nbsp;resample_angular_median</code> | Imports specific classes or functions from the named module so this file can use them. |
| 10 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 11 | <code>class&nbsp;FrequencyPicker(QWidget):</code> | Starts a class definition; any base classes in parentheses supply inherited behavior. |
| 12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Available&nbsp;(-)&nbsp;and&nbsp;included&nbsp;(+)&nbsp;frequencies&nbsp;in&nbsp;MHz."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;__init__(self,&nbsp;frequencies,&nbsp;parent=None):</code> | Defines the named function/method; indented lines below form its body. |
| 14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;super().__init__(parent)</code> | Finishes this expression or function-call argument sequence. |
| 15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.available&nbsp;=&nbsp;QListWidget()</code> | Stores or updates `self.available` on the current object so other methods can use it. |
| 16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.included&nbsp;=&nbsp;QListWidget()</code> | Stores or updates `self.included` on the current object so other methods can use it. |
| 17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.available.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)</code> | Finishes this expression or function-call argument sequence. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.included.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)</code> | Finishes this expression or function-call argument sequence. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;val&nbsp;in&nbsp;sorted(set(float(x)&nbsp;for&nbsp;x&nbsp;in&nbsp;frequencies)):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.included.addItem(self.make_item(val))</code> | Adds an option to a selection widget, sometimes with hidden application data. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row&nbsp;=&nbsp;QHBoxLayout(self)</code> | Creates a layout arranging items horizontally. |
| 22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left&nbsp;=&nbsp;QVBoxLayout()</code> | Creates a layout stacking items vertically. |
| 23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(QLabel("Excluded"))</code> | Creates a text label shown in the interface. |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left.addWidget(self.available)</code> | Inserts the specified widget into the surrounding layout. |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;middle&nbsp;=&nbsp;QVBoxLayout()</code> | Creates a layout stacking items vertically. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;middle.addStretch()</code> | Finishes this expression or function-call argument sequence. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;plus&nbsp;=&nbsp;QPushButton("+&nbsp;&nbsp;Include")</code> | Creates a clickable button. |
| 28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;minus&nbsp;=&nbsp;QPushButton("−&nbsp;&nbsp;Exclude")</code> | Creates a clickable button. |
| 29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;plus.clicked.connect(lambda:&nbsp;self.move(self.available,&nbsp;self.included))</code> | Connects the `plus.clicked` Qt signal to the callback inside `.connect(...)`. |
| 30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;minus.clicked.connect(lambda:&nbsp;self.move(self.included,&nbsp;self.available))</code> | Connects the `minus.clicked` Qt signal to the callback inside `.connect(...)`. |
| 31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;middle.addWidget(plus)</code> | Inserts the specified widget into the surrounding layout. |
| 32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;middle.addWidget(minus)</code> | Inserts the specified widget into the surrounding layout. |
| 33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;middle.addStretch()</code> | Finishes this expression or function-call argument sequence. |
| 34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right&nbsp;=&nbsp;QVBoxLayout()</code> | Creates a layout stacking items vertically. |
| 35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right.addWidget(QLabel("Included&nbsp;(MHz)"))</code> | Creates a text label shown in the interface. |
| 36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right.addWidget(self.included)</code> | Inserts the specified widget into the surrounding layout. |
| 37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addLayout(left,&nbsp;1)</code> | Nests one layout inside another layout. |
| 38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addLayout(middle)</code> | Nests one layout inside another layout. |
| 39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addLayout(right,&nbsp;1)</code> | Nests one layout inside another layout. |
| 40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.setMinimumHeight(115)</code> | Finishes this expression or function-call argument sequence. |
| 41 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | Decorator: this method does not receive an automatic `self` argument. |
| 43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;make_item(freq):</code> | Defines the named function/method; indented lines below form its body. |
| 44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;item&nbsp;=&nbsp;QListWidgetItem(f"{freq:g}")</code> | Assigns the expression on the right to `item` for later use. |
| 45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;item.setData(Qt.ItemDataRole.UserRole,&nbsp;float(freq))</code> | Finishes this expression or function-call argument sequence. |
| 46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;item</code> | Returns this computed value to the caller; the function ends here. |
| 47 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;move(self,&nbsp;source,&nbsp;dest):</code> | Defines the named function/method; indented lines below form its body. |
| 49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;item&nbsp;in&nbsp;source.selectedItems():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;source.takeItem(source.row(item))</code> | Finishes this expression or function-call argument sequence. |
| 51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dest.addItem(item)</code> | Adds an option to a selection widget, sometimes with hidden application data. |
| 52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dest.sortItems()</code> | Finishes this expression or function-call argument sequence. |
| 53 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;selected_frequencies(self):</code> | Defines the named function/method; indented lines below form its body. |
| 55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;sorted(self.included.item(i).data(Qt.ItemDataRole.UserRole)</code> | Returns this computed value to the caller; the function ends here. |
| 56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;i&nbsp;in&nbsp;range(self.included.count()))</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 57 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 58 | <code>class&nbsp;DatasetLoadDialog(QDialog):</code> | Starts a class definition; any base classes in parentheses supply inherited behavior. |
| 59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""One&nbsp;load&nbsp;popup:&nbsp;assign&nbsp;files&nbsp;to&nbsp;groups,&nbsp;scan&nbsp;them,&nbsp;and&nbsp;configure&nbsp;groups."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;__init__(self,&nbsp;paths,&nbsp;parent=None):</code> | Defines the named function/method; indented lines below form its body. |
| 61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;super().__init__(parent)</code> | Finishes this expression or function-call argument sequence. |
| 62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.setWindowTitle("Group&nbsp;and&nbsp;configure&nbsp;RF&nbsp;datasets")</code> | Sets the title shown in a popup or main window border. |
| 63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.resize(940,&nbsp;720)</code> | Sets the starting dimensions of the window or widget. |
| 64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.paths&nbsp;=&nbsp;list(dict.fromkeys(str(p)&nbsp;for&nbsp;p&nbsp;in&nbsp;paths))</code> | Stores or updates `self.paths` on the current object so other methods can use it. |
| 65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.configs&nbsp;=&nbsp;{}</code> | Stores or updates `self.configs` on the current object so other methods can use it. |
| 66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.result_groups&nbsp;=&nbsp;[]</code> | Stores or updates `self.result_groups` on the current object so other methods can use it. |
| 67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout&nbsp;=&nbsp;QVBoxLayout(self)</code> | Creates a layout stacking items vertically. |
| 68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel(</code> | Creates a text label shown in the interface. |
| 69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Assign&nbsp;a&nbsp;dataset&nbsp;name&nbsp;to&nbsp;each&nbsp;file.&nbsp;Files&nbsp;with&nbsp;identical&nbsp;dataset&nbsp;names&nbsp;"</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"will&nbsp;be&nbsp;combined.&nbsp;Click&nbsp;'Scan&nbsp;groups'&nbsp;to&nbsp;choose&nbsp;frequencies&nbsp;and&nbsp;median&nbsp;settings."</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;))</code> | Finishes this expression or function-call argument sequence. |
| 72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.assignment_table&nbsp;=&nbsp;QTableWidget(len(self.paths),&nbsp;2)</code> | Stores or updates `self.assignment_table` on the current object so other methods can use it. |
| 73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.assignment_table.setHorizontalHeaderLabels(["Selected&nbsp;file",&nbsp;"Dataset&nbsp;group&nbsp;(editable)"])</code> | Finishes this expression or function-call argument sequence. |
| 74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.assignment_table.horizontalHeader().setSectionResizeMode(0,&nbsp;QHeaderView.ResizeMode.Stretch)</code> | Finishes this expression or function-call argument sequence. |
| 75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.assignment_table.horizontalHeader().setSectionResizeMode(1,&nbsp;QHeaderView.ResizeMode.Stretch)</code> | Finishes this expression or function-call argument sequence. |
| 76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;index,&nbsp;path&nbsp;in&nbsp;enumerate(self.paths):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;item&nbsp;=&nbsp;QTableWidgetItem(Path(path).name)</code> | Assigns the expression on the right to `item` for later use. |
| 78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;item.setToolTip(path)</code> | Finishes this expression or function-call argument sequence. |
| 79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;item.setFlags(item.flags()&nbsp;&&nbsp;~Qt.ItemFlag.ItemIsEditable)</code> | Finishes this expression or function-call argument sequence. |
| 80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.assignment_table.setItem(index,&nbsp;0,&nbsp;item)</code> | Finishes this expression or function-call argument sequence. |
| 81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.assignment_table.setCellWidget(index,&nbsp;1,&nbsp;QLineEdit(Path(path).stem))</code> | Creates a single-line text input. |
| 82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.assignment_table.setMaximumHeight(210)</code> | Finishes this expression or function-call argument sequence. |
| 83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.assignment_table)</code> | Inserts the specified widget into the surrounding layout. |
| 84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scan&nbsp;=&nbsp;QPushButton("Scan&nbsp;groups&nbsp;/&nbsp;refresh&nbsp;frequency&nbsp;options")</code> | Creates a clickable button. |
| 85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scan.clicked.connect(self.scan_groups)</code> | Connects the `scan.clicked` Qt signal to the callback inside `.connect(...)`. |
| 86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(scan)</code> | Inserts the specified widget into the surrounding layout. |
| 87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.note&nbsp;=&nbsp;QLabel("Frequency&nbsp;controls&nbsp;will&nbsp;appear&nbsp;after&nbsp;scanning&nbsp;groups.")</code> | Creates a text label shown in the interface. |
| 88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.note.setWordWrap(True)</code> | Finishes this expression or function-call argument sequence. |
| 89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.note)</code> | Inserts the specified widget into the surrounding layout. |
| 90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.scroll&nbsp;=&nbsp;QScrollArea()</code> | Stores or updates `self.scroll` on the current object so other methods can use it. |
| 91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.scroll.setWidgetResizable(True)</code> | Finishes this expression or function-call argument sequence. |
| 92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.config_container&nbsp;=&nbsp;QWidget()</code> | Stores or updates `self.config_container` on the current object so other methods can use it. |
| 93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.config_layout&nbsp;=&nbsp;QVBoxLayout(self.config_container)</code> | Creates a layout stacking items vertically. |
| 94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.config_layout.addStretch()</code> | Finishes this expression or function-call argument sequence. |
| 95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.scroll.setWidget(self.config_container)</code> | Finishes this expression or function-call argument sequence. |
| 96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.scroll,&nbsp;1)</code> | Inserts the specified widget into the surrounding layout. |
| 97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buttons&nbsp;=&nbsp;QDialogButtonBox(QDialogButtonBox.StandardButton.Ok&nbsp;\|</code> | Assigns the expression on the right to `buttons` for later use. |
| 98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QDialogButtonBox.StandardButton.Cancel)</code> | Finishes this expression or function-call argument sequence. |
| 99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Add&nbsp;datasets")</code> | Updates text shown in an existing widget. |
| 100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buttons.accepted.connect(self.accept)</code> | Connects the `buttons.accepted` Qt signal to the callback inside `.connect(...)`. |
| 101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buttons.rejected.connect(self.reject)</code> | Connects the `buttons.rejected` Qt signal to the callback inside `.connect(...)`. |
| 102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(buttons)</code> | Inserts the specified widget into the surrounding layout. |
| 103 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;assignments(self):</code> | Defines the named function/method; indented lines below form its body. |
| 105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;groups&nbsp;=&nbsp;{}</code> | Assigns the expression on the right to `groups` for later use. |
| 106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;i,&nbsp;path&nbsp;in&nbsp;enumerate(self.paths):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name&nbsp;=&nbsp;self.assignment_table.cellWidget(i,&nbsp;1).text().strip()</code> | Assigns the expression on the right to `name` for later use. |
| 108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;name:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"Please&nbsp;enter&nbsp;a&nbsp;group&nbsp;name&nbsp;for&nbsp;{Path(path).name}.")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;groups.setdefault(name,&nbsp;[]).append(path)</code> | Finishes this expression or function-call argument sequence. |
| 111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;groups</code> | Returns this computed value to the caller; the function ends here. |
| 112 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;scan_groups(self):</code> | Defines the named function/method; indented lines below form its body. |
| 114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;groups&nbsp;=&nbsp;self.assignments()</code> | Assigns the expression on the right to `groups` for later use. |
| 116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `result` for later use. |
| 117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;name,&nbsp;paths&nbsp;in&nbsp;groups.items():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data&nbsp;=&nbsp;fl.load_multiple(paths)</code> | Assigns the expression on the right to `data` for later use. |
| 119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;data&nbsp;is&nbsp;None&nbsp;or&nbsp;data.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"{name}&nbsp;returned&nbsp;no&nbsp;data")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat&nbsp;=&nbsp;normalized_flat(data,&nbsp;name)</code> | Assigns the expression on the right to `flat` for later use. |
| 122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;flat.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"{name}&nbsp;contains&nbsp;no&nbsp;valid&nbsp;samples")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result.append(dict(name=name,&nbsp;paths=paths,&nbsp;data=data,&nbsp;raw=flat))</code> | Finishes this expression or function-call argument sequence. |
| 125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;Exception&nbsp;as&nbsp;exc:</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QMessageBox.critical(self,&nbsp;"Scan&nbsp;error",&nbsp;str(exc))</code> | Displays an informational, warning, or error popup to the user. |
| 127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;while&nbsp;self.config_layout.count():</code> | Repeats the indented block while the condition remains true. |
| 129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;child&nbsp;=&nbsp;self.config_layout.takeAt(0)</code> | Assigns the expression on the right to `child` for later use. |
| 130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;child.widget():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;child.widget().deleteLater()</code> | Finishes this expression or function-call argument sequence. |
| 132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.configs&nbsp;=&nbsp;{}</code> | Stores or updates `self.configs` on the current object so other methods can use it. |
| 133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;entry&nbsp;in&nbsp;result:</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name&nbsp;=&nbsp;entry["name"]</code> | Assigns the expression on the right to `name` for later use. |
| 135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group_box&nbsp;=&nbsp;QGroupBox(f"{name}&nbsp;&nbsp;—&nbsp;&nbsp;{len(entry['paths'])}&nbsp;file(s),&nbsp;{len(entry['raw']):,}&nbsp;samples")</code> | Assigns the expression on the right to `group_box` for later use. |
| 136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form&nbsp;=&nbsp;QVBoxLayout(group_box)</code> | Creates a layout stacking items vertically. |
| 137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;toggle&nbsp;=&nbsp;QCheckBox("Apply&nbsp;frequency&nbsp;bandwidth&nbsp;median")</code> | Creates a checkbox the user can toggle on or off. |
| 139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value.setRange(0,&nbsp;1_000_000)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value.setDecimals(4)</code> | Finishes this expression or function-call argument sequence. |
| 142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value.setValue(0)</code> | Sets the current value of a control or measurement display. |
| 143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;unit&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;unit.addItems(["MHz",&nbsp;"%"])</code> | Adds several options to a dropdown in one operation. |
| 145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value.setEnabled(False)</code> | Enables or disables user interaction with the control. |
| 146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;unit.setEnabled(False)</code> | Enables or disables user interaction with the control. |
| 147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;toggle.toggled.connect(value.setEnabled)</code> | Connects the `toggle.toggled` Qt signal to the callback inside `.connect(...)`. |
| 148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;toggle.toggled.connect(unit.setEnabled)</code> | Connects the `toggle.toggled` Qt signal to the callback inside `.connect(...)`. |
| 149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(toggle)</code> | Inserts the specified widget into the surrounding layout. |
| 150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(QLabel("Full&nbsp;bandwidth:"))</code> | Creates a text label shown in the interface. |
| 151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(value)</code> | Inserts the specified widget into the surrounding layout. |
| 152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(unit)</code> | Inserts the specified widget into the surrounding layout. |
| 153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addStretch()</code> | Finishes this expression or function-call argument sequence. |
| 154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form.addLayout(row)</code> | Nests one layout inside another layout. |
| 155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resample&nbsp;=&nbsp;QCheckBox("Resample&nbsp;oversampled&nbsp;0.5°&nbsp;angular&nbsp;grid&nbsp;to&nbsp;1°&nbsp;(median&nbsp;I/Q)")</code> | Creates a checkbox the user can toggle on or off. |
| 156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form.addWidget(resample)</code> | Inserts the specified widget into the surrounding layout. |
| 157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form.addWidget(QLabel("Choose&nbsp;center&nbsp;frequencies&nbsp;to&nbsp;include&nbsp;(+)&nbsp;or&nbsp;exclude&nbsp;(−):"))</code> | Creates a text label shown in the interface. |
| 158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;picker&nbsp;=&nbsp;FrequencyPicker(entry["raw"]["Freq"].unique())</code> | Gets the distinct values in a column, useful for frequency or angle choices. |
| 159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;form.addWidget(picker)</code> | Inserts the specified widget into the surrounding layout. |
| 160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.config_layout.addWidget(group_box)</code> | Inserts the specified widget into the surrounding layout. |
| 161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.configs[name]&nbsp;=&nbsp;dict(entry=entry,&nbsp;toggle=toggle,&nbsp;value=value,</code> | Stores or updates `self.configs[name]` on the current object so other methods can use it. |
| 162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;unit=unit,&nbsp;picker=picker,&nbsp;resample=resample)</code> | Assigns the expression on the right to `unit` for later use. |
| 163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.config_layout.addStretch()</code> | Finishes this expression or function-call argument sequence. |
| 164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.note.setText(f"Scanned&nbsp;{len(result)}&nbsp;dataset&nbsp;group(s).&nbsp;Changes&nbsp;to&nbsp;group&nbsp;names&nbsp;"</code> | Updates text shown in an existing widget. |
| 165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"or&nbsp;assignments&nbsp;require&nbsp;scanning&nbsp;again.")</code> | Finishes this expression or function-call argument sequence. |
| 166 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;accept(self):</code> | Defines the named function/method; indented lines below form its body. |
| 168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;assignments&nbsp;=&nbsp;self.assignments()</code> | Assigns the expression on the right to `assignments` for later use. |
| 170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self.configs&nbsp;or&nbsp;set(assignments)&nbsp;!=&nbsp;set(self.configs)&nbsp;or&nbsp;any(</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;assignments[n]&nbsp;!=&nbsp;self.configs[n]["entry"]["paths"]&nbsp;for&nbsp;n&nbsp;in&nbsp;assignments</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;):</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("Click&nbsp;'Scan&nbsp;groups'&nbsp;after&nbsp;editing&nbsp;file&nbsp;assignments.")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;output&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `output` for later use. |
| 175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;name,&nbsp;controls&nbsp;in&nbsp;self.configs.items():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;selected&nbsp;=&nbsp;controls["picker"].selected_frequencies()</code> | Assigns the expression on the right to `selected` for later use. |
| 177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;selected:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"{name}:&nbsp;include&nbsp;at&nbsp;least&nbsp;one&nbsp;frequency.")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;entry&nbsp;=&nbsp;controls["entry"]</code> | Assigns the expression on the right to `entry` for later use. |
| 180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;bandwidth&nbsp;=&nbsp;controls["value"].value()&nbsp;if&nbsp;controls["toggle"].isChecked()&nbsp;else&nbsp;0</code> | Assigns the expression on the right to `bandwidth` for later use. |
| 181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;unit&nbsp;=&nbsp;controls["unit"].currentText()</code> | Assigns the expression on the right to `unit` for later use. |
| 182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat&nbsp;=&nbsp;entry["raw"]</code> | Assigns the expression on the right to `flat` for later use. |
| 183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resample&nbsp;=&nbsp;controls["resample"].isChecked()</code> | Assigns the expression on the right to `resample` for later use. |
| 184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;resample:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat&nbsp;=&nbsp;resample_angular_median(flat)</code> | Assigns the expression on the right to `flat` for later use. |
| 186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat&nbsp;=&nbsp;process_frequency_median(flat,&nbsp;selected,&nbsp;bandwidth,&nbsp;unit)</code> | Assigns the expression on the right to `flat` for later use. |
| 187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;output.append(dict(id=uuid4().hex,&nbsp;name=name,&nbsp;paths=entry["paths"],</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data=entry["data"],&nbsp;raw=entry["raw"],&nbsp;flat=flat,</code> | Assigns the expression on the right to `data` for later use. |
| 189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frequencies=selected,&nbsp;bandwidth=bandwidth,&nbsp;unit=unit,&nbsp;resampled=resample,</code> | Assigns the expression on the right to `frequencies` for later use. |
| 190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;visible=True,&nbsp;role="None"))</code> | Assigns the expression on the right to `visible` for later use. |
| 191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.result_groups&nbsp;=&nbsp;output</code> | Stores or updates `self.result_groups` on the current object so other methods can use it. |
| 192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;Exception&nbsp;as&nbsp;exc:</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QMessageBox.warning(self,&nbsp;"Dataset&nbsp;configuration",&nbsp;str(exc))</code> | Displays an informational, warning, or error popup to the user. |
| 194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;super().accept()</code> | Finishes this expression or function-call argument sequence. |


## `src/Lolth/file_reading/loader.py`

File import: parse RF text/pickles and normalize their fields into a flat DataFrame.

**Code landmarks:** `read_rf_text` (line 14, function), `_nested_measurements` (line 45, function), `normalized_flat` (line 91, function), `load_multiple` (line 136, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>"""RF&nbsp;ingestion&nbsp;from&nbsp;measurement&nbsp;text,&nbsp;flat&nbsp;pickle,&nbsp;or&nbsp;legacy&nbsp;nested&nbsp;pickle.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 2 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 3 | <code>Original&nbsp;scan&nbsp;names&nbsp;are&nbsp;always&nbsp;retained:&nbsp;E1&nbsp;is&nbsp;the&nbsp;-90..90&nbsp;scan&nbsp;(Phi),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 4 | <code>A1&nbsp;is&nbsp;the&nbsp;-180..180&nbsp;scan&nbsp;(Theta).&nbsp;Plotting&nbsp;aliases&nbsp;are&nbsp;additive,&nbsp;optional.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 5 | <code>"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 6 | <code>from&nbsp;pathlib&nbsp;import&nbsp;Path</code> | Imports specific classes or functions from the named module so this file can use them. |
| 7 | <code>import&nbsp;re</code> | Loads the named Python package/module for use in this file. |
| 8 | <code>import&nbsp;numpy&nbsp;as&nbsp;np</code> | Loads the named Python package/module for use in this file. |
| 9 | <code>import&nbsp;pandas&nbsp;as&nbsp;pd</code> | Loads the named Python package/module for use in this file. |
| 10 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 11 | <code>FREQ_RE&nbsp;=&nbsp;re.compile(r"frequency\\s+([0-9.eE+-]+)\\s*(GHz\|MHz\|kHz\|Hz)?",&nbsp;re.I)</code> | Assigns the expression on the right to `FREQ_RE` for later use. |
| 12 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 13 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 14 | <code>def&nbsp;read_rf_text(path):</code> | Defines the named function/method; indented lines below form its body. |
| 15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;records&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `records` for later use. |
| 16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;frequency&nbsp;=&nbsp;None</code> | Assigns the expression on the right to `frequency` for later use. |
| 17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;with&nbsp;open(path,&nbsp;"r",&nbsp;encoding="utf8",&nbsp;errors="replace")&nbsp;as&nbsp;fh:</code> | Opens a managed resource (often a file); Python cleans it up when the block ends. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;lineno,&nbsp;line&nbsp;in&nbsp;enumerate(fh,&nbsp;1):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;match&nbsp;=&nbsp;FREQ_RE.search(line)</code> | Assigns the expression on the right to `match` for later use. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;match:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value&nbsp;=&nbsp;float(match.group(1))</code> | Assigns the expression on the right to `value` for later use. |
| 22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;unit&nbsp;=&nbsp;(match.group(2)&nbsp;or&nbsp;"MHz").lower()</code> | Assigns the expression on the right to `unit` for later use. |
| 23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frequency&nbsp;=&nbsp;value&nbsp;*&nbsp;{"ghz":&nbsp;1000,&nbsp;"mhz":&nbsp;1,&nbsp;"khz":&nbsp;.001,</code> | Assigns the expression on the right to `frequency` for later use. |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"hz":&nbsp;1e-6}[unit]</code> | Finishes this expression or function-call argument sequence. |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | Skips the rest of this loop iteration and proceeds to the next item. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts&nbsp;=&nbsp;line.split()</code> | Assigns the expression on the right to `parts` for later use. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;len(parts)&nbsp;&lt;&nbsp;9&nbsp;or&nbsp;parts[0].strip("\\"'").upper()&nbsp;not&nbsp;in&nbsp;("A",&nbsp;"B"):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | Skips the rest of this loop iteration and proceeds to the next item. |
| 29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;frequency&nbsp;is&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"{path}:{lineno}&nbsp;data&nbsp;row&nbsp;precedes&nbsp;frequency&nbsp;header")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;e1,&nbsp;a1&nbsp;=&nbsp;float(parts[1]),&nbsp;float(parts[2])</code> | Assigns the expression on the right to `e1, a1` for later use. |
| 33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;real,&nbsp;imag,&nbsp;power&nbsp;=&nbsp;map(float,&nbsp;parts[6:9])</code> | Assigns the expression on the right to `real, imag, power` for later use. |
| 34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;(ValueError,&nbsp;IndexError):</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | Skips the rest of this loop iteration and proceeds to the next item. |
| 36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;polarization&nbsp;=&nbsp;parts[0].strip("\\"'").upper()&nbsp;+&nbsp;parts[3].strip("\\"'").upper()</code> | Assigns the expression on the right to `polarization` for later use. |
| 37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;records.append((frequency,&nbsp;e1,&nbsp;a1,&nbsp;polarization,&nbsp;real,&nbsp;imag,&nbsp;power))</code> | Finishes this expression or function-call argument sequence. |
| 38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;records:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"No&nbsp;RF&nbsp;records&nbsp;in&nbsp;{path}")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;frame&nbsp;=&nbsp;pd.DataFrame.from_records(records,</code> | Assigns the expression on the right to `frame` for later use. |
| 41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;columns=["Freq",&nbsp;"E1",&nbsp;"A1",&nbsp;"P",&nbsp;"I",&nbsp;"Q",&nbsp;"PdB"])</code> | Assigns the expression on the right to `columns` for later use. |
| 42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;normalized_flat(frame,&nbsp;str(path))</code> | Returns this computed value to the caller; the function ends here. |
| 43 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 44 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 45 | <code>def&nbsp;_nested_measurements(obj,&nbsp;parent):</code> | Defines the named function/method; indented lines below form its body. |
| 46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Flatten&nbsp;legacy&nbsp;Data&nbsp;cells&nbsp;while&nbsp;retaining&nbsp;row-level&nbsp;Freq/E1/P&nbsp;metadata."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;obj&nbsp;is&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;pd.DataFrame()</code> | Returns this computed value to the caller; the function ends here. |
| 49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;isinstance(obj,&nbsp;pd.DataFrame):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner&nbsp;=&nbsp;obj.copy()</code> | Creates a separate copy so later modifications do not unexpectedly change the original data. |
| 51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;isinstance(obj,&nbsp;pd.Series):</code> | Tests an alternative condition only if previous conditions were false. |
| 52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner&nbsp;=&nbsp;obj.to_frame().T&nbsp;if&nbsp;not&nbsp;isinstance(obj.iloc[0],&nbsp;(list,&nbsp;tuple,&nbsp;np.ndarray))&nbsp;else&nbsp;pd.DataFrame(obj.to_dict())</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;isinstance(obj,&nbsp;dict):</code> | Tests an alternative condition only if previous conditions were false. |
| 54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner&nbsp;=&nbsp;pd.DataFrame(obj)</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;array&nbsp;=&nbsp;np.asarray(obj)</code> | Converts input data to a NumPy array. |
| 57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;array.ndim&nbsp;==&nbsp;0:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("Unsupported&nbsp;scalar&nbsp;Data&nbsp;field&nbsp;in&nbsp;legacy&nbsp;pickle")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;array.ndim&nbsp;==&nbsp;1:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;len(array)&nbsp;and&nbsp;isinstance(array[0],&nbsp;(dict,&nbsp;pd.Series)):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner&nbsp;=&nbsp;pd.DataFrame(list(array))</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner&nbsp;=&nbsp;pd.DataFrame({"PdBsm":&nbsp;array})</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;array.ndim&nbsp;==&nbsp;2:</code> | Tests an alternative condition only if previous conditions were false. |
| 65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Legacy&nbsp;file_loader.mread&nbsp;/&nbsp;nest_data&nbsp;stores&nbsp;each&nbsp;field&nbsp;in&nbsp;a</code> | Developer comment: Legacy file_loader.mread / nest_data stores each field in a |
| 66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;separate&nbsp;ROW:&nbsp;(4,&nbsp;N)&nbsp;=&nbsp;[A1,&nbsp;I,&nbsp;Q,&nbsp;PdBsm].&nbsp;Modern&nbsp;flat&nbsp;inputs</code> | Developer comment: separate ROW: (4, N) = [A1, I, Q, PdBsm]. Modern flat inputs |
| 67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;may&nbsp;instead&nbsp;store&nbsp;one&nbsp;measurement&nbsp;per&nbsp;row:&nbsp;(N,&nbsp;4).</code> | Developer comment: may instead store one measurement per row: (N, 4). |
| 68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;names&nbsp;=&nbsp;{3:&nbsp;["A1",&nbsp;"I",&nbsp;"Q"],</code> | Assigns the expression on the right to `names` for later use. |
| 69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4:&nbsp;["A1",&nbsp;"I",&nbsp;"Q",&nbsp;"PdBsm"],</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5:&nbsp;["A1",&nbsp;"E1",&nbsp;"I",&nbsp;"Q",&nbsp;"PdBsm"]}</code> | Finishes this expression or function-call argument sequence. |
| 71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rows,&nbsp;cols&nbsp;=&nbsp;array.shape</code> | Assigns the expression on the right to `rows, cols` for later use. |
| 72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;rows&nbsp;in&nbsp;names&nbsp;and&nbsp;cols&nbsp;not&nbsp;in&nbsp;names:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner&nbsp;=&nbsp;pd.DataFrame(array.T,&nbsp;columns=names[rows])</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;cols&nbsp;in&nbsp;names&nbsp;and&nbsp;rows&nbsp;not&nbsp;in&nbsp;names:</code> | Tests an alternative condition only if previous conditions were false. |
| 75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner&nbsp;=&nbsp;pd.DataFrame(array,&nbsp;columns=names[cols])</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;rows&nbsp;in&nbsp;names&nbsp;and&nbsp;cols&nbsp;in&nbsp;names:</code> | Tests an alternative condition only if previous conditions were false. |
| 77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Prefer&nbsp;the&nbsp;legacy&nbsp;field-per-row&nbsp;convention&nbsp;for&nbsp;small&nbsp;arrays.</code> | Developer comment: Prefer the legacy field-per-row convention for small arrays. |
| 78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner&nbsp;=&nbsp;pd.DataFrame(array.T,&nbsp;columns=names[rows])</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"Unsupported&nbsp;nested&nbsp;Data&nbsp;array&nbsp;shape&nbsp;{array.shape}")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"Unsupported&nbsp;nested&nbsp;Data&nbsp;array&nbsp;shape&nbsp;{array.shape}")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;key&nbsp;in&nbsp;("Freq",&nbsp;"E1",&nbsp;"A1",&nbsp;"P",&nbsp;"File"):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;key&nbsp;not&nbsp;in&nbsp;inner.columns&nbsp;and&nbsp;key&nbsp;in&nbsp;parent:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;inner[key]&nbsp;=&nbsp;[parent[key]]&nbsp;*&nbsp;len(inner)</code> | Assigns the expression on the right to `inner[key]` for later use. |
| 86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;The&nbsp;original&nbsp;nested&nbsp;reader&nbsp;can&nbsp;store&nbsp;per-point&nbsp;A1&nbsp;under&nbsp;'A1',</code> | Developer comment: The original nested reader can store per-point A1 under 'A1', |
| 87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;but&nbsp;if&nbsp;only&nbsp;per-row&nbsp;E1&nbsp;and&nbsp;an&nbsp;angular&nbsp;sweep&nbsp;are&nbsp;supplied,&nbsp;retain&nbsp;both.</code> | Developer comment: but if only per-row E1 and an angular sweep are supplied, retain both. |
| 88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;inner</code> | Returns this computed value to the caller; the function ends here. |
| 89 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 90 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 91 | <code>def&nbsp;normalized_flat(frame,&nbsp;name="Dataset"):</code> | Defines the named function/method; indented lines below form its body. |
| 92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;isinstance(frame,&nbsp;pd.DataFrame):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"{name}:&nbsp;loader&nbsp;did&nbsp;not&nbsp;return&nbsp;a&nbsp;DataFrame")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;frame&nbsp;=&nbsp;frame.copy()</code> | Creates a separate copy so later modifications do not unexpectedly change the original data. |
| 95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"Data"&nbsp;in&nbsp;frame.columns:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pieces&nbsp;=&nbsp;[_nested_measurements(row["Data"],&nbsp;row)</code> | Assigns the expression on the right to `pieces` for later use. |
| 97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;_,&nbsp;row&nbsp;in&nbsp;frame.iterrows()]</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame&nbsp;=&nbsp;pd.concat(pieces,&nbsp;ignore_index=True)&nbsp;if&nbsp;pieces&nbsp;else&nbsp;pd.DataFrame()</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"Freq"&nbsp;not&nbsp;in&nbsp;frame:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;candidate&nbsp;in&nbsp;("Frequency",&nbsp;"frequency"):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;candidate&nbsp;in&nbsp;frame:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["Freq"]&nbsp;=&nbsp;frame[candidate]</code> | Assigns the expression on the right to `frame["Freq"]` for later use. |
| 103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;break</code> | Stops the current loop. |
| 104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Source&nbsp;schema&nbsp;takes&nbsp;precedence&nbsp;over&nbsp;any&nbsp;previously&nbsp;derived&nbsp;aliases.</code> | Developer comment: Source schema takes precedence over any previously derived aliases. |
| 105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"E1"&nbsp;in&nbsp;frame:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["Phi"]&nbsp;=&nbsp;frame["E1"]</code> | Assigns the expression on the right to `frame["Phi"]` for later use. |
| 107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;"Phi"&nbsp;in&nbsp;frame:</code> | Tests an alternative condition only if previous conditions were false. |
| 108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["E1"]&nbsp;=&nbsp;frame["Phi"]</code> | Assigns the expression on the right to `frame["E1"]` for later use. |
| 109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"A1"&nbsp;in&nbsp;frame:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["Theta"]&nbsp;=&nbsp;frame["A1"]</code> | Assigns the expression on the right to `frame["Theta"]` for later use. |
| 111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;"Theta"&nbsp;in&nbsp;frame:</code> | Tests an alternative condition only if previous conditions were false. |
| 112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["A1"]&nbsp;=&nbsp;frame["Theta"]</code> | Assigns the expression on the right to `frame["A1"]` for later use. |
| 113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;"theta"&nbsp;in&nbsp;frame:</code> | Tests an alternative condition only if previous conditions were false. |
| 114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["Theta"]&nbsp;=&nbsp;frame["theta"]</code> | Assigns the expression on the right to `frame["Theta"]` for later use. |
| 115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["A1"]&nbsp;=&nbsp;frame["theta"]</code> | Assigns the expression on the right to `frame["A1"]` for later use. |
| 116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"PdB"&nbsp;not&nbsp;in&nbsp;frame&nbsp;and&nbsp;"PdBsm"&nbsp;in&nbsp;frame:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["PdB"]&nbsp;=&nbsp;frame["PdBsm"]</code> | Assigns the expression on the right to `frame["PdB"]` for later use. |
| 118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"PdB"&nbsp;not&nbsp;in&nbsp;frame&nbsp;and&nbsp;"I"&nbsp;in&nbsp;frame&nbsp;and&nbsp;"Q"&nbsp;in&nbsp;frame:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;real&nbsp;=&nbsp;pd.to_numeric(frame["I"],&nbsp;errors="coerce")</code> | Assigns the expression on the right to `real` for later use. |
| 120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;imag&nbsp;=&nbsp;pd.to_numeric(frame["Q"],&nbsp;errors="coerce")</code> | Assigns the expression on the right to `imag` for later use. |
| 121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["PdB"]&nbsp;=&nbsp;20&nbsp;*&nbsp;np.log10(np.maximum(np.hypot(real,&nbsp;imag),&nbsp;1e-15))</code> | Assigns the expression on the right to `frame["PdB"]` for later use. |
| 122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Keep&nbsp;the&nbsp;original&nbsp;P&nbsp;polarization&nbsp;pair&nbsp;(AA/AB/BA/BB).&nbsp;Older&nbsp;flat&nbsp;files</code> | Developer comment: Keep the original P polarization pair (AA/AB/BA/BB). Older flat files |
| 123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;without&nbsp;P&nbsp;are&nbsp;treated&nbsp;as&nbsp;AA&nbsp;for&nbsp;backward&nbsp;compatibility.</code> | Developer comment: without P are treated as AA for backward compatibility. |
| 124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"P"&nbsp;not&nbsp;in&nbsp;frame.columns:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["P"]&nbsp;=&nbsp;"AA"</code> | Assigns the expression on the right to `frame["P"]` for later use. |
| 126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;frame["P"]&nbsp;=&nbsp;frame["P"].astype(str).str.strip().str.upper()</code> | Assigns the expression on the right to `frame["P"]` for later use. |
| 127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;required&nbsp;=&nbsp;["Freq",&nbsp;"E1",&nbsp;"A1",&nbsp;"PdB"]</code> | Assigns the expression on the right to `required` for later use. |
| 128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;missing&nbsp;=&nbsp;[k&nbsp;for&nbsp;k&nbsp;in&nbsp;required&nbsp;if&nbsp;k&nbsp;not&nbsp;in&nbsp;frame]</code> | Assigns the expression on the right to `missing` for later use. |
| 129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;missing:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"{name}:&nbsp;missing&nbsp;{missing};&nbsp;available&nbsp;columns:&nbsp;{list(frame.columns)}")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;col&nbsp;in&nbsp;required&nbsp;+&nbsp;["Phi",&nbsp;"Theta"]&nbsp;+&nbsp;[x&nbsp;for&nbsp;x&nbsp;in&nbsp;("I",&nbsp;"Q")&nbsp;if&nbsp;x&nbsp;in&nbsp;frame]:</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame[col]&nbsp;=&nbsp;pd.to_numeric(frame[col],&nbsp;errors="coerce")</code> | Assigns the expression on the right to `frame[col]` for later use. |
| 133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;frame.dropna(subset=required).reset_index(drop=True)</code> | Returns this computed value to the caller; the function ends here. |
| 134 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 135 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 136 | <code>def&nbsp;load_multiple(paths):</code> | Defines the named function/method; indented lines below form its body. |
| 137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;frames&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `frames` for later use. |
| 138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;path&nbsp;in&nbsp;paths:</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;path&nbsp;=&nbsp;Path(path)</code> | Assigns the expression on the right to `path` for later use. |
| 140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;path.suffix.lower()&nbsp;==&nbsp;".txt":</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frames.append(read_rf_text(path))</code> | Finishes this expression or function-call argument sequence. |
| 142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;path.suffix.lower()&nbsp;==&nbsp;".pkl":</code> | Tests an alternative condition only if previous conditions were false. |
| 143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frames.append(normalized_flat(pd.read_pickle(path),&nbsp;str(path)))</code> | Finishes this expression or function-call argument sequence. |
| 145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;(TypeError,&nbsp;NotImplementedError)&nbsp;as&nbsp;exc:</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"Cannot&nbsp;read&nbsp;{path.name}&nbsp;with&nbsp;the&nbsp;installed&nbsp;pandas&nbsp;version.&nbsp;"</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f"Try&nbsp;the&nbsp;pandas&nbsp;version&nbsp;used&nbsp;to&nbsp;save&nbsp;the&nbsp;pickle.&nbsp;Details:&nbsp;{exc}")&nbsp;from&nbsp;exc</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"Unsupported&nbsp;extension:&nbsp;{path.suffix}")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;pd.concat(frames,&nbsp;ignore_index=True)&nbsp;if&nbsp;frames&nbsp;else&nbsp;pd.DataFrame()</code> | Returns this computed value to the caller; the function ends here. |


## `src/Lolth/modeling/__init__.py`

Package marker file; Python treats this directory as an importable package.

This file is empty on purpose: it marks the package directory. There are no executable lines to explain.


## `src/Lolth/modeling/vtk_viewer.py`

Interactive STL and RF-pattern 3D views, built using the VTK Qt OpenGL interactor.

**Code landmarks:** `EmbeddedVTKDialog` (line 8, class), `__init__` (line 11, function), `showEvent` (line 150, function), `_initialize_vtk` (line 155, function), `_render` (line 163, function), `_flush_render` (line 169, function), `_refresh_color` (line 177, function), `choose_color` (line 182, function), `open_stl` (line 192, function), `_triangle_polydata` (line 214, function), `_draw_stl` (line 236, function), `refresh_frequencies` (line 249, function), `_color_limits` (line 269, function), `update_annotations` (line 276, function), `update_colormap` (line 288, function), `update_color_scale` (line 303, function), `render_pattern` (line 325, function), `closeEvent` (line 428, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>import&nbsp;numpy&nbsp;as&nbsp;np</code> | Loads the named Python package/module for use in this file. |
| 2 | <code>import&nbsp;pandas&nbsp;as&nbsp;pd</code> | Loads the named Python package/module for use in this file. |
| 3 | <code>from&nbsp;pathlib&nbsp;import&nbsp;Path</code> | Imports specific classes or functions from the named module so this file can use them. |
| 4 | <code>from&nbsp;PyQt6.QtCore&nbsp;import&nbsp;Qt,QTimer</code> | Imports specific classes or functions from the named module so this file can use them. |
| 5 | <code>from&nbsp;PyQt6.QtGui&nbsp;import&nbsp;QColor</code> | Imports specific classes or functions from the named module so this file can use them. |
| 6 | <code>from&nbsp;PyQt6.QtWidgets&nbsp;import&nbsp;(QDialog,QWidget,QLabel,QPushButton,QComboBox,QDoubleSpinBox,QColorDialog,QFileDialog,QMessageBox,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,QCheckBox,QGroupBox)</code> | Imports specific classes or functions from the named module so this file can use them. |
| 7 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 8 | <code>class&nbsp;EmbeddedVTKDialog(QDialog):</code> | Starts a class definition; any base classes in parentheses supply inherited behavior. |
| 9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Experimental&nbsp;Qt6&nbsp;QOpenGLWidget&nbsp;interactor&nbsp;for&nbsp;VTK&nbsp;9.4.2."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 10 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;__init__(self,&nbsp;parent=None,&nbsp;radiation=False):</code> | Defines the named function/method; indented lines below form its body. |
| 12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;super().__init__(parent)</code> | Finishes this expression or function-call argument sequence. |
| 13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.radiation_mode&nbsp;=&nbsp;radiation</code> | Stores or updates `self.radiation_mode` on the current object so other methods can use it. |
| 14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.setWindowTitle("3D&nbsp;Model&nbsp;-&nbsp;Radiation&nbsp;Pattern"&nbsp;if&nbsp;radiation&nbsp;else&nbsp;"3D&nbsp;Model")</code> | Sets the title shown in a popup or main window border. |
| 15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.resize(1200,&nbsp;820)</code> | Sets the starting dimensions of the window or widget. |
| 16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_path&nbsp;=&nbsp;None</code> | Stores or updates `self.model_path` on the current object so other methods can use it. |
| 17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_color&nbsp;=&nbsp;QColor("#a6bdd0")</code> | Stores or updates `self.model_color` on the current object so other methods can use it. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_actor&nbsp;=&nbsp;None</code> | Stores or updates `self.model_actor` on the current object so other methods can use it. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_actor&nbsp;=&nbsp;None</code> | Stores or updates `self.pattern_actor` on the current object so other methods can use it. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_actor&nbsp;=&nbsp;None</code> | Stores or updates `self.bar_actor` on the current object so other methods can use it. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._initialized&nbsp;=&nbsp;False</code> | Stores or updates `self._initialized` on the current object so other methods can use it. |
| 22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._pending_render&nbsp;=&nbsp;False</code> | Stores or updates `self._pending_render` on the current object so other methods can use it. |
| 23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._camera_reset_pending&nbsp;=&nbsp;False</code> | Stores or updates `self._camera_reset_pending` on the current object so other methods can use it. |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render_timer&nbsp;=&nbsp;QTimer(self)</code> | Creates a Qt timer, used to schedule work without blocking immediate UI interaction. |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render_timer.setSingleShot(True)</code> | Configures whether the timer runs only once per start. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render_timer.setInterval(35)</code> | Sets the timer interval in milliseconds. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render_timer.timeout.connect(self._flush_render)</code> | Connects the `self._render_timer.timeout` Qt signal to the callback inside `.connect(...)`. |
| 28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.last_dir&nbsp;=&nbsp;getattr(parent,&nbsp;"last_dir",&nbsp;Path.cwd())</code> | Stores or updates `self.last_dir` on the current object so other methods can use it. |
| 29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.groups&nbsp;=&nbsp;parent.groups&nbsp;if&nbsp;parent&nbsp;is&nbsp;not&nbsp;None&nbsp;else&nbsp;{}</code> | Stores or updates `self.groups` on the current object so other methods can use it. |
| 30 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Request&nbsp;the&nbsp;Qt6&nbsp;OpenGL&nbsp;widget&nbsp;implementation&nbsp;rather&nbsp;than&nbsp;the&nbsp;default</code> | Developer comment: Request the Qt6 OpenGL widget implementation rather than the default |
| 32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;native&nbsp;child&nbsp;QWidget&nbsp;window.&nbsp;Must&nbsp;be&nbsp;set&nbsp;before&nbsp;importing&nbsp;the&nbsp;class.</code> | Developer comment: native child QWidget window. Must be set before importing the class. |
| 33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;import&nbsp;vtkmodules.qt</code> | Loads the named Python package/module for use in this file. |
| 34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vtkmodules.qt.QVTKRWIBase&nbsp;=&nbsp;"QOpenGLWidget"</code> | Assigns the expression on the right to `vtkmodules.qt.QVTKRWIBase` for later use. |
| 35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.qt.QVTKRenderWindowInteractor&nbsp;import&nbsp;QVTKRenderWindowInteractor</code> | Imports specific classes or functions from the named module so this file can use them. |
| 36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkRenderingCore&nbsp;import&nbsp;vtkRenderer</code> | Imports specific classes or functions from the named module so this file can use them. |
| 37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkInteractionStyle&nbsp;import&nbsp;vtkInteractorStyleTrackballCamera</code> | Imports specific classes or functions from the named module so this file can use them. |
| 38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;import&nbsp;vtkmodules.vtkRenderingOpenGL2&nbsp;&nbsp;#&nbsp;Register&nbsp;OpenGL&nbsp;rendering&nbsp;backend</code> | Loads the named Python package/module for use in this file. |
| 39 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outer&nbsp;=&nbsp;QHBoxLayout(self)</code> | Creates a layout arranging items horizontally. |
| 41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;controls&nbsp;=&nbsp;QWidget()</code> | Assigns the expression on the right to `controls` for later use. |
| 42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;controls.setMaximumWidth(310)</code> | Finishes this expression or function-call argument sequence. |
| 43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout&nbsp;=&nbsp;QVBoxLayout(controls)</code> | Creates a layout stacking items vertically. |
| 44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("STL&nbsp;geometry"))</code> | Creates a text label shown in the interface. |
| 45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;browse&nbsp;=&nbsp;QPushButton("Load&nbsp;STL…")</code> | Creates a clickable button. |
| 46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;browse.clicked.connect(self.open_stl)</code> | Connects the `browse.clicked` Qt signal to the callback inside `.connect(...)`. |
| 47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(browse)</code> | Inserts the specified widget into the surrounding layout. |
| 48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_label&nbsp;=&nbsp;QLabel("No&nbsp;STL&nbsp;loaded")</code> | Creates a text label shown in the interface. |
| 49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_label.setWordWrap(True)</code> | Finishes this expression or function-call argument sequence. |
| 50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.model_label)</code> | Inserts the specified widget into the surrounding layout. |
| 51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_button&nbsp;=&nbsp;QPushButton("Model&nbsp;Color…")</code> | Creates a clickable button. |
| 52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_button.clicked.connect(self.choose_color)</code> | Connects the `self.color_button.clicked` Qt signal to the callback inside `.connect(...)`. |
| 53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.color_button)</code> | Inserts the specified widget into the surrounding layout. |
| 54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._refresh_color()</code> | Finishes this expression or function-call argument sequence. |
| 55 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;radiation:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Plot&nbsp;title"))</code> | Creates a text label shown in the interface. |
| 58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_title_edit&nbsp;=&nbsp;QLineEdit("3D&nbsp;Antenna&nbsp;Radiation&nbsp;Pattern")</code> | Creates a single-line text input. |
| 59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_title_edit.editingFinished.connect(self.update_annotations)</code> | Connects the `self.plot_title_edit.editingFinished` Qt signal to the callback inside `.connect(...)`. |
| 60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.plot_title_edit)</code> | Inserts the specified widget into the surrounding layout. |
| 61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Color&nbsp;bar&nbsp;title"))</code> | Creates a text label shown in the interface. |
| 62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_title_edit&nbsp;=&nbsp;QLineEdit("Relative&nbsp;Gain&nbsp;(dB)")</code> | Creates a single-line text input. |
| 63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_title_edit.editingFinished.connect(self.update_annotations)</code> | Connects the `self.bar_title_edit.editingFinished` Qt signal to the callback inside `.connect(...)`. |
| 64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.bar_title_edit)</code> | Inserts the specified widget into the surrounding layout. |
| 65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Radiation&nbsp;colormap"))</code> | Creates a text label shown in the interface. |
| 66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cmap_combo&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cmap_combo.addItems(["jet",&nbsp;"viridis",&nbsp;"plasma",&nbsp;"inferno",&nbsp;"magma",&nbsp;"cividis",&nbsp;"turbo",&nbsp;"coolwarm",&nbsp;"Spectral",&nbsp;"gray"])</code> | Adds several options to a dropdown in one operation. |
| 68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cmap_combo.currentTextChanged.connect(self.update_colormap)</code> | Connects the `self.cmap_combo.currentTextChanged` Qt signal to the callback inside `.connect(...)`. |
| 69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.cmap_combo)</code> | Inserts the specified widget into the surrounding layout. |
| 70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("RF&nbsp;dataset"))</code> | Creates a text label shown in the interface. |
| 71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_combo&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;key,&nbsp;group&nbsp;in&nbsp;self.groups.items():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_combo.addItem(group["name"],&nbsp;key)</code> | Adds an option to a selection widget, sometimes with hidden application data. |
| 74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.dataset_combo.currentIndexChanged.connect(self.refresh_frequencies)</code> | Connects the `self.dataset_combo.currentIndexChanged` Qt signal to the callback inside `.connect(...)`. |
| 75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.dataset_combo)</code> | Inserts the specified widget into the surrounding layout. |
| 76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Center&nbsp;frequency&nbsp;(MHz)"))</code> | Creates a text label shown in the interface. |
| 77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.frequency_combo&nbsp;=&nbsp;QComboBox()</code> | Creates a dropdown widget where the user can choose one option. |
| 78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.frequency_combo)</code> | Inserts the specified widget into the surrounding layout. |
| 79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Radiation&nbsp;origin&nbsp;(x,&nbsp;y,&nbsp;z)&nbsp;in&nbsp;STL&nbsp;units"))</code> | Creates a text label shown in the interface. |
| 80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.origin_spins&nbsp;=&nbsp;[]</code> | Stores or updates `self.origin_spins` on the current object so other methods can use it. |
| 81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;label&nbsp;in&nbsp;("X",&nbsp;"Y",&nbsp;"Z"):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(QLabel(label))</code> | Creates a text label shown in the interface. |
| 84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;spin&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;spin.setRange(-1e9,&nbsp;1e9)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;spin.setDecimals(4)</code> | Finishes this expression or function-call argument sequence. |
| 87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;row.addWidget(spin)</code> | Inserts the specified widget into the surrounding layout. |
| 88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addLayout(row)</code> | Nests one layout inside another layout. |
| 89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.origin_spins.append(spin)</code> | Finishes this expression or function-call argument sequence. |
| 90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Radiation&nbsp;scale&nbsp;(relative&nbsp;to&nbsp;STL&nbsp;size)"))</code> | Creates a text label shown in the interface. |
| 91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.scale_spin&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.scale_spin.setRange(0.001,&nbsp;1000)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.scale_spin.setDecimals(3)</code> | Finishes this expression or function-call argument sequence. |
| 94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.scale_spin.setValue(1.5)</code> | Sets the current value of a control or measurement display. |
| 95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.scale_spin)</code> | Inserts the specified widget into the surrounding layout. |
| 96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Gain&nbsp;floor&nbsp;(relative&nbsp;dB)"))</code> | Creates a text label shown in the interface. |
| 97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.floor_spin&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.floor_spin.setRange(-200,&nbsp;-0.01)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.floor_spin.setValue(-35)</code> | Sets the current value of a control or measurement display. |
| 100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.floor_spin)</code> | Inserts the specified widget into the surrounding layout. |
| 101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Color&nbsp;scale&nbsp;(relative&nbsp;gain,&nbsp;dB)"))</code> | Creates a text label shown in the interface. |
| 102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color_range_row&nbsp;=&nbsp;QHBoxLayout()</code> | Creates a layout arranging items horizontally. |
| 103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_min_spin&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_min_spin.setRange(-200,&nbsp;200)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_min_spin.setDecimals(1)</code> | Finishes this expression or function-call argument sequence. |
| 106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_min_spin.setSingleStep(5)</code> | Finishes this expression or function-call argument sequence. |
| 107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_min_spin.setValue(-35.0)</code> | Sets the current value of a control or measurement display. |
| 108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_min_spin.setPrefix("Min:&nbsp;")</code> | Finishes this expression or function-call argument sequence. |
| 109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color_range_row.addWidget(self.color_min_spin)</code> | Inserts the specified widget into the surrounding layout. |
| 110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_max_spin&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_max_spin.setRange(-200,&nbsp;200)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_max_spin.setDecimals(1)</code> | Finishes this expression or function-call argument sequence. |
| 113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_max_spin.setSingleStep(5)</code> | Finishes this expression or function-call argument sequence. |
| 114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_max_spin.setValue(0.0)</code> | Sets the current value of a control or measurement display. |
| 115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_max_spin.setPrefix("Max:&nbsp;")</code> | Finishes this expression or function-call argument sequence. |
| 116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color_range_row.addWidget(self.color_max_spin)</code> | Inserts the specified widget into the surrounding layout. |
| 117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addLayout(color_range_row)</code> | Nests one layout inside another layout. |
| 118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_min_spin.valueChanged.connect(self.update_color_scale)</code> | Connects the `self.color_min_spin.valueChanged` Qt signal to the callback inside `.connect(...)`. |
| 119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_max_spin.valueChanged.connect(self.update_color_scale)</code> | Connects the `self.color_max_spin.valueChanged` Qt signal to the callback inside `.connect(...)`. |
| 120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Gaussian&nbsp;sigma&nbsp;(samples)"))</code> | Creates a text label shown in the interface. |
| 121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.sigma_spin&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.sigma_spin.setRange(0,&nbsp;50)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.sigma_spin.setDecimals(2)</code> | Finishes this expression or function-call argument sequence. |
| 124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.sigma_spin.setValue(2)</code> | Sets the current value of a control or measurement display. |
| 125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.sigma_spin)</code> | Inserts the specified widget into the surrounding layout. |
| 126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(QLabel("Pattern&nbsp;opacity"))</code> | Creates a text label shown in the interface. |
| 127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.opacity_spin&nbsp;=&nbsp;QDoubleSpinBox()</code> | Creates a signed numeric input with stepper arrows. |
| 128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.opacity_spin.setRange(0.05,&nbsp;1.0)</code> | Sets the allowed minimum and maximum for a numeric control. |
| 129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.opacity_spin.setSingleStep(0.05)</code> | Finishes this expression or function-call argument sequence. |
| 130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.opacity_spin.setValue(0.75)</code> | Sets the current value of a control or measurement display. |
| 131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.opacity_spin)</code> | Inserts the specified widget into the surrounding layout. |
| 132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;update&nbsp;=&nbsp;QPushButton("Render&nbsp;radiation&nbsp;pattern")</code> | Creates a clickable button. |
| 133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;update.clicked.connect(self.render_pattern)</code> | Connects the `update.clicked` Qt signal to the callback inside `.connect(...)`. |
| 134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(update)</code> | Inserts the specified widget into the surrounding layout. |
| 135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.refresh_frequencies()</code> | Finishes this expression or function-call argument sequence. |
| 136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addStretch(1)</code> | Finishes this expression or function-call argument sequence. |
| 137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.status_label&nbsp;=&nbsp;QLabel("Drag&nbsp;to&nbsp;rotate;&nbsp;scroll&nbsp;to&nbsp;zoom.")</code> | Creates a text label shown in the interface. |
| 138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.status_label.setWordWrap(True)</code> | Finishes this expression or function-call argument sequence. |
| 139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;layout.addWidget(self.status_label)</code> | Inserts the specified widget into the surrounding layout. |
| 140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outer.addWidget(controls)</code> | Inserts the specified widget into the surrounding layout. |
| 141 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.vtk_widget&nbsp;=&nbsp;QVTKRenderWindowInteractor(self)</code> | Stores or updates `self.vtk_widget` on the current object so other methods can use it. |
| 143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outer.addWidget(self.vtk_widget,&nbsp;1)</code> | Inserts the specified widget into the surrounding layout. |
| 144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer&nbsp;=&nbsp;vtkRenderer()</code> | Stores or updates `self.renderer` on the current object so other methods can use it. |
| 145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.SetBackground(1.0,&nbsp;1.0,&nbsp;1.0)</code> | Finishes this expression or function-call argument sequence. |
| 146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)</code> | Configures or updates a native VTK renderer, actor, camera, or display property. |
| 147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.vtk_widget.GetRenderWindow().GetInteractor().SetInteractorStyle(</code> | Configures or updates a native VTK renderer, actor, camera, or display property. |
| 148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vtkInteractorStyleTrackballCamera())</code> | Finishes this expression or function-call argument sequence. |
| 149 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;showEvent(self,&nbsp;event):</code> | Defines the named function/method; indented lines below form its body. |
| 151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;super().showEvent(event)</code> | Finishes this expression or function-call argument sequence. |
| 152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self._initialized:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QTimer.singleShot(0,&nbsp;self._initialize_vtk)</code> | Finishes this expression or function-call argument sequence. |
| 154 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_initialize_vtk(self):</code> | Defines the named function/method; indented lines below form its body. |
| 156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self._initialized:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._initialized&nbsp;=&nbsp;True</code> | Stores or updates `self._initialized` on the current object so other methods can use it. |
| 159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.vtk_widget.Initialize()</code> | Finishes this expression or function-call argument sequence. |
| 160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.vtk_widget.Start()</code> | Finishes this expression or function-call argument sequence. |
| 161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render()</code> | Finishes this expression or function-call argument sequence. |
| 162 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_render(self,&nbsp;reset_camera=False):</code> | Defines the named function/method; indented lines below form its body. |
| 164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Coalesce&nbsp;updates,&nbsp;avoiding&nbsp;a&nbsp;heavy&nbsp;GL&nbsp;render&nbsp;inside&nbsp;click&nbsp;handlers."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._camera_reset_pending&nbsp;\|=&nbsp;bool(reset_camera)</code> | Stores or updates `self._camera_reset_pending \|` on the current object so other methods can use it. |
| 166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self._initialized:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render_timer.start()</code> | Finishes this expression or function-call argument sequence. |
| 168 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_flush_render(self):</code> | Defines the named function/method; indented lines below form its body. |
| 170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self._initialized&nbsp;or&nbsp;not&nbsp;self.isVisible():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self._camera_reset_pending:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.ResetCamera()</code> | Finishes this expression or function-call argument sequence. |
| 174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._camera_reset_pending&nbsp;=&nbsp;False</code> | Stores or updates `self._camera_reset_pending` on the current object so other methods can use it. |
| 175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.vtk_widget.GetRenderWindow().Render()</code> | Asks VTK to redraw the interactive 3D scene. |
| 176 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_refresh_color(self):</code> | Defines the named function/method; indented lines below form its body. |
| 178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color&nbsp;=&nbsp;self.model_color</code> | Assigns the expression on the right to `color` for later use. |
| 179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fg&nbsp;=&nbsp;"white"&nbsp;if&nbsp;color.lightness()&nbsp;&lt;&nbsp;125&nbsp;else&nbsp;"black"</code> | Assigns the expression on the right to `fg` for later use. |
| 180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.color_button.setStyleSheet(f"background-color:&nbsp;{color.name()};&nbsp;color:&nbsp;{fg};")</code> | Finishes this expression or function-call argument sequence. |
| 181 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;choose_color(self):</code> | Defines the named function/method; indented lines below form its body. |
| 183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color&nbsp;=&nbsp;QColorDialog.getColor(self.model_color,&nbsp;self,&nbsp;"Model&nbsp;color")</code> | Opens Qt’s color picker. |
| 184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;color.isValid():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_color&nbsp;=&nbsp;color</code> | Stores or updates `self.model_color` on the current object so other methods can use it. |
| 187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._refresh_color()</code> | Finishes this expression or function-call argument sequence. |
| 188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.model_actor&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_actor.GetProperty().SetColor(*color.getRgbF()[:3])</code> | Finishes this expression or function-call argument sequence. |
| 190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render()</code> | Finishes this expression or function-call argument sequence. |
| 191 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;open_stl(self):</code> | Defines the named function/method; indented lines below form its body. |
| 193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;path,&nbsp;_&nbsp;=&nbsp;QFileDialog.getOpenFileName(</code> | Opens a file picker or a save-file picker. |
| 194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,&nbsp;"Open&nbsp;STL",&nbsp;str(self.last_dir),&nbsp;"STL&nbsp;(*.stl);;All&nbsp;Files&nbsp;(*)")</code> | Finishes this expression or function-call argument sequence. |
| 195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;path:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;stl.mesh&nbsp;import&nbsp;Mesh</code> | Imports specific classes or functions from the named module so this file can use them. |
| 199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mesh&nbsp;=&nbsp;Mesh.from_file(path)</code> | Assigns the expression on the right to `mesh` for later use. |
| 200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vectors&nbsp;=&nbsp;np.asarray(mesh.vectors,&nbsp;dtype=float)</code> | Converts input data to a NumPy array. |
| 201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;len(vectors)&nbsp;or&nbsp;not&nbsp;np.isfinite(vectors).all():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("STL&nbsp;is&nbsp;empty&nbsp;or&nbsp;contains&nbsp;non-finite&nbsp;vertices")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_vertices&nbsp;=&nbsp;vectors</code> | Stores or updates `self.model_vertices` on the current object so other methods can use it. |
| 204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_path&nbsp;=&nbsp;Path(path)</code> | Stores or updates `self.model_path` on the current object so other methods can use it. |
| 205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.last_dir&nbsp;=&nbsp;self.model_path.parent</code> | Stores or updates `self.last_dir` on the current object so other methods can use it. |
| 206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._draw_stl(vectors)</code> | Finishes this expression or function-call argument sequence. |
| 207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_label.setText(f"{self.model_path.name}&nbsp;—&nbsp;{len(vectors):,}&nbsp;triangles")</code> | Updates text shown in an existing widget. |
| 208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Render&nbsp;the&nbsp;STL&nbsp;first;&nbsp;RF&nbsp;geometry&nbsp;remains&nbsp;explicitly&nbsp;user-controlled</code> | Developer comment: Render the STL first; RF geometry remains explicitly user-controlled |
| 209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;via&nbsp;the&nbsp;Render&nbsp;radiation&nbsp;pattern&nbsp;button.</code> | Developer comment: via the Render radiation pattern button. |
| 210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;Exception&nbsp;as&nbsp;exc:</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QMessageBox.critical(self,&nbsp;"STL&nbsp;load&nbsp;error",&nbsp;str(exc))</code> | Displays an informational, warning, or error popup to the user. |
| 212 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | Decorator: this method does not receive an automatic `self` argument. |
| 214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_triangle_polydata(triangles,&nbsp;scalar_values=None):</code> | Defines the named function/method; indented lines below form its body. |
| 215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkCommonDataModel&nbsp;import&nbsp;vtkPolyData,&nbsp;vtkCellArray</code> | Imports specific classes or functions from the named module so this file can use them. |
| 216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.util.numpy_support&nbsp;import&nbsp;numpy_to_vtk,&nbsp;numpy_to_vtkIdTypeArray</code> | Imports specific classes or functions from the named module so this file can use them. |
| 217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;triangles&nbsp;=&nbsp;np.ascontiguousarray(triangles,&nbsp;dtype=np.float64)</code> | Assigns the expression on the right to `triangles` for later use. |
| 218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;verts&nbsp;=&nbsp;triangles.reshape(-1,&nbsp;3)</code> | Assigns the expression on the right to `verts` for later use. |
| 219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkCommonCore&nbsp;import&nbsp;vtkPoints</code> | Imports specific classes or functions from the named module so this file can use them. |
| 220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points&nbsp;=&nbsp;vtkPoints()</code> | Assigns the expression on the right to `points` for later use. |
| 221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points.SetData(numpy_to_vtk(verts,&nbsp;deep=True))</code> | Configures or updates a native VTK renderer, actor, camera, or display property. |
| 222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;poly&nbsp;=&nbsp;vtkPolyData()</code> | Assigns the expression on the right to `poly` for later use. |
| 223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;poly.SetPoints(points)</code> | Finishes this expression or function-call argument sequence. |
| 224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;n&nbsp;=&nbsp;len(triangles)</code> | Assigns the expression on the right to `n` for later use. |
| 225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;connectivity&nbsp;=&nbsp;np.column_stack([np.full(n,&nbsp;3,&nbsp;dtype=np.int64),</code> | Assigns the expression on the right to `connectivity` for later use. |
| 226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;np.arange(n&nbsp;*&nbsp;3,&nbsp;dtype=np.int64).reshape(n,&nbsp;3)]).ravel()</code> | Finishes this expression or function-call argument sequence. |
| 227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cells&nbsp;=&nbsp;vtkCellArray()</code> | Assigns the expression on the right to `cells` for later use. |
| 228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cells.SetCells(n,&nbsp;numpy_to_vtkIdTypeArray(connectivity,&nbsp;deep=True))</code> | Configures or updates a native VTK renderer, actor, camera, or display property. |
| 229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;poly.SetPolys(cells)</code> | Finishes this expression or function-call argument sequence. |
| 230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;scalar_values&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scalars&nbsp;=&nbsp;numpy_to_vtk(np.asarray(scalar_values,&nbsp;dtype=np.float64).ravel(),&nbsp;deep=True)</code> | Converts input data to a NumPy array. |
| 232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scalars.SetName("Relative&nbsp;Gain&nbsp;(dB)")</code> | Finishes this expression or function-call argument sequence. |
| 233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;poly.GetPointData().SetScalars(scalars)</code> | Finishes this expression or function-call argument sequence. |
| 234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;poly</code> | Returns this computed value to the caller; the function ends here. |
| 235 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_draw_stl(self,&nbsp;vertices):</code> | Defines the named function/method; indented lines below form its body. |
| 237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkRenderingCore&nbsp;import&nbsp;vtkActor,&nbsp;vtkPolyDataMapper</code> | Imports specific classes or functions from the named module so this file can use them. |
| 238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.model_actor&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.RemoveActor(self.model_actor)</code> | Finishes this expression or function-call argument sequence. |
| 240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapper&nbsp;=&nbsp;vtkPolyDataMapper()</code> | Assigns the expression on the right to `mapper` for later use. |
| 241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapper.SetInputData(self._triangle_polydata(vertices))</code> | Finishes this expression or function-call argument sequence. |
| 242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;actor&nbsp;=&nbsp;vtkActor()</code> | Assigns the expression on the right to `actor` for later use. |
| 243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;actor.SetMapper(mapper)</code> | Finishes this expression or function-call argument sequence. |
| 244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;actor.GetProperty().SetColor(*self.model_color.getRgbF()[:3])</code> | Finishes this expression or function-call argument sequence. |
| 245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.AddActor(actor)</code> | Finishes this expression or function-call argument sequence. |
| 246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model_actor&nbsp;=&nbsp;actor</code> | Stores or updates `self.model_actor` on the current object so other methods can use it. |
| 247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render(reset_camera=True)</code> | Stores or updates `self._render(reset_camera` on the current object so other methods can use it. |
| 248 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;refresh_frequencies(self,&nbsp;*_):</code> | Defines the named function/method; indented lines below form its body. |
| 250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self.radiation_mode:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;current&nbsp;=&nbsp;self.frequency_combo.currentData()</code> | Assigns the expression on the right to `current` for later use. |
| 253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.frequency_combo.blockSignals(True)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.frequency_combo.clear()</code> | Finishes this expression or function-call argument sequence. |
| 255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group&nbsp;=&nbsp;self.groups.get(self.dataset_combo.currentData())</code> | Assigns the expression on the right to `group` for later use. |
| 256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;group&nbsp;is&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.frequency_combo.blockSignals(False)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;values&nbsp;=&nbsp;group.get("frequency_options")</code> | Assigns the expression on the right to `values` for later use. |
| 260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;values&nbsp;is&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;values&nbsp;=&nbsp;np.sort(group["flat"]["Freq"].dropna().unique())</code> | Gets the distinct values in a column, useful for frequency or angle choices. |
| 262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;freq&nbsp;in&nbsp;values:</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 263 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.frequency_combo.addItem(f"{freq:g}&nbsp;MHz",&nbsp;float(freq))</code> | Adds an option to a selection widget, sometimes with hidden application data. |
| 264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;idx&nbsp;=&nbsp;self.frequency_combo.findData(current)</code> | Assigns the expression on the right to `idx` for later use. |
| 265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;idx&nbsp;&gt;=&nbsp;0:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.frequency_combo.setCurrentIndex(idx)</code> | Changes the current visible/selected item in a Qt control. |
| 267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.frequency_combo.blockSignals(False)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 268 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_color_limits(self):</code> | Defines the named function/method; indented lines below form its body. |
| 270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vmin&nbsp;=&nbsp;self.color_min_spin.value()</code> | Assigns the expression on the right to `vmin` for later use. |
| 271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vmax&nbsp;=&nbsp;self.color_max_spin.value()</code> | Assigns the expression on the right to `vmax` for later use. |
| 272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;vmin&nbsp;&gt;=&nbsp;vmax:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("Color&nbsp;scale&nbsp;minimum&nbsp;must&nbsp;be&nbsp;less&nbsp;than&nbsp;maximum.")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;vmin,&nbsp;vmax</code> | Returns this computed value to the caller; the function ends here. |
| 275 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;update_annotations(self):</code> | Defines the named function/method; indented lines below form its body. |
| 277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Update&nbsp;titles&nbsp;without&nbsp;regenerating&nbsp;mesh&nbsp;geometry&nbsp;or&nbsp;resetting&nbsp;camera."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self.radiation_mode:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.bar_actor&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_actor.SetTitle(self.bar_title_edit.text().strip())</code> | Finishes this expression or function-call argument sequence. |
| 282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_actor.Modified()</code> | Finishes this expression or function-call argument sequence. |
| 283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;hasattr(self,&nbsp;"title_actor"):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.title_actor.SetInput(self.plot_title_edit.text().strip())</code> | Finishes this expression or function-call argument sequence. |
| 285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.title_actor.Modified()</code> | Finishes this expression or function-call argument sequence. |
| 286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render()</code> | Finishes this expression or function-call argument sequence. |
| 287 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;update_colormap(self,&nbsp;*_):</code> | Defines the named function/method; indented lines below form its body. |
| 289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Update&nbsp;VTK's&nbsp;LUT&nbsp;while&nbsp;preserving&nbsp;geometry&nbsp;and&nbsp;scalar&nbsp;range."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self.radiation_mode&nbsp;or&nbsp;not&nbsp;hasattr(self,&nbsp;"pattern_lut"):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 292 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;import&nbsp;matplotlib</code> | Loads the named Python package/module for use in this file. |
| 293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cmap&nbsp;=&nbsp;matplotlib.colormaps.get_cmap(self.cmap_combo.currentText())</code> | Assigns the expression on the right to `cmap` for later use. |
| 294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;i&nbsp;in&nbsp;range(256):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_lut.SetTableValue(i,&nbsp;*cmap(i&nbsp;/&nbsp;255.0))</code> | Finishes this expression or function-call argument sequence. |
| 296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_lut.Build()</code> | Finishes this expression or function-call argument sequence. |
| 297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_lut.Modified()</code> | Finishes this expression or function-call argument sequence. |
| 298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_mapper.Modified()</code> | Finishes this expression or function-call argument sequence. |
| 299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.bar_actor&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_actor.Modified()</code> | Finishes this expression or function-call argument sequence. |
| 301 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render()</code> | Finishes this expression or function-call argument sequence. |
| 302 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 303 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;update_color_scale(self,&nbsp;*_):</code> | Defines the named function/method; indented lines below form its body. |
| 304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Apply&nbsp;independent&nbsp;scale&nbsp;limits&nbsp;to&nbsp;both&nbsp;surface&nbsp;colors&nbsp;and&nbsp;the&nbsp;scalar&nbsp;bar.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 305 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Does&nbsp;not&nbsp;recalculate&nbsp;the&nbsp;geometry,&nbsp;smooth&nbsp;the&nbsp;measurement,&nbsp;or&nbsp;reset&nbsp;the&nbsp;camera.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 307 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Values&nbsp;outside&nbsp;the&nbsp;color&nbsp;range&nbsp;saturate&nbsp;at&nbsp;its&nbsp;endpoints.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self.radiation_mode&nbsp;or&nbsp;not&nbsp;hasattr(self,&nbsp;"pattern_mapper"):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;low,&nbsp;high&nbsp;=&nbsp;self._color_limits()</code> | Assigns the expression on the right to `low, high` for later use. |
| 313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;ValueError:</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.status_label.setText("Color&nbsp;minimum&nbsp;must&nbsp;be&nbsp;less&nbsp;than&nbsp;maximum.")</code> | Updates text shown in an existing widget. |
| 315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_lut.SetRange(low,&nbsp;high)</code> | Finishes this expression or function-call argument sequence. |
| 317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_lut.Build()</code> | Finishes this expression or function-call argument sequence. |
| 318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_mapper.SetScalarRange(low,&nbsp;high)</code> | Finishes this expression or function-call argument sequence. |
| 319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_mapper.Modified()</code> | Finishes this expression or function-call argument sequence. |
| 320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.bar_actor&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 321 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_actor.SetLookupTable(self.pattern_lut)</code> | Finishes this expression or function-call argument sequence. |
| 322 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_actor.Modified()</code> | Finishes this expression or function-call argument sequence. |
| 323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render()</code> | Finishes this expression or function-call argument sequence. |
| 324 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;render_pattern(self):</code> | Defines the named function/method; indented lines below form its body. |
| 326 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;self.radiation_mode:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group&nbsp;=&nbsp;self.groups.get(self.dataset_combo.currentData())</code> | Assigns the expression on the right to `group` for later use. |
| 329 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;freq&nbsp;=&nbsp;self.frequency_combo.currentData()</code> | Assigns the expression on the right to `freq` for later use. |
| 330 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;group&nbsp;is&nbsp;None&nbsp;or&nbsp;freq&nbsp;is&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 331 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.status_label.setText("Select&nbsp;a&nbsp;loaded&nbsp;RF&nbsp;dataset&nbsp;and&nbsp;frequency.")</code> | Updates text shown in an existing widget. |
| 332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;scipy.ndimage&nbsp;import&nbsp;gaussian_filter</code> | Imports specific classes or functions from the named module so this file can use them. |
| 335 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkRenderingCore&nbsp;import&nbsp;vtkActor,&nbsp;vtkPolyDataMapper</code> | Imports specific classes or functions from the named module so this file can use them. |
| 336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkRenderingAnnotation&nbsp;import&nbsp;vtkScalarBarActor</code> | Imports specific classes or functions from the named module so this file can use them. |
| 337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkCommonCore&nbsp;import&nbsp;vtkLookupTable</code> | Imports specific classes or functions from the named module so this file can use them. |
| 338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;import&nbsp;matplotlib</code> | Loads the named Python package/module for use in this file. |
| 339 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;df&nbsp;=&nbsp;group["flat"]</code> | Assigns the expression on the right to `df` for later use. |
| 340 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;selection&nbsp;=&nbsp;df.loc[np.isclose(df["Freq"].to_numpy(dtype=float),&nbsp;float(freq))]</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 341 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;selection.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("No&nbsp;data&nbsp;for&nbsp;selected&nbsp;frequency")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Conventions&nbsp;match&nbsp;the&nbsp;supplied&nbsp;RF&nbsp;script:&nbsp;Phi&nbsp;=&nbsp;elevation,&nbsp;Theta&nbsp;=&nbsp;azimuth.</code> | Developer comment: Conventions match the supplied RF script: Phi = elevation, Theta = azimuth. |
| 344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;grid&nbsp;=&nbsp;selection.pivot_table(index="Phi",&nbsp;columns="Theta",&nbsp;values="PdB",&nbsp;aggfunc="mean")</code> | Rearranges flat samples into a 2D grid indexed by scan angle. |
| 345 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;grid&nbsp;=&nbsp;grid.sort_index().sort_index(axis=1)</code> | Assigns the expression on the right to `grid` for later use. |
| 346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;min(grid.shape)&nbsp;&lt;&nbsp;2:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 347 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("Need&nbsp;&gt;=2&nbsp;distinct&nbsp;elevations&nbsp;and&nbsp;&gt;=2&nbsp;azimuths")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 348 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elevations&nbsp;=&nbsp;grid.index.to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;azimuths&nbsp;=&nbsp;grid.columns.to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 350 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;full_azimuth&nbsp;=&nbsp;np.isclose(azimuths[-1]&nbsp;-&nbsp;azimuths[0],&nbsp;360,&nbsp;atol=1.5)</code> | Assigns the expression on the right to `full_azimuth` for later use. |
| 351 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;full_azimuth:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 352 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;grid&nbsp;=&nbsp;grid.iloc[:,&nbsp;:-1]</code> | Assigns the expression on the right to `grid` for later use. |
| 353 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;azimuths&nbsp;=&nbsp;grid.columns.to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 354 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;grid&nbsp;=&nbsp;grid.interpolate(axis=0,&nbsp;method="index",&nbsp;limit_direction="both")</code> | Assigns the expression on the right to `grid` for later use. |
| 355 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;grid&nbsp;=&nbsp;grid.interpolate(axis=1,&nbsp;method="index",&nbsp;limit_direction="both")</code> | Assigns the expression on the right to `grid` for later use. |
| 356 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;grid.isna().any().any():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 357 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("Cannot&nbsp;interpolate&nbsp;missing&nbsp;grid&nbsp;samples")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 358 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;db&nbsp;=&nbsp;grid.to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 359 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;smooth&nbsp;=&nbsp;gaussian_filter(db,&nbsp;sigma=self.sigma_spin.value(),</code> | Smooths neighboring gain values using Gaussian weights. |
| 360 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mode=("nearest",&nbsp;"wrap"&nbsp;if&nbsp;full_azimuth&nbsp;else&nbsp;"nearest"))</code> | Assigns the expression on the right to `mode` for later use. |
| 361 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rel&nbsp;=&nbsp;smooth&nbsp;-&nbsp;float(np.max(smooth))</code> | Assigns the expression on the right to `rel` for later use. |
| 362 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;radius&nbsp;=&nbsp;10&nbsp;**&nbsp;(np.maximum(rel,&nbsp;self.floor_spin.value())&nbsp;/&nbsp;20.0)</code> | Assigns the expression on the right to `radius` for later use. |
| 363 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;hasattr(self,&nbsp;"model_vertices"):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 364 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;size&nbsp;=&nbsp;float(np.ptp(self.model_vertices.reshape(-1,&nbsp;3),&nbsp;axis=0).max())</code> | Assigns the expression on the right to `size` for later use. |
| 365 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;size&nbsp;&lt;=&nbsp;0:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 366 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("Model&nbsp;dimensions&nbsp;are&nbsp;zero")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 367 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 368 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;size&nbsp;=&nbsp;1.0</code> | Assigns the expression on the right to `size` for later use. |
| 369 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;radius&nbsp;*=&nbsp;size&nbsp;*&nbsp;self.scale_spin.value()</code> | Finishes this expression or function-call argument sequence. |
| 370 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;th,&nbsp;ph&nbsp;=&nbsp;np.meshgrid(np.deg2rad(elevations),&nbsp;np.deg2rad(azimuths),&nbsp;indexing="ij")</code> | Converts degrees to radians for trigonometric calculations. |
| 371 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;origin&nbsp;=&nbsp;np.array([x.value()&nbsp;for&nbsp;x&nbsp;in&nbsp;self.origin_spins])</code> | Creates a NumPy array containing the listed values. |
| 372 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points&nbsp;=&nbsp;np.stack((radius&nbsp;*&nbsp;np.cos(th)&nbsp;*&nbsp;np.cos(ph),</code> | Combines separate coordinate arrays into a last dimension, such as `(x, y, z)`. |
| 373 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;radius&nbsp;*&nbsp;np.cos(th)&nbsp;*&nbsp;np.sin(ph),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 374 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;radius&nbsp;*&nbsp;np.sin(th)),&nbsp;axis=-1)&nbsp;+&nbsp;origin</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 375 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;full_azimuth:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 376 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points&nbsp;=&nbsp;np.concatenate([points,&nbsp;points[:,&nbsp;:1]],&nbsp;axis=1)</code> | Joins arrays, for example to close an angular seam. |
| 377 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rel&nbsp;=&nbsp;np.concatenate([rel,&nbsp;rel[:,&nbsp;:1]],&nbsp;axis=1)</code> | Joins arrays, for example to close an angular seam. |
| 378 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;triangles&nbsp;=&nbsp;np.concatenate((np.stack((points[:-1,:-1],&nbsp;points[1:,:-1],&nbsp;points[1:,1:]),&nbsp;axis=-2),</code> | Combines separate coordinate arrays into a last dimension, such as `(x, y, z)`. |
| 379 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;np.stack((points[:-1,:-1],&nbsp;points[1:,1:],&nbsp;points[:-1,1:]),&nbsp;axis=-2)),&nbsp;axis=0).reshape(-1,3,3)</code> | Combines separate coordinate arrays into a last dimension, such as `(x, y, z)`. |
| 380 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;values&nbsp;=&nbsp;np.concatenate((np.stack((rel[:-1,:-1],&nbsp;rel[1:,:-1],&nbsp;rel[1:,1:]),&nbsp;axis=-1),</code> | Combines separate coordinate arrays into a last dimension, such as `(x, y, z)`. |
| 381 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;np.stack((rel[:-1,:-1],&nbsp;rel[1:,1:],&nbsp;rel[:-1,1:]),&nbsp;axis=-1)),axis=0).reshape(-1,3)</code> | Combines separate coordinate arrays into a last dimension, such as `(x, y, z)`. |
| 382 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;poly&nbsp;=&nbsp;self._triangle_polydata(triangles,&nbsp;values)</code> | Assigns the expression on the right to `poly` for later use. |
| 383 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lut&nbsp;=&nbsp;vtkLookupTable()</code> | Assigns the expression on the right to `lut` for later use. |
| 384 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lut.SetNumberOfTableValues(256)</code> | Finishes this expression or function-call argument sequence. |
| 385 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cmap&nbsp;=&nbsp;matplotlib.colormaps.get_cmap(self.cmap_combo.currentText())</code> | Assigns the expression on the right to `cmap` for later use. |
| 386 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;i&nbsp;in&nbsp;range(256):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 387 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lut.SetTableValue(i,&nbsp;*cmap(i/255))</code> | Finishes this expression or function-call argument sequence. |
| 388 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vmin,&nbsp;vmax&nbsp;=&nbsp;self._color_limits()</code> | Assigns the expression on the right to `vmin, vmax` for later use. |
| 389 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lut.SetRange(vmin,&nbsp;vmax)</code> | Finishes this expression or function-call argument sequence. |
| 390 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lut.Build()</code> | Finishes this expression or function-call argument sequence. |
| 391 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapper&nbsp;=&nbsp;vtkPolyDataMapper()</code> | Assigns the expression on the right to `mapper` for later use. |
| 392 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapper.SetInputData(poly)</code> | Finishes this expression or function-call argument sequence. |
| 393 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapper.SetLookupTable(lut)</code> | Finishes this expression or function-call argument sequence. |
| 394 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapper.SetScalarRange(vmin,&nbsp;vmax)</code> | Finishes this expression or function-call argument sequence. |
| 395 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mapper.SetScalarModeToUsePointData()</code> | Finishes this expression or function-call argument sequence. |
| 396 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;actor&nbsp;=&nbsp;vtkActor()</code> | Assigns the expression on the right to `actor` for later use. |
| 397 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;actor.SetMapper(mapper)</code> | Finishes this expression or function-call argument sequence. |
| 398 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;actor.GetProperty().SetOpacity(self.opacity_spin.value())</code> | Finishes this expression or function-call argument sequence. |
| 399 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.pattern_actor&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 400 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.RemoveActor(self.pattern_actor)</code> | Finishes this expression or function-call argument sequence. |
| 401 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.AddActor(actor)</code> | Finishes this expression or function-call argument sequence. |
| 402 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_actor&nbsp;=&nbsp;actor</code> | Stores or updates `self.pattern_actor` on the current object so other methods can use it. |
| 403 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_mapper&nbsp;=&nbsp;mapper</code> | Stores or updates `self.pattern_mapper` on the current object so other methods can use it. |
| 404 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.pattern_lut&nbsp;=&nbsp;lut</code> | Stores or updates `self.pattern_lut` on the current object so other methods can use it. |
| 405 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.bar_actor&nbsp;is&nbsp;not&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 406 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.RemoveActor2D(self.bar_actor)</code> | Finishes this expression or function-call argument sequence. |
| 407 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;bar&nbsp;=&nbsp;vtkScalarBarActor()</code> | Assigns the expression on the right to `bar` for later use. |
| 408 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;bar.SetLookupTable(lut)</code> | Finishes this expression or function-call argument sequence. |
| 409 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;bar.SetTitle(self.bar_title_edit.text().strip())</code> | Finishes this expression or function-call argument sequence. |
| 410 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;bar.SetNumberOfLabels(5)</code> | Finishes this expression or function-call argument sequence. |
| 411 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.AddActor2D(bar)</code> | Finishes this expression or function-call argument sequence. |
| 412 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.bar_actor&nbsp;=&nbsp;bar</code> | Stores or updates `self.bar_actor` on the current object so other methods can use it. |
| 413 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;hasattr(self,&nbsp;"title_actor"):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 414 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from&nbsp;vtkmodules.vtkRenderingCore&nbsp;import&nbsp;vtkTextActor</code> | Imports specific classes or functions from the named module so this file can use them. |
| 415 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.title_actor&nbsp;=&nbsp;vtkTextActor()</code> | Stores or updates `self.title_actor` on the current object so other methods can use it. |
| 416 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.title_actor.GetTextProperty().SetFontSize(22)</code> | Finishes this expression or function-call argument sequence. |
| 417 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.title_actor.GetTextProperty().SetColor(0.1,&nbsp;0.1,&nbsp;0.1)</code> | Finishes this expression or function-call argument sequence. |
| 418 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.title_actor.GetTextProperty().SetJustificationToCentered()</code> | Finishes this expression or function-call argument sequence. |
| 419 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.title_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()</code> | Finishes this expression or function-call argument sequence. |
| 420 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.title_actor.SetPosition(0.47,&nbsp;0.955)</code> | Finishes this expression or function-call argument sequence. |
| 421 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.renderer.AddActor2D(self.title_actor)</code> | Finishes this expression or function-call argument sequence. |
| 422 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.update_annotations()</code> | Finishes this expression or function-call argument sequence. |
| 423 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._render(reset_camera=True)</code> | Stores or updates `self._render(reset_camera` on the current object so other methods can use it. |
| 424 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.status_label.setText(f"{group['name']}&nbsp;\|&nbsp;{freq:g}&nbsp;MHz&nbsp;\|&nbsp;{len(triangles):,}&nbsp;triangles")</code> | Updates text shown in an existing widget. |
| 425 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;Exception&nbsp;as&nbsp;exc:</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 426 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QMessageBox.warning(self,&nbsp;"Radiation&nbsp;pattern",&nbsp;str(exc))</code> | Displays an informational, warning, or error popup to the user. |
| 427 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 428 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;closeEvent(self,&nbsp;event):</code> | Defines the named function/method; indented lines below form its body. |
| 429 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 430 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.vtk_widget.Finalize()</code> | Finishes this expression or function-call argument sequence. |
| 431 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.vtk_widget.GetRenderWindow().SetInteractor(None)</code> | Configures or updates a native VTK renderer, actor, camera, or display property. |
| 432 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;Exception:</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 433 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pass</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 434 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;super().closeEvent(event)</code> | Finishes this expression or function-call argument sequence. |


## `src/Lolth/plotting/__init__.py`

Package marker file; Python treats this directory as an importable package.

This file is empty on purpose: it marks the package directory. There are no executable lines to explain.


## `src/Lolth/plotting/charts.py`

2D plotting: linear, polar, heatmap, and CDF rendering.

**Code landmarks:** `PlotMixin` (line 8, class), `plot_coordinate_labels` (line 9, function), `draw_message` (line 15, function), `split_theta_sweeps` (line 25, function), `update_heatmap_datasets` (line 33, function), `update_plot` (line 45, function), `_paint_selected_plot` (line 50, function), `plot_heatmap` (line 62, function), `plot_overlay` (line 121, function), `plot_cdf` (line 188, function), `refresh_regions` (line 228, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>"""2D&nbsp;Matplotlib&nbsp;rendering&nbsp;methods&nbsp;mixed&nbsp;into&nbsp;the&nbsp;main&nbsp;window."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 2 | <code>import&nbsp;numpy&nbsp;as&nbsp;np</code> | Loads the named Python package/module for use in this file. |
| 3 | <code>import&nbsp;pandas&nbsp;as&nbsp;pd</code> | Loads the named Python package/module for use in this file. |
| 4 | <code>from&nbsp;PyQt6.QtWidgets&nbsp;import&nbsp;QMessageBox</code> | Imports specific classes or functions from the named module so this file can use them. |
| 5 | <code>from&nbsp;..processing.cdf&nbsp;import&nbsp;cdf_statistics</code> | Imports specific classes or functions from the named module so this file can use them. |
| 6 | <code>from&nbsp;.coordinates&nbsp;import&nbsp;scan_to_az_el</code> | Imports specific classes or functions from the named module so this file can use them. |
| 7 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 8 | <code>class&nbsp;PlotMixin:</code> | Starts a class definition; any base classes in parentheses supply inherited behavior. |
| 9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;plot_coordinate_labels(self):</code> | Defines the named function/method; indented lines below form its body. |
| 10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Axis&nbsp;labels&nbsp;corresponding&nbsp;to&nbsp;raw&nbsp;scan&nbsp;angles&nbsp;or&nbsp;converted&nbsp;Az/El."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;(("Theta",&nbsp;"Phi")&nbsp;if&nbsp;self.plot_phi_theta.isChecked()</code> | Returns this computed value to the caller; the function ends here. |
| 12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else&nbsp;("Azimuth",&nbsp;"Elevation"))</code> | Finishes this expression or function-call argument sequence. |
| 13 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | Decorator: this method does not receive an automatic `self` argument. |
| 15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;draw_message(canvas,&nbsp;message):</code> | Defines the named function/method; indented lines below form its body. |
| 16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig&nbsp;=&nbsp;canvas.figure</code> | Assigns the expression on the right to `fig` for later use. |
| 17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig.clear()</code> | Finishes this expression or function-call argument sequence. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax&nbsp;=&nbsp;fig.add_subplot(111)</code> | Assigns the expression on the right to `ax` for later use. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.text(.5,&nbsp;.5,&nbsp;message,&nbsp;transform=ax.transAxes,&nbsp;ha="center",&nbsp;va="center",&nbsp;wrap=True)</code> | Finishes this expression or function-call argument sequence. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.axis("off")</code> | Finishes this expression or function-call argument sequence. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;canvas.draw_idle()</code> | Requests a Matplotlib redraw when the GUI becomes idle, instead of drawing immediately. |
| 22 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 23 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | Decorator: this method does not receive an automatic `self` argument. |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;split_theta_sweeps(data):</code> | Defines the named function/method; indented lines below form its body. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;data.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;[]</code> | Returns this computed value to the caller; the function ends here. |
| 28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;theta&nbsp;=&nbsp;data["Theta"].to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;split&nbsp;=&nbsp;np.where(np.diff(theta)&nbsp;&lt;&nbsp;-180)[0]&nbsp;+&nbsp;1</code> | Assigns the expression on the right to `split` for later use. |
| 30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;[data.iloc[idx]&nbsp;for&nbsp;idx&nbsp;in&nbsp;np.split(np.arange(len(data)),&nbsp;split)&nbsp;if&nbsp;len(idx)]</code> | Returns this computed value to the caller; the function ends here. |
| 31 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 32 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;update_heatmap_datasets(self):</code> | Defines the named function/method; indented lines below form its body. |
| 34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;previous&nbsp;=&nbsp;self.heatmap_dataset_select.currentData()</code> | Assigns the expression on the right to `previous` for later use. |
| 35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_dataset_select.blockSignals(True)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_dataset_select.clear()</code> | Finishes this expression or function-call argument sequence. |
| 37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;key,&nbsp;group&nbsp;in&nbsp;self.groups.items():</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_dataset_select.addItem(group["name"],&nbsp;key)</code> | Adds an option to a selection widget, sometimes with hidden application data. |
| 39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;index&nbsp;=&nbsp;self.heatmap_dataset_select.findData(previous)</code> | Assigns the expression on the right to `index` for later use. |
| 40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;index&nbsp;&gt;=&nbsp;0:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_dataset_select.setCurrentIndex(index)</code> | Changes the current visible/selected item in a Qt control. |
| 42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_dataset_select.blockSignals(False)</code> | Temporarily suppresses Qt signals to prevent unwanted recursive updates. |
| 43 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 44 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;update_plot(self,&nbsp;*_):</code> | Defines the named function/method; indented lines below form its body. |
| 46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Allow&nbsp;native&nbsp;combo&nbsp;popups&nbsp;and&nbsp;button&nbsp;animations&nbsp;to&nbsp;close&nbsp;before&nbsp;rendering."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._plot_timer.start()</code> | Finishes this expression or function-call argument sequence. |
| 48 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 49 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;_paint_selected_plot(self):</code> | Defines the named function/method; indented lines below form its body. |
| 51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kind&nbsp;=&nbsp;self.plot_select.currentText()</code> | Assigns the expression on the right to `kind` for later use. |
| 52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_label.setVisible(kind&nbsp;==&nbsp;"CDF")</code> | Shows or hides the widget. |
| 53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.heatmap_controls.setVisible(kind&nbsp;==&nbsp;"Heatmap")</code> | Shows or hides the widget. |
| 54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;kind&nbsp;==&nbsp;"CDF":</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_cdf()</code> | Finishes this expression or function-call argument sequence. |
| 56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif&nbsp;kind&nbsp;==&nbsp;"Heatmap":</code> | Tests an alternative condition only if previous conditions were false. |
| 57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_heatmap()</code> | Finishes this expression or function-call argument sequence. |
| 58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.plot_overlay(polar=kind&nbsp;==&nbsp;"Polar&nbsp;Plot")</code> | Finishes this expression or function-call argument sequence. |
| 60 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 61 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;plot_heatmap(self):</code> | Defines the named function/method; indented lines below form its body. |
| 63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Single-dataset&nbsp;Phi&nbsp;vs&nbsp;Theta&nbsp;heatmap&nbsp;for&nbsp;one&nbsp;selected&nbsp;frequency.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 64 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;With&nbsp;multiple&nbsp;selected&nbsp;frequencies,&nbsp;choose&nbsp;the&nbsp;first&nbsp;selected&nbsp;frequency</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;present&nbsp;in&nbsp;this&nbsp;dataset.&nbsp;Repeated&nbsp;angular&nbsp;samples&nbsp;are&nbsp;median-aggregated.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;canvas&nbsp;=&nbsp;self.heatmap_canvas</code> | Assigns the expression on the right to `canvas` for later use. |
| 69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stacklayout.setCurrentWidget(self.plot_pages[canvas])</code> | Changes the current visible/selected item in a Qt control. |
| 70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key&nbsp;=&nbsp;self.heatmap_dataset_select.currentData()</code> | Assigns the expression on the right to `key` for later use. |
| 71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;key&nbsp;not&nbsp;in&nbsp;self.groups:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"Load&nbsp;a&nbsp;dataset&nbsp;and&nbsp;select&nbsp;it&nbsp;for&nbsp;the&nbsp;heatmap.")</code> | Finishes this expression or function-call argument sequence. |
| 73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group&nbsp;=&nbsp;self.groups[key]</code> | Assigns the expression on the right to `group` for later use. |
| 75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data&nbsp;=&nbsp;self.filtered_data(group)</code> | Assigns the expression on the right to `data` for later use. |
| 76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;data.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"No&nbsp;data&nbsp;matches&nbsp;the&nbsp;selected&nbsp;frequency&nbsp;and&nbsp;Phi&nbsp;filters.")</code> | Finishes this expression or function-call argument sequence. |
| 78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chosen_p&nbsp;=&nbsp;self.heatmap_p_select.currentText()</code> | Assigns the expression on the right to `chosen_p` for later use. |
| 80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data&nbsp;=&nbsp;data.loc[data["P"]&nbsp;==&nbsp;chosen_p]</code> | Finishes this expression or function-call argument sequence. |
| 81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;data.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;f"No&nbsp;{chosen_p}&nbsp;measurements&nbsp;match&nbsp;selected&nbsp;filters.")</code> | Finishes this expression or function-call argument sequence. |
| 83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;freq&nbsp;=&nbsp;float(np.min(data["Freq"].unique()))</code> | Gets the distinct values in a column, useful for frequency or angle choices. |
| 85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data&nbsp;=&nbsp;data.loc[data["Freq"]&nbsp;==&nbsp;freq]</code> | Finishes this expression or function-call argument sequence. |
| 86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Rows&nbsp;=&nbsp;Phi,&nbsp;columns&nbsp;=&nbsp;Theta;&nbsp;repeated&nbsp;angles&nbsp;use&nbsp;a&nbsp;median.</code> | Developer comment: Rows = Phi, columns = Theta; repeated angles use a median. |
| 87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;grid&nbsp;=&nbsp;data.pivot_table(index="Phi",&nbsp;columns="Theta",&nbsp;values="PdB",&nbsp;aggfunc="median")</code> | Rearranges flat samples into a 2D grid indexed by scan angle. |
| 88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;grid.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"No&nbsp;heatmap&nbsp;samples&nbsp;available.")</code> | Finishes this expression or function-call argument sequence. |
| 90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig&nbsp;=&nbsp;canvas.figure</code> | Assigns the expression on the right to `fig` for later use. |
| 92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig.clear()</code> | Finishes this expression or function-call argument sequence. |
| 93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax&nbsp;=&nbsp;fig.add_subplot(111)</code> | Assigns the expression on the right to `ax` for later use. |
| 94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;theta_vals&nbsp;=&nbsp;grid.columns.to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi_vals&nbsp;=&nbsp;grid.index.to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;power&nbsp;=&nbsp;grid.to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.plot_phi_theta.isChecked():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;horizontal_points,&nbsp;vertical_points&nbsp;=&nbsp;theta_vals,&nbsp;phi_vals</code> | Assigns the expression on the right to `horizontal_points, vertical_points` for later use. |
| 99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Pure&nbsp;angular&nbsp;wrap/flip,&nbsp;NOT&nbsp;a&nbsp;spatial&nbsp;rotation&nbsp;or&nbsp;regridding.</code> | Developer comment: Pure angular wrap/flip, NOT a spatial rotation or regridding. |
| 101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Sort&nbsp;both&nbsp;transformed&nbsp;axes&nbsp;and&nbsp;reorder&nbsp;power&nbsp;accordingly.</code> | Developer comment: Sort both transformed axes and reorder power accordingly. |
| 102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;horizontal_points,&nbsp;vertical_points&nbsp;=&nbsp;scan_to_az_el(theta_vals,&nbsp;phi_vals)</code> | Assigns the expression on the right to `horizontal_points, vertical_points` for later use. |
| 103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;order_x&nbsp;=&nbsp;np.argsort(horizontal_points,&nbsp;kind="stable")</code> | Assigns the expression on the right to `order_x` for later use. |
| 104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;order_y&nbsp;=&nbsp;np.argsort(vertical_points,&nbsp;kind="stable")</code> | Assigns the expression on the right to `order_y` for later use. |
| 105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;horizontal_points&nbsp;=&nbsp;horizontal_points[order_x]</code> | Assigns the expression on the right to `horizontal_points` for later use. |
| 106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vertical_points&nbsp;=&nbsp;vertical_points[order_y]</code> | Assigns the expression on the right to `vertical_points` for later use. |
| 107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;power&nbsp;=&nbsp;power[np.ix_(order_y,&nbsp;order_x)]</code> | Assigns the expression on the right to `power` for later use. |
| 108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mesh&nbsp;=&nbsp;ax.pcolormesh(horizontal_points,&nbsp;vertical_points,</code> | Draws heatmap cells colored by their associated values. |
| 109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;np.ma.masked_invalid(power),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shading="auto",&nbsp;cmap="viridis")</code> | Assigns the expression on the right to `shading` for later use. |
| 111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig.colorbar(mesh,&nbsp;ax=ax,&nbsp;label="Power&nbsp;(dB)")</code> | Finishes this expression or function-call argument sequence. |
| 112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_title(f"{group['name']}&nbsp;\|&nbsp;{freq:g}&nbsp;MHz&nbsp;\|&nbsp;{chosen_p}")</code> | Sets the visible chart axis label or title. |
| 113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;horizontal,&nbsp;vertical&nbsp;=&nbsp;self.plot_coordinate_labels()</code> | Assigns the expression on the right to `horizontal, vertical` for later use. |
| 114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_xlabel(f"{horizontal}&nbsp;(degrees)")</code> | Sets the visible chart axis label or title. |
| 115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_ylabel(f"{vertical}&nbsp;(degrees)")</code> | Sets the visible chart axis label or title. |
| 116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig.tight_layout()</code> | Finishes this expression or function-call argument sequence. |
| 117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;canvas.draw_idle()</code> | Requests a Matplotlib redraw when the GUI becomes idle, instead of drawing immediately. |
| 118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.statusBar().showMessage(f"Heatmap:&nbsp;{group['name']}&nbsp;at&nbsp;{freq:g}&nbsp;MHz")</code> | Finishes this expression or function-call argument sequence. |
| 119 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 120 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;plot_overlay(self,&nbsp;polar=False):</code> | Defines the named function/method; indented lines below form its body. |
| 122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;canvas&nbsp;=&nbsp;self.polar_canvas&nbsp;if&nbsp;polar&nbsp;else&nbsp;self.linear_canvas</code> | Assigns the expression on the right to `canvas` for later use. |
| 123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stacklayout.setCurrentWidget(self.plot_pages[canvas])</code> | Changes the current visible/selected item in a Qt control. |
| 124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;active&nbsp;=&nbsp;[x&nbsp;for&nbsp;x&nbsp;in&nbsp;self.groups.values()&nbsp;if&nbsp;x["visible"]]</code> | Assigns the expression on the right to `active` for later use. |
| 125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;active:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"Load&nbsp;datasets&nbsp;or&nbsp;enable&nbsp;dataset&nbsp;visibility.")</code> | Finishes this expression or function-call argument sequence. |
| 127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;freqs,&nbsp;phis&nbsp;=&nbsp;self.selected_filters()</code> | Assigns the expression on the right to `freqs, phis` for later use. |
| 129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;freqs&nbsp;or&nbsp;not&nbsp;phis:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"Select&nbsp;at&nbsp;least&nbsp;one&nbsp;frequency&nbsp;and&nbsp;phi.")</code> | Finishes this expression or function-call argument sequence. |
| 131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig&nbsp;=&nbsp;canvas.figure</code> | Assigns the expression on the right to `fig` for later use. |
| 133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig.clear()</code> | Finishes this expression or function-call argument sequence. |
| 134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax&nbsp;=&nbsp;fig.add_subplot(111,&nbsp;projection="polar"&nbsp;if&nbsp;polar&nbsp;else&nbsp;None)</code> | Assigns the expression on the right to `ax` for later use. |
| 135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;horizontal,&nbsp;vertical&nbsp;=&nbsp;self.plot_coordinate_labels()</code> | Assigns the expression on the right to `horizontal, vertical` for later use. |
| 136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;combos&nbsp;=&nbsp;[(f,&nbsp;p)&nbsp;for&nbsp;f&nbsp;in&nbsp;freqs&nbsp;for&nbsp;p&nbsp;in&nbsp;phis]</code> | Assigns the expression on the right to `combos` for later use. |
| 137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;styles&nbsp;=&nbsp;{fp:&nbsp;self.line_styles[i&nbsp;%&nbsp;len(self.line_styles)]&nbsp;for&nbsp;i,&nbsp;fp&nbsp;in&nbsp;enumerate(combos)}</code> | Assigns the expression on the right to `styles` for later use. |
| 138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curves&nbsp;=&nbsp;0</code> | Assigns the expression on the right to `curves` for later use. |
| 139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;group&nbsp;in&nbsp;active:</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;filtered&nbsp;=&nbsp;self.filtered_data(group)</code> | Assigns the expression on the right to `filtered` for later use. |
| 141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;filtered.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | Skips the rest of this loop iteration and proceeds to the next item. |
| 143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;(freq,&nbsp;pol,&nbsp;phi),&nbsp;subset&nbsp;in&nbsp;filtered.groupby(["Freq",&nbsp;"P",&nbsp;"Phi"],&nbsp;sort=False):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;sweep_index,&nbsp;sweep&nbsp;in&nbsp;enumerate(self.split_theta_sweeps(subset)):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;theta&nbsp;=&nbsp;sweep["Theta"].to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value&nbsp;=&nbsp;sweep["PdB"].to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.plot_phi_theta.isChecked():</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x_values&nbsp;=&nbsp;theta</code> | Assigns the expression on the right to `x_values` for later use. |
| 149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x_values,&nbsp;_&nbsp;=&nbsp;scan_to_az_el(theta,&nbsp;np.full_like(theta,&nbsp;phi))</code> | Assigns the expression on the right to `x_values, _` for later use. |
| 151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;The&nbsp;angular&nbsp;flip&nbsp;reverses&nbsp;sweep&nbsp;order;&nbsp;sort&nbsp;each&nbsp;portion</code> | Developer comment: The angular flip reverses sweep order; sort each portion |
| 152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;before&nbsp;plotting&nbsp;and&nbsp;avoid&nbsp;crossing&nbsp;the&nbsp;0/360&nbsp;seam.</code> | Developer comment: before plotting and avoid crossing the 0/360 seam. |
| 153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x_values&nbsp;=&nbsp;np.asarray(x_values,&nbsp;dtype=float).copy()</code> | Creates a separate copy so later modifications do not unexpectedly change the original data. |
| 154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;jumps&nbsp;=&nbsp;np.flatnonzero(np.abs(np.diff(x_values))&nbsp;&gt;&nbsp;180)&nbsp;+&nbsp;1</code> | Assigns the expression on the right to `jumps` for later use. |
| 155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;segment&nbsp;in&nbsp;np.split(np.arange(len(x_values)),&nbsp;jumps):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;len(segment):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | Skips the rest of this loop iteration and proceeds to the next item. |
| 158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;segment&nbsp;=&nbsp;segment[np.argsort(x_values[segment])]</code> | Assigns the expression on the right to `segment` for later use. |
| 159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.plot(np.deg2rad(x_values[segment])&nbsp;if&nbsp;polar&nbsp;else&nbsp;x_values[segment],</code> | Plots a curve or points on the Matplotlib axes using the provided data and styling. |
| 160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value[segment],</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color=group["color"],&nbsp;linestyle=styles.get((freq,&nbsp;phi),&nbsp;"-"),</code> | Assigns the expression on the right to `color` for later use. |
| 162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;linewidth=1.5,&nbsp;alpha=.85,</code> | Assigns the expression on the right to `linewidth` for later use. |
| 163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;label=(f"{group['name']}&nbsp;\|&nbsp;{freq:g}&nbsp;MHz,&nbsp;{pol},&nbsp;Phi&nbsp;cut={phi:g}°"</code> | Assigns the expression on the right to `label` for later use. |
| 164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;sweep_index&nbsp;==&nbsp;0&nbsp;and&nbsp;segment[0]&nbsp;==&nbsp;0&nbsp;else&nbsp;"_nolegend_"))</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curves&nbsp;+=&nbsp;1</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;curves:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"No&nbsp;data&nbsp;matches&nbsp;selected&nbsp;filters.")</code> | Finishes this expression or function-call argument sequence. |
| 168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;polar:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_title(f"Polar&nbsp;Radiation&nbsp;Pattern&nbsp;({horizontal}/{vertical})",&nbsp;pad=20)</code> | Sets the visible chart axis label or title. |
| 171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_theta_zero_location("N")</code> | Finishes this expression or function-call argument sequence. |
| 172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_theta_direction(-1)</code> | Finishes this expression or function-call argument sequence. |
| 173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_rlim(-80,&nbsp;0)</code> | Finishes this expression or function-call argument sequence. |
| 174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_rlabel_position(225)</code> | Finishes this expression or function-call argument sequence. |
| 175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | Runs the alternative block when the preceding condition does not match. |
| 176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_title(f"Linear&nbsp;Radiation&nbsp;Pattern&nbsp;({horizontal}/{vertical})")</code> | Sets the visible chart axis label or title. |
| 177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_xlabel(f"{horizontal}&nbsp;(degrees)")</code> | Sets the visible chart axis label or title. |
| 178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_ylabel("Power&nbsp;(dB)")</code> | Sets the visible chart axis label or title. |
| 179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_xlim((-180,&nbsp;180)&nbsp;if&nbsp;self.plot_phi_theta.isChecked()&nbsp;else&nbsp;(0,&nbsp;360))</code> | Controls the visible chart axis boundaries. |
| 180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_ylim(-80,&nbsp;0)</code> | Controls the visible chart axis boundaries. |
| 181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.grid(True,&nbsp;alpha=.35)</code> | Finishes this expression or function-call argument sequence. |
| 182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.legend(loc="upper&nbsp;left",&nbsp;bbox_to_anchor=(1.02,&nbsp;1),&nbsp;fontsize="small")</code> | Shows the legend describing plotted curves and colors. |
| 183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig.tight_layout()</code> | Finishes this expression or function-call argument sequence. |
| 184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;canvas.draw_idle()</code> | Requests a Matplotlib redraw when the GUI becomes idle, instead of drawing immediately. |
| 185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.statusBar().showMessage(f"Displaying&nbsp;{curves}&nbsp;angular&nbsp;sweeps&nbsp;from&nbsp;{len(active)}&nbsp;datasets")</code> | Finishes this expression or function-call argument sequence. |
| 186 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 187 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;plot_cdf(self):</code> | Defines the named function/method; indented lines below form its body. |
| 189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""CDF&nbsp;of&nbsp;\|test-synthetic\|;&nbsp;overlay&nbsp;per-curve&nbsp;P75&nbsp;quantile&nbsp;envelope."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;canvas&nbsp;=&nbsp;self.cdf_canvas</code> | Assigns the expression on the right to `canvas` for later use. |
| 191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stacklayout.setCurrentWidget(self.plot_pages[canvas])</code> | Changes the current visible/selected item in a Qt control. |
| 192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_plot_data&nbsp;=&nbsp;pd.DataFrame()</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_summary&nbsp;=&nbsp;pd.DataFrame()</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_p75&nbsp;=&nbsp;None</code> | Stores or updates `self.cdf_overall_p75` on the current object so other methods can use it. |
| 195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_label.setText("Overall&nbsp;\|ΔdB\|&nbsp;P75:&nbsp;—")</code> | Updates text shown in an existing widget. |
| 196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_label.show()</code> | Displays the window/widget or requests its display. |
| 197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test,&nbsp;synthetic&nbsp;=&nbsp;self.selected_pair()</code> | Assigns the expression on the right to `test, synthetic` for later use. |
| 198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;test&nbsp;is&nbsp;None&nbsp;or&nbsp;synthetic&nbsp;is&nbsp;None:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"Assign&nbsp;one&nbsp;dataset&nbsp;as&nbsp;Test&nbsp;and&nbsp;another&nbsp;as&nbsp;Synthetic&nbsp;for&nbsp;CDF.")</code> | Finishes this expression or function-call argument sequence. |
| 200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left,&nbsp;right&nbsp;=&nbsp;self.filtered_data(test),&nbsp;self.filtered_data(synthetic)</code> | Assigns the expression on the right to `left, right` for later use. |
| 202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;left.empty&nbsp;or&nbsp;right.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"No&nbsp;selected&nbsp;frequency/phi&nbsp;samples&nbsp;for&nbsp;the&nbsp;CDF&nbsp;pair.")</code> | Finishes this expression or function-call argument sequence. |
| 204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keys&nbsp;=&nbsp;["Freq",&nbsp;"P",&nbsp;"Phi",&nbsp;"Theta"]</code> | Assigns the expression on the right to `keys` for later use. |
| 206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;left&nbsp;=&nbsp;left.groupby(keys,&nbsp;as_index=False)["PdB"].median().rename(columns={"PdB":&nbsp;"test_db"})</code> | Groups DataFrame rows by matching column values for independent processing. |
| 207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right&nbsp;=&nbsp;right.groupby(keys,&nbsp;as_index=False)["PdB"].median().rename(columns={"PdB":&nbsp;"synthetic_db"})</code> | Groups DataFrame rows by matching column values for independent processing. |
| 208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;paired&nbsp;=&nbsp;left.merge(right,&nbsp;on=keys,&nbsp;how="inner")</code> | Assigns the expression on the right to `paired` for later use. |
| 209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;paired.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"No&nbsp;matching&nbsp;frequency&nbsp;/&nbsp;phi&nbsp;/&nbsp;theta&nbsp;samples.")</code> | Finishes this expression or function-call argument sequence. |
| 211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;paired["signed_delta_db"]&nbsp;=&nbsp;paired["test_db"]&nbsp;-&nbsp;paired["synthetic_db"]</code> | Assigns the expression on the right to `paired["signed_delta_db"]` for later use. |
| 213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;paired["delta_db"]&nbsp;=&nbsp;paired["signed_delta_db"].abs()</code> | Assigns the expression on the right to `paired["delta_db"]` for later use. |
| 214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_paired&nbsp;=&nbsp;paired</code> | Stores or updates `self.cdf_paired` on the current object so other methods can use it. |
| 215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;all_deltas&nbsp;=&nbsp;paired["delta_db"].to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;overall_p75&nbsp;=&nbsp;float(np.percentile(all_deltas,&nbsp;75))</code> | Calculates a percentile of the supplied numerical data. |
| 217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x_max&nbsp;=&nbsp;max(3.5,&nbsp;float(np.max(all_deltas))&nbsp;*&nbsp;1.05)</code> | Assigns the expression on the right to `x_max` for later use. |
| 218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig&nbsp;=&nbsp;canvas.figure</code> | Assigns the expression on the right to `fig` for later use. |
| 219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig.clear()</code> | Finishes this expression or function-call argument sequence. |
| 220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax&nbsp;=&nbsp;fig.add_subplot(111)</code> | Assigns the expression on the right to `ax` for later use. |
| 221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Rebuild&nbsp;the&nbsp;background&nbsp;on&nbsp;x-limit&nbsp;changes&nbsp;so&nbsp;the&nbsp;green/yellow/red</code> | Developer comment: Rebuild the background on x-limit changes so the green/yellow/red |
| 222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;bands&nbsp;still&nbsp;cover&nbsp;the&nbsp;whole&nbsp;chart&nbsp;after&nbsp;toolbar&nbsp;zoom&nbsp;or&nbsp;x-axis&nbsp;edits.</code> | Developer comment: bands still cover the whole chart after toolbar zoom or x-axis edits. |
| 223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regions&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `regions` for later use. |
| 224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;threshold_line&nbsp;=&nbsp;ax.axvline(3,&nbsp;color="black",&nbsp;linestyle=":",&nbsp;linewidth=1.3,&nbsp;zorder=3)</code> | Assigns the expression on the right to `threshold_line` for later use. |
| 225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;probability_line&nbsp;=&nbsp;ax.plot([3,&nbsp;x_max],&nbsp;[.75,&nbsp;.75],&nbsp;color="black",</code> | Plots a curve or points on the Matplotlib axes using the provided data and styling. |
| 226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;linestyle=":",&nbsp;linewidth=1.3,&nbsp;zorder=3)[0]</code> | Assigns the expression on the right to `linestyle` for later use. |
| 227 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;refresh_regions(axis):</code> | Defines the named function/method; indented lines below form its body. |
| 229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;right&nbsp;=&nbsp;axis.get_xlim()[1]</code> | Assigns the expression on the right to `right` for later use. |
| 230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;patch&nbsp;in&nbsp;regions:</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;patch.remove()</code> | Finishes this expression or function-call argument sequence. |
| 232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regions.clear()</code> | Finishes this expression or function-call argument sequence. |
| 233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regions.append(axis.axvspan(0,&nbsp;3,&nbsp;0,&nbsp;1,</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;facecolor="#ccead1",&nbsp;alpha=.78,&nbsp;zorder=0))</code> | Assigns the expression on the right to `facecolor` for later use. |
| 235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;right&nbsp;&gt;&nbsp;3:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regions.append(axis.axvspan(3,&nbsp;right,&nbsp;0,&nbsp;.75,</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;facecolor="#fff0af",&nbsp;alpha=.82,&nbsp;zorder=0))</code> | Assigns the expression on the right to `facecolor` for later use. |
| 238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regions.append(axis.axvspan(3,&nbsp;right,&nbsp;.75,&nbsp;1,</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;facecolor="#f5c5c5",&nbsp;alpha=.82,&nbsp;zorder=0))</code> | Assigns the expression on the right to `facecolor` for later use. |
| 240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;probability_line.set_xdata([3,&nbsp;max(right,&nbsp;3)])</code> | Finishes this expression or function-call argument sequence. |
| 241 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.callbacks.connect("xlim_changed",&nbsp;refresh_regions)</code> | Connects the `ax.callbacks` Qt signal to the callback inside `.connect(...)`. |
| 243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_,&nbsp;vertical&nbsp;=&nbsp;self.plot_coordinate_labels()</code> | Assigns the expression on the right to `_, vertical` for later use. |
| 244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;summary,&nbsp;export_curves,&nbsp;per_curve_arrays&nbsp;=&nbsp;[],&nbsp;[],&nbsp;[]</code> | Assigns the expression on the right to `summary, export_curves, per_curve_arrays` for later use. |
| 245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;A&nbsp;shared&nbsp;probability&nbsp;grid&nbsp;lets&nbsp;the&nbsp;P75&nbsp;curve&nbsp;follow&nbsp;the&nbsp;other&nbsp;CDFs.</code> | Developer comment: A shared probability grid lets the P75 curve follow the other CDFs. |
| 246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;probability_grid&nbsp;=&nbsp;np.linspace(0,&nbsp;1,&nbsp;501)</code> | Assigns the expression on the right to `probability_grid` for later use. |
| 247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;(freq,&nbsp;pol,&nbsp;phi),&nbsp;subset&nbsp;in&nbsp;paired.groupby(["Freq",&nbsp;"P",&nbsp;"Phi"],&nbsp;sort=True):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x,&nbsp;y,&nbsp;(p25,&nbsp;p50,&nbsp;p75)&nbsp;=&nbsp;cdf_statistics(subset["delta_db"])</code> | Finishes this expression or function-call argument sequence. |
| 249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;len(x)&nbsp;==&nbsp;0:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | Skips the rest of this loop iteration and proceeds to the next item. |
| 251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;label&nbsp;=&nbsp;f"{test['name']}&nbsp;vs&nbsp;{synthetic['name']}&nbsp;\|&nbsp;{freq:g}&nbsp;MHz,&nbsp;{pol},&nbsp;{vertical}={phi:g}°"</code> | Assigns the expression on the right to `label` for later use. |
| 252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;line,&nbsp;=&nbsp;ax.step(x,&nbsp;y,&nbsp;where="post",&nbsp;linewidth=1.6,&nbsp;zorder=4,&nbsp;label=label)</code> | Plots stepped CDF values on the Matplotlib axes. |
| 253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;prob,&nbsp;value,&nbsp;marker&nbsp;in&nbsp;((.25,&nbsp;p25,&nbsp;"o"),&nbsp;(.5,&nbsp;p50,&nbsp;"s"),&nbsp;(.75,&nbsp;p75,&nbsp;"^")):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.plot(value,&nbsp;prob,&nbsp;marker=marker,&nbsp;color=line.get_color(),&nbsp;markersize=4,</code> | Plots a curve or points on the Matplotlib axes using the provided data and styling. |
| 255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;linestyle="None",&nbsp;zorder=5)</code> | Assigns the expression on the right to `linestyle` for later use. |
| 256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;summary.append({"Freq":&nbsp;freq,&nbsp;"P":&nbsp;pol,&nbsp;"Phi":&nbsp;phi,&nbsp;"Count":&nbsp;len(subset),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"P25":&nbsp;p25,&nbsp;"P50":&nbsp;p50,&nbsp;"P75":&nbsp;p75})</code> | Finishes this expression or function-call argument sequence. |
| 258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;export_curves.append(pd.DataFrame({"Curve":&nbsp;label,&nbsp;"P":&nbsp;pol,&nbsp;"Freq_MHz":&nbsp;freq,</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Phi_deg":&nbsp;phi,&nbsp;"Abs_Delta_dB":&nbsp;x,</code> | Provides a string label, key, path, or parameter in the surrounding call/collection. |
| 260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Cumulative_Probability":&nbsp;y,</code> | Provides a string label, key, path, or parameter in the surrounding call/collection. |
| 261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Curve_P75_dB":&nbsp;p75}))</code> | Finishes this expression or function-call argument sequence. |
| 262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;per_curve_arrays.append(np.quantile(subset["delta_db"].to_numpy(dtype=float),</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 263 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;probability_grid))</code> | Finishes this expression or function-call argument sequence. |
| 264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;per_curve_arrays:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.draw_message(canvas,&nbsp;"No&nbsp;CDF&nbsp;curves&nbsp;could&nbsp;be&nbsp;generated.")</code> | Finishes this expression or function-call argument sequence. |
| 266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;At&nbsp;each&nbsp;probability,&nbsp;calculate&nbsp;the&nbsp;75th&nbsp;percentile&nbsp;of&nbsp;the&nbsp;individual</code> | Developer comment: At each probability, calculate the 75th percentile of the individual |
| 268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;curve&nbsp;quantiles.&nbsp;This&nbsp;is&nbsp;a&nbsp;CDF-shaped&nbsp;aggregate,&nbsp;not&nbsp;a&nbsp;fixed-x&nbsp;line.</code> | Developer comment: curve quantiles. This is a CDF-shaped aggregate, not a fixed-x line. |
| 269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;p75_trace&nbsp;=&nbsp;np.percentile(np.vstack(per_curve_arrays),&nbsp;75,&nbsp;axis=0)</code> | Calculates a percentile of the supplied numerical data. |
| 270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.plot(p75_trace,&nbsp;probability_grid,&nbsp;color="black",&nbsp;linewidth=2.7,</code> | Plots a curve or points on the Matplotlib axes using the provided data and styling. |
| 271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zorder=12,&nbsp;label="P75&nbsp;across&nbsp;plotted&nbsp;CDF&nbsp;curves")</code> | Assigns the expression on the right to `zorder` for later use. |
| 272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;export_curves.append(pd.DataFrame({</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Curve":&nbsp;"P75&nbsp;across&nbsp;plotted&nbsp;CDF&nbsp;curves",&nbsp;"P":&nbsp;"All",&nbsp;"Freq_MHz":&nbsp;np.nan,</code> | Provides a string label, key, path, or parameter in the surrounding call/collection. |
| 274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Phi_deg":&nbsp;np.nan,&nbsp;"Abs_Delta_dB":&nbsp;p75_trace,</code> | Provides a string label, key, path, or parameter in the surrounding call/collection. |
| 275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Cumulative_Probability":&nbsp;probability_grid,</code> | Provides a string label, key, path, or parameter in the surrounding call/collection. |
| 276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Curve_P75_dB":&nbsp;np.nan}))</code> | Finishes this expression or function-call argument sequence. |
| 277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_title(f"Absolute&nbsp;Power&nbsp;Difference&nbsp;CDF:&nbsp;{test['name']}&nbsp;vs&nbsp;{synthetic['name']}")</code> | Sets the visible chart axis label or title. |
| 278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_xlabel("Absolute&nbsp;power&nbsp;difference&nbsp;\|Test&nbsp;−&nbsp;Synthetic\|&nbsp;(dB)")</code> | Sets the visible chart axis label or title. |
| 279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_ylabel("Cumulative&nbsp;Probability")</code> | Sets the visible chart axis label or title. |
| 280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_xlim(0,&nbsp;x_max)</code> | Controls the visible chart axis boundaries. |
| 281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.set_ylim(0,&nbsp;1)</code> | Controls the visible chart axis boundaries. |
| 282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.grid(True,&nbsp;alpha=.18,&nbsp;zorder=1)</code> | Finishes this expression or function-call argument sequence. |
| 283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ax.legend(loc="upper&nbsp;left",&nbsp;bbox_to_anchor=(1.02,&nbsp;1),&nbsp;fontsize="small")</code> | Shows the legend describing plotted curves and colors. |
| 284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fig.tight_layout()</code> | Finishes this expression or function-call argument sequence. |
| 285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;canvas.draw_idle()</code> | Requests a Matplotlib redraw when the GUI becomes idle, instead of drawing immediately. |
| 286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_summary&nbsp;=&nbsp;pd.DataFrame(summary)</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_plot_data&nbsp;=&nbsp;pd.concat(export_curves,&nbsp;ignore_index=True)</code> | Combines multiple DataFrames into a single table. |
| 288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_p75&nbsp;=&nbsp;overall_p75</code> | Stores or updates `self.cdf_overall_p75` on the current object so other methods can use it. |
| 289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_overall_label.setText(f"Overall&nbsp;\|ΔdB\|&nbsp;P75:&nbsp;{overall_p75:.3f}&nbsp;dB")</code> | Updates text shown in an existing widget. |
| 290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.statusBar().showMessage(</code> | Opens or closes a multi-line expression or collection. |
| 291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f"CDF:&nbsp;{len(paired):,}&nbsp;matches,&nbsp;{len(summary)}&nbsp;curves,&nbsp;overall&nbsp;\|ΔdB\|&nbsp;P75&nbsp;=&nbsp;{overall_p75:.2f}&nbsp;dB")</code> | Finishes this expression or function-call argument sequence. |
| 292 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |


## `src/Lolth/plotting/coordinates.py`

Conversion of displayed scan angles between the requested conventions.

**Code landmarks:** `wrap_to_360` (line 11, function), `scan_to_az_el` (line 17, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>"""Reversible&nbsp;angular&nbsp;display&nbsp;remapping;&nbsp;never&nbsp;changes&nbsp;the&nbsp;imported&nbsp;RF&nbsp;arrays.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 2 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 3 | <code>The&nbsp;requested&nbsp;Az/El&nbsp;display&nbsp;convention&nbsp;uses&nbsp;an&nbsp;angle&nbsp;reversal&nbsp;about&nbsp;180&nbsp;degrees.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 4 | <code>The&nbsp;horizontal&nbsp;axis&nbsp;is&nbsp;wrapped&nbsp;to&nbsp;0..360&nbsp;degrees,&nbsp;equivalent&nbsp;to&nbsp;MATLAB&nbsp;wrapTo360.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 5 | <code>The&nbsp;vertical&nbsp;scan&nbsp;is&nbsp;reversed&nbsp;about&nbsp;180&nbsp;as&nbsp;well,&nbsp;rather&nbsp;than&nbsp;performing&nbsp;a</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 6 | <code>Cartesian&nbsp;rotation.&nbsp;Its&nbsp;resulting&nbsp;display&nbsp;range&nbsp;is&nbsp;90..270&nbsp;for&nbsp;-90..90&nbsp;input.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 7 | <code>"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 8 | <code>import&nbsp;numpy&nbsp;as&nbsp;np</code> | Loads the named Python package/module for use in this file. |
| 9 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 10 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 11 | <code>def&nbsp;wrap_to_360(degrees):</code> | Defines the named function/method; indented lines below form its body. |
| 12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;values&nbsp;=&nbsp;np.mod(np.asarray(degrees,&nbsp;dtype=float),&nbsp;360.0)</code> | Converts input data to a NumPy array. |
| 13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Keep&nbsp;zero&nbsp;at&nbsp;zero&nbsp;including&nbsp;source&nbsp;angles&nbsp;representing&nbsp;full&nbsp;revolutions.</code> | Developer comment: Keep zero at zero including source angles representing full revolutions. |
| 14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;values</code> | Returns this computed value to the caller; the function ends here. |
| 15 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 16 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 17 | <code>def&nbsp;scan_to_az_el(theta_deg,&nbsp;phi_deg):</code> | Defines the named function/method; indented lines below form its body. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Return&nbsp;flipped/wrapped&nbsp;display&nbsp;azimuth&nbsp;and&nbsp;vertical-angle&nbsp;coordinates.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 19 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;Theta/A1:&nbsp;-180..180&nbsp;-&gt;&nbsp;display&nbsp;Az&nbsp;=&nbsp;wrap360(180&nbsp;-&nbsp;Theta)</code> | Finishes this expression or function-call argument sequence. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;Phi/E1:&nbsp;&nbsp;&nbsp;-90..90&nbsp;-&gt;&nbsp;display&nbsp;El&nbsp;=&nbsp;wrap360(180&nbsp;-&nbsp;Phi)</code> | Finishes this expression or function-call argument sequence. |
| 22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;(wrap_to_360(180.0&nbsp;-&nbsp;np.asarray(theta_deg,&nbsp;dtype=float)),</code> | Returns this computed value to the caller; the function ends here. |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;wrap_to_360(180.0&nbsp;-&nbsp;np.asarray(phi_deg,&nbsp;dtype=float)))</code> | Converts input data to a NumPy array. |


## `src/Lolth/plotting/export.py`

Export plotted CDF curves and summary statistics to one Excel workbook.

**Code landmarks:** `_excel_column` (line 15, function), `_cell_xml` (line 24, function), `_write_sheet` (line 42, function), `write` (line 47, function), `write_cdf_workbook` (line 63, function), `CDFExportMixin` (line 95, class), `export_cdf_data` (line 96, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>"""Export&nbsp;all&nbsp;CDF&nbsp;data&nbsp;to&nbsp;one&nbsp;Excel&nbsp;workbook&nbsp;using&nbsp;only&nbsp;Python's&nbsp;standard&nbsp;library.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 2 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 3 | <code>No&nbsp;artifact_tool,&nbsp;openpyxl,&nbsp;or&nbsp;xlsxwriter&nbsp;installation&nbsp;is&nbsp;required.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 4 | <code>"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 5 | <code>from&nbsp;datetime&nbsp;import&nbsp;date,&nbsp;datetime</code> | Imports specific classes or functions from the named module so this file can use them. |
| 6 | <code>from&nbsp;html&nbsp;import&nbsp;escape</code> | Imports specific classes or functions from the named module so this file can use them. |
| 7 | <code>from&nbsp;math&nbsp;import&nbsp;isfinite</code> | Imports specific classes or functions from the named module so this file can use them. |
| 8 | <code>from&nbsp;pathlib&nbsp;import&nbsp;Path</code> | Imports specific classes or functions from the named module so this file can use them. |
| 9 | <code>from&nbsp;zipfile&nbsp;import&nbsp;ZipFile,&nbsp;ZIP_DEFLATED</code> | Imports specific classes or functions from the named module so this file can use them. |
| 10 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 11 | <code>import&nbsp;pandas&nbsp;as&nbsp;pd</code> | Loads the named Python package/module for use in this file. |
| 12 | <code>from&nbsp;PyQt6.QtWidgets&nbsp;import&nbsp;QFileDialog,&nbsp;QMessageBox</code> | Imports specific classes or functions from the named module so this file can use them. |
| 13 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 14 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 15 | <code>def&nbsp;_excel_column(index):</code> | Defines the named function/method; indented lines below form its body. |
| 16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""1-based&nbsp;column&nbsp;index&nbsp;to&nbsp;A,&nbsp;B,&nbsp;...,&nbsp;AA."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;letters&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `letters` for later use. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;while&nbsp;index:</code> | Repeats the indented block while the condition remains true. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;index,&nbsp;rem&nbsp;=&nbsp;divmod(index&nbsp;-&nbsp;1,&nbsp;26)</code> | Assigns the expression on the right to `index, rem` for later use. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;letters.append(chr(65&nbsp;+&nbsp;rem))</code> | Finishes this expression or function-call argument sequence. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;"".join(reversed(letters))</code> | Returns this computed value to the caller; the function ends here. |
| 22 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 23 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 24 | <code>def&nbsp;_cell_xml(value,&nbsp;address):</code> | Defines the named function/method; indented lines below form its body. |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Make&nbsp;a&nbsp;numeric&nbsp;or&nbsp;inline-string&nbsp;XLSX&nbsp;cell,&nbsp;skipping&nbsp;NaN&nbsp;and&nbsp;missing&nbsp;data."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;value&nbsp;is&nbsp;None&nbsp;or&nbsp;pd.isna(value):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;""</code> | Returns this computed value to the caller; the function ends here. |
| 28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;isinstance(value,&nbsp;(int,&nbsp;float))&nbsp;and&nbsp;not&nbsp;isinstance(value,&nbsp;bool):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;number&nbsp;=&nbsp;float(value)</code> | Assigns the expression on the right to `number` for later use. |
| 30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;isfinite(number):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;f'&lt;c&nbsp;r="{address}"&gt;&lt;v&gt;{repr(number)}&lt;/v&gt;&lt;/c&gt;'</code> | Returns this computed value to the caller; the function ends here. |
| 32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;""</code> | Returns this computed value to the caller; the function ends here. |
| 33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;isinstance(value,&nbsp;bool):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;f'&lt;c&nbsp;r="{address}"&nbsp;t="b"&gt;&lt;v&gt;{int(value)}&lt;/v&gt;&lt;/c&gt;'</code> | Returns this computed value to the caller; the function ends here. |
| 35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;isinstance(value,&nbsp;(date,&nbsp;datetime)):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value&nbsp;=&nbsp;value.isoformat(sep="&nbsp;")&nbsp;if&nbsp;isinstance(value,&nbsp;datetime)&nbsp;else&nbsp;value.isoformat()</code> | Assigns the expression on the right to `value` for later use. |
| 37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Remove&nbsp;XML-invalid&nbsp;control&nbsp;characters&nbsp;and&nbsp;escape&nbsp;special&nbsp;XML&nbsp;characters.</code> | Developer comment: Remove XML-invalid control characters and escape special XML characters. |
| 38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;s&nbsp;=&nbsp;"".join(c&nbsp;for&nbsp;c&nbsp;in&nbsp;str(value)&nbsp;if&nbsp;ord(c)&nbsp;&gt;=&nbsp;32&nbsp;or&nbsp;c&nbsp;in&nbsp;"\\t\\n\\r")</code> | Finishes this expression or function-call argument sequence. |
| 39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;f'&lt;c&nbsp;r="{address}"&nbsp;t="inlineStr"&gt;&lt;is&gt;&lt;t&nbsp;xml:space="preserve"&gt;{escape(s,&nbsp;quote=False)}&lt;/t&gt;&lt;/is&gt;&lt;/c&gt;'</code> | Returns this computed value to the caller; the function ends here. |
| 40 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 41 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 42 | <code>def&nbsp;_write_sheet(zf,&nbsp;number,&nbsp;frame):</code> | Defines the named function/method; indented lines below form its body. |
| 43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Stream&nbsp;a&nbsp;DataFrame&nbsp;into&nbsp;a&nbsp;worksheet&nbsp;without&nbsp;storing&nbsp;all&nbsp;rows&nbsp;as&nbsp;XML."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;frame.shape[0]&nbsp;+&nbsp;1&nbsp;&gt;&nbsp;1_048_576&nbsp;or&nbsp;frame.shape[1]&nbsp;&gt;&nbsp;16_384:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError("The&nbsp;CDF&nbsp;export&nbsp;exceeds&nbsp;Excel's&nbsp;worksheet&nbsp;row/column&nbsp;limit.")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;with&nbsp;zf.open(f"xl/worksheets/sheet{number}.xml",&nbsp;"w")&nbsp;as&nbsp;stream:</code> | Opens a managed resource (often a file); Python cleans it up when the block ends. |
| 47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;write(s):</code> | Defines the named function/method; indented lines below form its body. |
| 48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;stream.write(s.encode("utf-8"))</code> | Finishes this expression or function-call argument sequence. |
| 49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write('&lt;?xml&nbsp;version="1.0"&nbsp;encoding="UTF-8"&nbsp;standalone="yes"?&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write('&lt;worksheet&nbsp;xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"&gt;&lt;sheetData&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write('&lt;row&nbsp;r="1"&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;col,&nbsp;name&nbsp;in&nbsp;enumerate(frame.columns,&nbsp;1):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write(_cell_xml(str(name),&nbsp;f"{_excel_column(col)}1"))</code> | Finishes this expression or function-call argument sequence. |
| 54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write('&lt;/row&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;row_idx,&nbsp;values&nbsp;in&nbsp;enumerate(frame.itertuples(index=False,&nbsp;name=None),&nbsp;2):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write(f'&lt;row&nbsp;r="{row_idx}"&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;col,&nbsp;value&nbsp;in&nbsp;enumerate(values,&nbsp;1):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write(_cell_xml(value,&nbsp;f"{_excel_column(col)}{row_idx}"))</code> | Finishes this expression or function-call argument sequence. |
| 59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write('&lt;/row&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write('&lt;/sheetData&gt;&lt;/worksheet&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 61 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 62 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 63 | <code>def&nbsp;write_cdf_workbook(path,&nbsp;curves,&nbsp;summary,&nbsp;overall):</code> | Defines the named function/method; indented lines below form its body. |
| 64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Write&nbsp;three&nbsp;independent&nbsp;sheets&nbsp;in&nbsp;a&nbsp;single&nbsp;valid&nbsp;.xlsx&nbsp;file."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;sheets&nbsp;=&nbsp;[</code> | Assigns the expression on the right to `sheets` for later use. |
| 66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;("CDF&nbsp;Curves",&nbsp;curves),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;("Curve&nbsp;Statistics",&nbsp;summary),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;("Overall&nbsp;Statistics",&nbsp;overall),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;]</code> | Opens or closes a multi-line expression or collection. |
| 70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;main_ns&nbsp;=&nbsp;"http://schemas.openxmlformats.org/spreadsheetml/2006/main"</code> | Assigns the expression on the right to `main_ns` for later use. |
| 71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;relationships_ns&nbsp;=&nbsp;"http://schemas.openxmlformats.org/officeDocument/2006/relationships"</code> | Assigns the expression on the right to `relationships_ns` for later use. |
| 72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;with&nbsp;ZipFile(path,&nbsp;"w",&nbsp;compression=ZIP_DEFLATED,&nbsp;compresslevel=6)&nbsp;as&nbsp;zf:</code> | Opens a managed resource (often a file); Python cleans it up when the block ends. |
| 73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zf.writestr("[Content_Types].xml",&nbsp;'''&lt;?xml&nbsp;version="1.0"&nbsp;encoding="UTF-8"&nbsp;standalone="yes"?&gt;</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 74 | <code>&lt;Types&nbsp;xmlns="http://schemas.openxmlformats.org/package/2006/content-types"&gt;</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 75 | <code>&lt;Default&nbsp;Extension="rels"&nbsp;ContentType="application/vnd.openxmlformats-package.relationships+xml"/&gt;</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 76 | <code>&lt;Default&nbsp;Extension="xml"&nbsp;ContentType="application/xml"/&gt;</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 77 | <code>&lt;Override&nbsp;PartName="/xl/workbook.xml"&nbsp;ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/&gt;</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 78 | <code>'''&nbsp;+&nbsp;"".join(f'&lt;Override&nbsp;PartName="/xl/worksheets/sheet{i}.xml"&nbsp;ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/&gt;'&nbsp;for&nbsp;i&nbsp;in&nbsp;range(1,&nbsp;4))&nbsp;+&nbsp;"&lt;/Types&gt;")</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zf.writestr("_rels/.rels",&nbsp;'''&lt;?xml&nbsp;version="1.0"&nbsp;encoding="UTF-8"&nbsp;standalone="yes"?&gt;</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 80 | <code>&lt;Relationships&nbsp;xmlns="http://schemas.openxmlformats.org/package/2006/relationships"&gt;&lt;Relationship&nbsp;Id="rId1"&nbsp;Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"&nbsp;Target="xl/workbook.xml"/&gt;&lt;/Relationships&gt;''')</code> | Finishes this expression or function-call argument sequence. |
| 81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;entries&nbsp;=&nbsp;"".join(</code> | Opens or closes a multi-line expression or collection. |
| 82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f'&lt;sheet&nbsp;name="{escape(name,&nbsp;quote=True)}"&nbsp;sheetId="{i}"&nbsp;r:id="rId{i}"/&gt;'</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;i,&nbsp;(name,&nbsp;_)&nbsp;in&nbsp;enumerate(sheets,&nbsp;1)</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | Opens or closes a multi-line expression or collection. |
| 85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zf.writestr("xl/workbook.xml",&nbsp;f'&lt;?xml&nbsp;version="1.0"&nbsp;encoding="UTF-8"&nbsp;standalone="yes"?&gt;&lt;workbook&nbsp;xmlns="{main_ns}"&nbsp;xmlns:r="{relationships_ns}"&gt;&lt;sheets&gt;{entries}&lt;/sheets&gt;&lt;/workbook&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rels&nbsp;=&nbsp;"".join(</code> | Opens or closes a multi-line expression or collection. |
| 87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f'&lt;Relationship&nbsp;Id="rId{i}"&nbsp;Type="{relationships_ns}/worksheet"&nbsp;Target="worksheets/sheet{i}.xml"/&gt;'</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;i&nbsp;in&nbsp;range(1,&nbsp;4)</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | Opens or closes a multi-line expression or collection. |
| 90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zf.writestr("xl/_rels/workbook.xml.rels",&nbsp;f'&lt;?xml&nbsp;version="1.0"&nbsp;encoding="UTF-8"&nbsp;standalone="yes"?&gt;&lt;Relationships&nbsp;xmlns="http://schemas.openxmlformats.org/package/2006/relationships"&gt;{rels}&lt;/Relationships&gt;')</code> | Finishes this expression or function-call argument sequence. |
| 91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;i,&nbsp;(_,&nbsp;frame)&nbsp;in&nbsp;enumerate(sheets,&nbsp;1):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_write_sheet(zf,&nbsp;i,&nbsp;frame)</code> | Finishes this expression or function-call argument sequence. |
| 93 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 94 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 95 | <code>class&nbsp;CDFExportMixin:</code> | Starts a class definition; any base classes in parentheses supply inherited behavior. |
| 96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;export_cdf_data(self):</code> | Defines the named function/method; indented lines below form its body. |
| 97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""Save&nbsp;plotted&nbsp;CDF&nbsp;traces,&nbsp;curve&nbsp;statistics,&nbsp;and&nbsp;totals&nbsp;in&nbsp;one&nbsp;workbook."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;self.cdf_plot_data&nbsp;is&nbsp;None&nbsp;or&nbsp;self.cdf_plot_data.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QMessageBox.information(self,&nbsp;"Export&nbsp;CDF",&nbsp;"Plot&nbsp;a&nbsp;CDF&nbsp;first,&nbsp;then&nbsp;export&nbsp;its&nbsp;data.")</code> | Displays an informational, warning, or error popup to the user. |
| 100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 101 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;path,&nbsp;_&nbsp;=&nbsp;QFileDialog.getSaveFileName(</code> | Opens a file picker or a save-file picker. |
| 103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,&nbsp;"Export&nbsp;CDF&nbsp;workbook",&nbsp;str(self.last_dir&nbsp;/&nbsp;"cdf_plot_data.xlsx"),</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Excel&nbsp;workbook&nbsp;(*.xlsx)",</code> | Provides a string label, key, path, or parameter in the surrounding call/collection. |
| 105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | Opens or closes a multi-line expression or collection. |
| 106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;path:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | Ends the current function early without returning a specific value. |
| 108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;output&nbsp;=&nbsp;Path(path).with_suffix(".xlsx")</code> | Assigns the expression on the right to `output` for later use. |
| 109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;overall&nbsp;=&nbsp;pd.DataFrame({</code> | Creates a pandas table from the supplied arrays, rows, or columns. |
| 110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Metric":&nbsp;["Overall&nbsp;absolute-dB&nbsp;P75",&nbsp;"Matched&nbsp;samples",&nbsp;"CDF&nbsp;curves"],</code> | Provides a string label, key, path, or parameter in the surrounding call/collection. |
| 111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Value":&nbsp;[self.cdf_overall_p75,&nbsp;len(self.cdf_paired),&nbsp;len(self.cdf_summary)],</code> | Provides a string label, key, path, or parameter in the surrounding call/collection. |
| 112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;})</code> | Finishes this expression or function-call argument sequence. |
| 113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | Begins a protected block; errors can be handled by the following `except` clauses. |
| 114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write_cdf_workbook(</code> | Opens or closes a multi-line expression or collection. |
| 115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;output,</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_plot_data,</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cdf_summary.assign(Overall_P75_dB=self.cdf_overall_p75),</code> | Stores or updates `self.cdf_summary.assign(Overall_P75_dB` on the current object so other methods can use it. |
| 118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;overall,</code> | Continues the enclosing function call, list, dictionary, or multiline expression with another argument/value. |
| 119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | Opens or closes a multi-line expression or collection. |
| 120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.last_dir&nbsp;=&nbsp;output.parent</code> | Stores or updates `self.last_dir` on the current object so other methods can use it. |
| 121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.statusBar().showMessage(f"Exported&nbsp;CDF&nbsp;workbook:&nbsp;{output}")</code> | Finishes this expression or function-call argument sequence. |
| 122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except&nbsp;Exception&nbsp;as&nbsp;exc:</code> | Handles the specified error type instead of allowing it to stop this operation. |
| 123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;QMessageBox.critical(self,&nbsp;"CDF&nbsp;export&nbsp;error",&nbsp;str(exc))</code> | Displays an informational, warning, or error popup to the user. |


## `src/Lolth/processing/__init__.py`

Package marker file; Python treats this directory as an importable package.

This file is empty on purpose: it marks the package directory. There are no executable lines to explain.


## `src/Lolth/processing/cdf.py`

Compute paired-data CDF statistics.

**Code landmarks:** `cdf_statistics` (line 3, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>import&nbsp;numpy&nbsp;as&nbsp;np</code> | Loads the named Python package/module for use in this file. |
| 2 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 3 | <code>def&nbsp;cdf_statistics(values):</code> | Defines the named function/method; indented lines below form its body. |
| 4 | <code>&nbsp;&nbsp;&nbsp;&nbsp;arr&nbsp;=&nbsp;np.asarray(values,&nbsp;dtype=float)</code> | Converts input data to a NumPy array. |
| 5 | <code>&nbsp;&nbsp;&nbsp;&nbsp;arr&nbsp;=&nbsp;np.sort(arr[np.isfinite(arr)])</code> | Checks that numeric values are real finite numbers rather than NaN or infinity. |
| 6 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;len(arr):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 7 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;np.array([]),&nbsp;np.array([]),&nbsp;(np.nan,&nbsp;np.nan,&nbsp;np.nan)</code> | Returns this computed value to the caller; the function ends here. |
| 8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;y&nbsp;=&nbsp;np.arange(1,&nbsp;len(arr)&nbsp;+&nbsp;1,&nbsp;dtype=float)&nbsp;/&nbsp;len(arr)</code> | Assigns the expression on the right to `y` for later use. |
| 9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;arr,&nbsp;y,&nbsp;tuple(np.percentile(arr,&nbsp;[25,50,75]))</code> | Returns this computed value to the caller; the function ends here. |


## `src/Lolth/processing/frequency.py`

Apply a median across the chosen frequency bandwidth.

**Code landmarks:** `process_frequency_median` (line 3, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>import&nbsp;pandas&nbsp;as&nbsp;pd</code> | Loads the named Python package/module for use in this file. |
| 2 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 3 | <code>def&nbsp;process_frequency_median(flat,&nbsp;selected,&nbsp;bandwidth,&nbsp;unit):</code> | Defines the named function/method; indented lines below form its body. |
| 4 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Process&nbsp;at&nbsp;selected&nbsp;center&nbsp;frequencies,&nbsp;preserving&nbsp;individual&nbsp;angular&nbsp;sweeps.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 5 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 6 | <code>&nbsp;&nbsp;&nbsp;&nbsp;Median&nbsp;is&nbsp;computed&nbsp;across&nbsp;frequencies,&nbsp;NOT&nbsp;with&nbsp;an&nbsp;angular&nbsp;median&nbsp;filter.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 7 | <code>&nbsp;&nbsp;&nbsp;&nbsp;A&nbsp;bandwidth&nbsp;of&nbsp;zero&nbsp;disables&nbsp;processing.&nbsp;Angular&nbsp;coordinates&nbsp;must&nbsp;coincide.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;selected:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;flat.iloc[0:0].copy()</code> | Returns this computed value to the caller; the function ends here. |
| 11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;centers&nbsp;=&nbsp;flat.loc[flat["Freq"].isin(selected)].copy()</code> | Creates a separate copy so later modifications do not unexpectedly change the original data. |
| 12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;centers.empty&nbsp;or&nbsp;bandwidth&nbsp;&lt;=&nbsp;0:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;centers</code> | Returns this computed value to the caller; the function ends here. |
| 14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;outputs&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `outputs` for later use. |
| 15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;center&nbsp;in&nbsp;sorted(set(selected)):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;target&nbsp;=&nbsp;centers.loc[centers["Freq"]&nbsp;==&nbsp;center].copy()</code> | Creates a separate copy so later modifications do not unexpectedly change the original data. |
| 17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;target.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | Skips the rest of this loop iteration and proceeds to the next item. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;width_mhz&nbsp;=&nbsp;bandwidth&nbsp;if&nbsp;unit&nbsp;==&nbsp;"MHz"&nbsp;else&nbsp;center&nbsp;*&nbsp;bandwidth&nbsp;/&nbsp;100.0</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;neighbors&nbsp;=&nbsp;flat.loc[(flat["Freq"]&nbsp;&gt;=&nbsp;center&nbsp;-&nbsp;width_mhz&nbsp;/&nbsp;2)</code> | Finishes this expression or function-call argument sequence. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&&nbsp;(flat["Freq"]&nbsp;&lt;=&nbsp;center&nbsp;+&nbsp;width_mhz&nbsp;/&nbsp;2)]</code> | Finishes this expression or function-call argument sequence. |
| 22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;neighbors.empty:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outputs.append(target)</code> | Finishes this expression or function-call argument sequence. |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | Skips the rest of this loop iteration and proceeds to the next item. |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;median&nbsp;=&nbsp;(neighbors.groupby(["P",&nbsp;"Phi",&nbsp;"Theta"],&nbsp;sort=False)["PdB"]</code> | Groups DataFrame rows by matching column values for independent processing. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.median().rename("_median_power"))</code> | Finishes this expression or function-call argument sequence. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;target&nbsp;=&nbsp;target.join(median,&nbsp;on=["P",&nbsp;"Phi",&nbsp;"Theta"])</code> | Assigns the expression on the right to `target` for later use. |
| 28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;target["PdB"]&nbsp;=&nbsp;target["_median_power"].fillna(target["PdB"])</code> | Assigns the expression on the right to `target["PdB"]` for later use. |
| 29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;outputs.append(target.drop(columns=["_median_power"]))</code> | Finishes this expression or function-call argument sequence. |
| 30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;pd.concat(outputs,&nbsp;ignore_index=True)&nbsp;if&nbsp;outputs&nbsp;else&nbsp;centers.iloc[0:0]</code> | Returns this computed value to the caller; the function ends here. |


## `src/Lolth/processing/resample.py`

Downsample an angular grid by taking neighboring medians.

**Code landmarks:** `resample_angular_median` (line 5, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>"""Angular&nbsp;2x&nbsp;reduction&nbsp;by&nbsp;median&nbsp;over&nbsp;each&nbsp;0.5-degree&nbsp;neighborhood."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 2 | <code>import&nbsp;numpy&nbsp;as&nbsp;np</code> | Loads the named Python package/module for use in this file. |
| 3 | <code>import&nbsp;pandas&nbsp;as&nbsp;pd</code> | Loads the named Python package/module for use in this file. |
| 4 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 5 | <code>def&nbsp;resample_angular_median(frame,&nbsp;step=1.0):</code> | Defines the named function/method; indented lines below form its body. |
| 6 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Return&nbsp;integer-degree&nbsp;angular&nbsp;centers;&nbsp;median&nbsp;I&nbsp;and&nbsp;Q&nbsp;within&nbsp;±0.5°.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 7 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;For&nbsp;a&nbsp;0.5°&nbsp;source&nbsp;grid&nbsp;this&nbsp;forms&nbsp;overlapping&nbsp;3x3&nbsp;neighborhoods.&nbsp;The</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;target&nbsp;center&nbsp;point&nbsp;participates&nbsp;with&nbsp;its&nbsp;immediate&nbsp;half-degree&nbsp;neighbors.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;Recompute&nbsp;PdB&nbsp;from&nbsp;median&nbsp;I/Q&nbsp;to&nbsp;keep&nbsp;complex&nbsp;magnitude&nbsp;consistent.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;If&nbsp;complex&nbsp;samples&nbsp;are&nbsp;missing,&nbsp;use&nbsp;median&nbsp;PdB&nbsp;instead.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;required&nbsp;=&nbsp;{"Freq",&nbsp;"Phi",&nbsp;"Theta",&nbsp;"PdB"}</code> | Assigns the expression on the right to `required` for later use. |
| 14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;not&nbsp;required.issubset(frame.columns):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise&nbsp;ValueError(f"Angular&nbsp;resampling&nbsp;requires&nbsp;{sorted(required)}")</code> | Raises an error to report invalid input or an unsuccessful operation. |
| 16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;columns&nbsp;=&nbsp;[x&nbsp;for&nbsp;x&nbsp;in&nbsp;("I","Q","PdB")&nbsp;if&nbsp;x&nbsp;in&nbsp;frame.columns]</code> | Assigns the expression on the right to `columns` for later use. |
| 17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;out&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `out` for later use. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;(frequency,&nbsp;polarization),&nbsp;group&nbsp;in&nbsp;frame.groupby(["Freq",&nbsp;"P"],&nbsp;sort=False):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tmin,&nbsp;tmax&nbsp;=&nbsp;group["Theta"].min(),group["Theta"].max()</code> | Assigns the expression on the right to `tmin, tmax` for later use. |
| 20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pmin,&nbsp;pmax&nbsp;=&nbsp;group["Phi"].min(),group["Phi"].max()</code> | Assigns the expression on the right to `pmin, pmax` for later use. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;theta_target&nbsp;=&nbsp;np.arange(np.ceil(tmin&nbsp;/&nbsp;step)*step,&nbsp;np.floor(tmax&nbsp;/&nbsp;step)*step+step*.01,&nbsp;step)</code> | Assigns the expression on the right to `theta_target` for later use. |
| 22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi_target&nbsp;=&nbsp;np.arange(np.ceil(pmin&nbsp;/&nbsp;step)*step,&nbsp;np.floor(pmax&nbsp;/&nbsp;step)*step+step*.01,&nbsp;step)</code> | Assigns the expression on the right to `phi_target` for later use. |
| 23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;Each&nbsp;source&nbsp;contributes&nbsp;to&nbsp;integer-degree&nbsp;centers&nbsp;no&nbsp;farther&nbsp;than</code> | Developer comment: Each source contributes to integer-degree centers no farther than |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;half&nbsp;a&nbsp;degree&nbsp;along&nbsp;either&nbsp;axis.&nbsp;Integer-position&nbsp;samples&nbsp;contribute</code> | Developer comment: half a degree along either axis. Integer-position samples contribute |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;#&nbsp;once;&nbsp;half-integer&nbsp;samples&nbsp;contribute&nbsp;to&nbsp;both&nbsp;adjacent&nbsp;centers.</code> | Developer comment: once; half-integer samples contribute to both adjacent centers. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;src&nbsp;=&nbsp;group[["Theta",&nbsp;"Phi"]&nbsp;+&nbsp;columns].reset_index(drop=True)</code> | Assigns the expression on the right to `src` for later use. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;coords&nbsp;=&nbsp;src[["Theta",&nbsp;"Phi"]].to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;target_low&nbsp;=&nbsp;np.floor(coords&nbsp;/&nbsp;step)&nbsp;*&nbsp;step</code> | Assigns the expression on the right to `target_low` for later use. |
| 29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;target_high&nbsp;=&nbsp;np.ceil(coords&nbsp;/&nbsp;step)&nbsp;*&nbsp;step</code> | Assigns the expression on the right to `target_high` for later use. |
| 30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;blocks&nbsp;=&nbsp;[]</code> | Assigns the expression on the right to `blocks` for later use. |
| 31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;it&nbsp;in&nbsp;(0,&nbsp;1):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for&nbsp;ip&nbsp;in&nbsp;(0,&nbsp;1):</code> | Starts a loop, repeating the indented block for every item from this iterable. |
| 33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;theta&nbsp;=&nbsp;(target_low&nbsp;if&nbsp;it&nbsp;==&nbsp;0&nbsp;else&nbsp;target_high)[:,&nbsp;0]</code> | Finishes this expression or function-call argument sequence. |
| 34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi&nbsp;=&nbsp;(target_low&nbsp;if&nbsp;ip&nbsp;==&nbsp;0&nbsp;else&nbsp;target_high)[:,&nbsp;1]</code> | Finishes this expression or function-call argument sequence. |
| 35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;valid&nbsp;=&nbsp;(np.abs(theta&nbsp;-&nbsp;coords[:,&nbsp;0])&nbsp;&lt;=&nbsp;step&nbsp;/&nbsp;2&nbsp;+&nbsp;1e-8)&nbsp;&&nbsp;(np.abs(phi&nbsp;-&nbsp;coords[:,&nbsp;1])&nbsp;&lt;=&nbsp;step&nbsp;/&nbsp;2&nbsp;+&nbsp;1e-8)</code> | Finishes this expression or function-call argument sequence. |
| 36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;it&nbsp;==&nbsp;1:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;valid&nbsp;&=&nbsp;target_high[:,&nbsp;0]&nbsp;!=&nbsp;target_low[:,&nbsp;0]</code> | Finishes this expression or function-call argument sequence. |
| 38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;ip&nbsp;==&nbsp;1:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;valid&nbsp;&=&nbsp;target_high[:,&nbsp;1]&nbsp;!=&nbsp;target_low[:,&nbsp;1]</code> | Finishes this expression or function-call argument sequence. |
| 40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;valid&nbsp;&=&nbsp;(theta&nbsp;&gt;=&nbsp;theta_target[0])&nbsp;&&nbsp;(theta&nbsp;&lt;=&nbsp;theta_target[-1])</code> | Finishes this expression or function-call argument sequence. |
| 41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;valid&nbsp;&=&nbsp;(phi&nbsp;&gt;=&nbsp;phi_target[0])&nbsp;&&nbsp;(phi&nbsp;&lt;=&nbsp;phi_target[-1])</code> | Finishes this expression or function-call argument sequence. |
| 42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;np.any(valid):</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;block&nbsp;=&nbsp;src.loc[valid,&nbsp;columns].copy()</code> | Creates a separate copy so later modifications do not unexpectedly change the original data. |
| 44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;block["Theta"]&nbsp;=&nbsp;theta[valid]</code> | Assigns the expression on the right to `block["Theta"]` for later use. |
| 45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;block["Phi"]&nbsp;=&nbsp;phi[valid]</code> | Assigns the expression on the right to `block["Phi"]` for later use. |
| 46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;blocks.append(block)</code> | Finishes this expression or function-call argument sequence. |
| 47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;candidates&nbsp;=&nbsp;pd.concat(blocks,&nbsp;ignore_index=True)</code> | Combines multiple DataFrames into a single table. |
| 48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agg&nbsp;=&nbsp;candidates.groupby(["Theta","Phi"],&nbsp;as_index=False)[columns].median()</code> | Groups DataFrame rows by matching column values for independent processing. |
| 49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agg.insert(0,"Freq",frequency)</code> | Finishes this expression or function-call argument sequence. |
| 50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agg["P"]&nbsp;=&nbsp;polarization</code> | Assigns the expression on the right to `agg["P"]` for later use. |
| 51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"I"&nbsp;in&nbsp;agg&nbsp;and&nbsp;"Q"&nbsp;in&nbsp;agg:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agg["PdB"]&nbsp;=&nbsp;20*np.log10(np.maximum(np.hypot(agg["I"],agg["Q"]),1e-15))</code> | Assigns the expression on the right to `agg["PdB"]` for later use. |
| 53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agg["E1"]&nbsp;=&nbsp;agg["Phi"]</code> | Assigns the expression on the right to `agg["E1"]` for later use. |
| 54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agg["A1"]&nbsp;=&nbsp;agg["Theta"]</code> | Assigns the expression on the right to `agg["A1"]` for later use. |
| 55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;out.append(agg)</code> | Finishes this expression or function-call argument sequence. |
| 56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;pd.concat(out,&nbsp;ignore_index=True)&nbsp;if&nbsp;out&nbsp;else&nbsp;frame.iloc[0:0].copy()</code> | Returns this computed value to the caller; the function ends here. |


## `src/Lolth/processing/shift.py`

Shift a dataset’s angular coordinates, with wrapping and synchronized aliases.

**Code landmarks:** `shift_dataset_angles` (line 5, function)

| Line | Original source | What it does |
|---:|---|---|
| 1 | <code>"""Periodic&nbsp;angle&nbsp;offsets&nbsp;for&nbsp;loaded&nbsp;RF&nbsp;datasets."""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 2 | <code>import&nbsp;numpy&nbsp;as&nbsp;np</code> | Loads the named Python package/module for use in this file. |
| 3 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 4 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 5 | <code>def&nbsp;shift_dataset_angles(frame,&nbsp;azimuth_delta=0.0,&nbsp;elevation_delta=0.0):</code> | Defines the named function/method; indented lines below form its body. |
| 6 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""Shift&nbsp;angular&nbsp;fields&nbsp;and&nbsp;wrap&nbsp;into&nbsp;the&nbsp;original&nbsp;signed&nbsp;intervals.</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 7 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;Theta/A1:&nbsp;360-degree&nbsp;period,&nbsp;canonical&nbsp;[-180,&nbsp;180).</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;Phi/E1:&nbsp;&nbsp;&nbsp;180-degree&nbsp;period,&nbsp;canonical&nbsp;[-90,&nbsp;90).</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 10 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;The&nbsp;end&nbsp;points&nbsp;of&nbsp;each&nbsp;interval&nbsp;are&nbsp;equivalent&nbsp;under&nbsp;this&nbsp;periodic</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;operation.&nbsp;Preserve&nbsp;the&nbsp;original&nbsp;source-field/plotting-alias&nbsp;agreement.</code> | Executes this Python statement as part of the surrounding function or control-flow block. |
| 13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;"""</code> | Documentation string: explains the purpose or assumptions of the surrounding module, class, or function. |
| 14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;azimuth_delta:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;theta&nbsp;=&nbsp;frame["Theta"].to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;wrapped&nbsp;=&nbsp;(theta&nbsp;+&nbsp;float(azimuth_delta)&nbsp;+&nbsp;180.0)&nbsp;%&nbsp;360.0&nbsp;-&nbsp;180.0</code> | Assigns the expression on the right to `wrapped` for later use. |
| 17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["Theta"]&nbsp;=&nbsp;wrapped</code> | Assigns the expression on the right to `frame["Theta"]` for later use. |
| 18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"A1"&nbsp;in&nbsp;frame.columns:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["A1"]&nbsp;=&nbsp;wrapped</code> | Assigns the expression on the right to `frame["A1"]` for later use. |
| 20 | <code>&nbsp;</code> | Blank separator to make the source easier to read. |
| 21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;elevation_delta:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;phi&nbsp;=&nbsp;frame["Phi"].to_numpy(dtype=float)</code> | Converts a labeled pandas column/table into a NumPy array for numerical operations. |
| 23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;wrapped&nbsp;=&nbsp;(phi&nbsp;+&nbsp;float(elevation_delta)&nbsp;+&nbsp;90.0)&nbsp;%&nbsp;180.0&nbsp;-&nbsp;90.0</code> | Assigns the expression on the right to `wrapped` for later use. |
| 24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["Phi"]&nbsp;=&nbsp;wrapped</code> | Assigns the expression on the right to `frame["Phi"]` for later use. |
| 25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if&nbsp;"E1"&nbsp;in&nbsp;frame.columns:</code> | Tests the condition; the next indented block runs only if the condition is true. |
| 26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;frame["E1"]&nbsp;=&nbsp;wrapped</code> | Assigns the expression on the right to `frame["E1"]` for later use. |
| 27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;frame</code> | Returns this computed value to the caller; the function ends here. |


---

## Safe extension workflow

1. **New widget:** Add it in `main_window.py` or the relevant popup. Connect its signal to a method with `.connect(...)`.
2. **New calculation:** Put a standalone function in `processing/`, then import and call it from the GUI or plotting module. Avoid doing heavy processing directly inside a click handler.
3. **New 2D chart:** Add plotting code in `plotting/charts.py`, then add a menu/dropdown option and dispatcher branch in `main_window.py`.
4. **New file format:** Extend `file_reading/loader.py` to return the same normalized columns; do not force new aliases into every existing input file.
5. **New 3D control:** Extend `modeling/vtk_viewer.py`, preserving the Qt OpenGL interactor path that worked with VTK 9.4.2.
6. **Before shipping:** Run `python -m compileall src/Lolth`, start `PYTHONPATH=src python -m Lolth`, and manually test text/pickle loads, angle filters, all plot types, angle shifts, export, and both 3D dialogs.

**Caveat:** This guide explains statements in the provided v14 source; it is not an independent correctness audit. Lines that only continue a multi-line expression are described in that context rather than as standalone operations.
