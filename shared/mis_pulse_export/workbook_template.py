"""Structural constants for the monthly report tab, copied exactly from the
original "MIS SUPPORT SUMMARY REPORT.xlsx" (e.g. its "SEPTEMBER 2026" tab) so
that a generated workbook is indistinguishable from one produced by hand.
"""

from openpyxl.styles import Alignment, Border, Font, Side

from .choices import MIS_PERSONNEL, OWNERSHIP_TYPE, REMARKS, TASK, TYPE_OF_SUPPORT

# Column letter -> (header text, width). Columns with no explicit width in the
# original file (A, F, G, H, R) are left at Excel's default.
COLUMNS = [
    ("A", "DATA", None),
    ("B", "STORE / DEPARTMENT", 26.14),
    ("C", "REPORTED BY:", 30.0),
    ("D", "TIME SENT", 13.0),
    ("E", "TIME RECEIVED", 11.86),
    ("F", "TIME DONE", None),
    ("G", "DURATION", None),
    ("H", "MIS PERSONNEL", None),
    ("I", "PROBLEM", 61.14),
    ("J", "FINDINGS /CAUSE of Problem", 55.57),
    ("K", "ACTION TAKEN", 100.57),
    ("L", "REMARKS", 21.71),
    ("M", "TASK", 13.43),
    ("N", "TASK REMARKS", 57.14),
    ("O", "ACKNOWLEDGE BY:", 17.86),
    ("P", "AREA MANAGER / HEAD", 20.29),
    ("Q", "TYPE", 21.57),
    ("R", "Type of Support (remote/site visit)", None),
]

FREEZE_PANES = "D2"

DATE_FORMAT = "M/d/yyyy"
TIME_FORMAT = "h:mm am/pm"
DURATION_FORMAT = "[h]:mm:ss"

FONT_NAME = "Calibri"
HEADER_FONT = Font(name=FONT_NAME, size=14, bold=True)
DATA_FONT = Font(name=FONT_NAME, size=11, bold=False)

CENTERED_WRAPPED = Alignment(horizontal="center", vertical="center", wrap_text=True)

_THIN = Side(style="thin")
THIN_BOX = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)

# Column letter -> allowed dropdown values, matching the original data validations.
DATA_VALIDATIONS = {
    "H": MIS_PERSONNEL,
    "L": REMARKS,
    "M": TASK,
    "Q": OWNERSHIP_TYPE,
    "R": TYPE_OF_SUPPORT,
}

MONTH_TAB_NAME = "{month_name} {year}"  # e.g. "SEPTEMBER 2026"
