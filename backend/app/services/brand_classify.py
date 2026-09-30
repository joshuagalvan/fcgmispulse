"""Maps a free-text store/department name to (location_type, brand) using
the same brand-prefix convention already present in the historical data
(e.g. "AP Kabihasnan", "F' Trinoma", "TM Makati"). Used both to import
historical entries and to classify anything typed before the curated
Store List is consulted."""

BRAND_PREFIXES = [
    ("ap ", "Angels Pizza"),
    ("ape", "Angels Pizza Express"),
    ("f'", "Figaro"),
    ("f ", "Figaro"),
    ("figaro", "Figaro"),
    ("tm ", "Tien Ma"),
    ("kk ", "Koobideh Kebab"),
]

BRANDS = ["Angels Pizza", "Figaro", "Tien Ma", "Koobideh Kebab", "Angels Pizza Express"]


def classify(name: str) -> tuple[str, str | None]:
    lowered = name.strip().lower()
    for prefix, brand in BRAND_PREFIXES:
        if lowered.startswith(prefix):
            return "STORE", brand
    return "DEPARTMENT", None
