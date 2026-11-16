"""File grouping, frequency scanning, and ingest processing UI."""
from pathlib import Path
from uuid import uuid4
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QTableWidget,QTableWidgetItem,QLineEdit,QPushButton,QScrollArea,QGroupBox,QDoubleSpinBox,QCheckBox,QComboBox,QMessageBox,QDialogButtonBox,QHeaderView,QListWidget,QListWidgetItem)
from . import loader as fl
from .loader import normalized_flat
from ..processing.frequency import process_frequency_median
from ..processing.resample import resample_angular_median

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
            resample = QCheckBox("Resample oversampled 0.5° angular grid to 1° (median I/Q)")
            form.addWidget(resample)
            form.addWidget(QLabel("Choose center frequencies to include (+) or exclude (−):"))
            picker = FrequencyPicker(entry["raw"]["Freq"].unique())
            form.addWidget(picker)
            self.config_layout.addWidget(group_box)
            self.configs[name] = dict(entry=entry, toggle=toggle, value=value,
                                      unit=unit, picker=picker, resample=resample)
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
                flat = entry["raw"]
                resample = controls["resample"].isChecked()
                if resample:
                    flat = resample_angular_median(flat)
                flat = process_frequency_median(flat, selected, bandwidth, unit)
                output.append(dict(id=uuid4().hex, name=name, paths=entry["paths"],
                                   data=entry["data"], raw=entry["raw"], flat=flat,
                                   frequencies=selected, bandwidth=bandwidth, unit=unit, resampled=resample,
                                   visible=True, role="None"))
            self.result_groups = output
        except Exception as exc:
            QMessageBox.warning(self, "Dataset configuration", str(exc))
            return
        super().accept()
