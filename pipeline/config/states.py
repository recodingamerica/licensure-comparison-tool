"""The 50 US states — code, display name, and Justia URL slug — owned in one place.

Every stage that iterates states or needs a state's name/slug imports from here, so
adding a state or fixing a name is a one-line edit, not a three-file hunt. STATE_NAMES
is the source; ALL_STATES and STATE_SLUG derive from it (they used to be three separate
literals in config/states, gap_harvest/_common, and scope/suggest_scope_rules).
"""

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}

# Two-letter codes, in the canonical order above.
ALL_STATES = list(STATE_NAMES)

# Justia code paths use a hyphenated lowercase slug: "New Jersey" -> "new-jersey".
STATE_SLUG = {code: name.lower().replace(" ", "-") for code, name in STATE_NAMES.items()}
