"""Fixed dropdown choices, mirrored from shared/mis_pulse_export/choices.py.

Duplicated rather than imported so the client never needs the export
package's openpyxl dependency (keeps the Windows installer's dependency
closure small). Keep in sync if the backend's choices ever change.
"""

LOCATION_TYPES = ["STORE", "DEPARTMENT"]

MIS_PERSONNEL = ["MARCO", "RAMON", "RENZ", "ERICK", "ALBERT", "DSS"]

REMARKS = ["CONCERN DONE", "NOT ACKNOWLEDGE", "WORKING"]

TASK = ["DONE", "PENDING", "WORKING", "NO RESPONSE"]

OWNERSHIP_TYPE = ["H.O.", "COMPANY OWNED", "FRANCHISE"]

TYPE_OF_SUPPORT = ["ONSITE", "REMOTE", "CALL"]
