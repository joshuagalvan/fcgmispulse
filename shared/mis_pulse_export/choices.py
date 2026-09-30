"""Fixed dropdown choices, mirroring the original spreadsheet's data validation lists.

Single source of truth for both the API's input validation and the exported
workbook's dropdown (data validation) lists, so the two can never drift apart.
"""

LOCATION_TYPES = ["STORE", "DEPARTMENT"]

MIS_PERSONNEL = ["MARCO", "RAMON", "RENZ", "ERICK", "ALBERT", "DSS"]

REMARKS = ["CONCERN DONE", "NOT ACKNOWLEDGE", "WORKING"]

TASK = ["DONE", "PENDING", "WORKING", "NO RESPONSE"]

OWNERSHIP_TYPE = ["H.O.", "COMPANY OWNED", "FRANCHISE"]

TYPE_OF_SUPPORT = ["ONSITE", "REMOTE", "CALL"]
