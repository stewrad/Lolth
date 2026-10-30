"""Export all CDF data to one Excel workbook using only Python's standard library.

No artifact_tool, openpyxl, or xlsxwriter installation is required.
"""
from datetime import date, datetime
from html import escape
from math import isfinite
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import pandas as pd
from PyQt6.QtWidgets import QFileDialog, QMessageBox


def _excel_column(index):
    """1-based column index to A, B, ..., AA."""
    letters = []
    while index:
        index, rem = divmod(index - 1, 26)
        letters.append(chr(65 + rem))
    return "".join(reversed(letters))


def _cell_xml(value, address):
    """Make a numeric or inline-string XLSX cell, skipping NaN and missing data."""
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
        if isfinite(number):
            return f'<c r="{address}"><v>{repr(number)}</v></c>'
        return ""
    if isinstance(value, bool):
        return f'<c r="{address}" t="b"><v>{int(value)}</v></c>'
    if isinstance(value, (date, datetime)):
        value = value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    # Remove XML-invalid control characters and escape special XML characters.
    s = "".join(c for c in str(value) if ord(c) >= 32 or c in "\t\n\r")
    return f'<c r="{address}" t="inlineStr"><is><t xml:space="preserve">{escape(s, quote=False)}</t></is></c>'


def _write_sheet(zf, number, frame):
    """Stream a DataFrame into a worksheet without storing all rows as XML."""
    if frame.shape[0] + 1 > 1_048_576 or frame.shape[1] > 16_384:
        raise ValueError("The CDF export exceeds Excel's worksheet row/column limit.")
    with zf.open(f"xl/worksheets/sheet{number}.xml", "w") as stream:
        def write(s):
            stream.write(s.encode("utf-8"))
        write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        write('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>')
        write('<row r="1">')
        for col, name in enumerate(frame.columns, 1):
            write(_cell_xml(str(name), f"{_excel_column(col)}1"))
        write('</row>')
        for row_idx, values in enumerate(frame.itertuples(index=False, name=None), 2):
            write(f'<row r="{row_idx}">')
            for col, value in enumerate(values, 1):
                write(_cell_xml(value, f"{_excel_column(col)}{row_idx}"))
            write('</row>')
        write('</sheetData></worksheet>')


def write_cdf_workbook(path, curves, summary, overall):
    """Write three independent sheets in a single valid .xlsx file."""
    sheets = [
        ("CDF Curves", curves),
        ("Curve Statistics", summary),
        ("Overall Statistics", overall),
    ]
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    relationships_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=6) as zf:
        zf.writestr("[Content_Types].xml", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
''' + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, 4)) + "</Types>")
        zf.writestr("_rels/.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''')
        entries = "".join(
            f'<sheet name="{escape(name, quote=True)}" sheetId="{i}" r:id="rId{i}"/>'
            for i, (name, _) in enumerate(sheets, 1)
        )
        zf.writestr("xl/workbook.xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="{main_ns}" xmlns:r="{relationships_ns}"><sheets>{entries}</sheets></workbook>')
        rels = "".join(
            f'<Relationship Id="rId{i}" Type="{relationships_ns}/worksheet" Target="worksheets/sheet{i}.xml"/>'
            for i in range(1, 4)
        )
        zf.writestr("xl/_rels/workbook.xml.rels", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        for i, (_, frame) in enumerate(sheets, 1):
            _write_sheet(zf, i, frame)


class CDFExportMixin:
    def export_cdf_data(self):
        """Save plotted CDF traces, curve statistics, and totals in one workbook."""
        if self.cdf_plot_data is None or self.cdf_plot_data.empty:
            QMessageBox.information(self, "Export CDF", "Plot a CDF first, then export its data.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export CDF workbook", str(self.last_dir / "cdf_plot_data.xlsx"),
            "Excel workbook (*.xlsx)",
        )
        if not path:
            return
        output = Path(path).with_suffix(".xlsx")
        overall = pd.DataFrame({
            "Metric": ["Overall absolute-dB P75", "Matched samples", "CDF curves"],
            "Value": [self.cdf_overall_p75, len(self.cdf_paired), len(self.cdf_summary)],
        })
        try:
            write_cdf_workbook(
                output,
                self.cdf_plot_data,
                self.cdf_summary.assign(Overall_P75_dB=self.cdf_overall_p75),
                overall,
            )
            self.last_dir = output.parent
            self.statusBar().showMessage(f"Exported CDF workbook: {output}")
        except Exception as exc:
            QMessageBox.critical(self, "CDF export error", str(exc))
