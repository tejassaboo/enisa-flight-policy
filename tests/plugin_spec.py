"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "eu-enisa-missions" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 32-scenario row).
MIX = {"easy": 6, "boundary_twin": 8, "multi_rule": 5, "hidden_clause": 3, "distractor": 3, "refusal": 3, "flag": 4}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. It has no overnight-stop rule
# and no day-count rule (date_arithmetic and month_end have no handbook rule behind them, so they are left out).
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "personal_travel": 1, "multi_traveller": 1, "dearer_option": 2, "upgrade_not_taken": 2,
    "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "rail", "train", "railway", "kilometre", "km", "distance", "air", "direct", "nonstop", "connection", "segment",
    "continuous", "flying", "business", "economy", "class", "flexible", "change", "changeable", "refundable",
    "refund", "risk", "cancel", "cancelled", "mission", "order", "authorised", "authorisation", "authorising",
    "officer", "line", "manager", "commissioner", "commission", "member", "derogation", "accompany", "organiser",
    "conference", "leave", "holiday", "personal", "private", "spouse", "husband", "wife", "family", "companion",
    "rest", "tiring", "early", "late", "dawn", "night", "midnight", "morning", "evening", "meeting", "deadline",
    "agency", "pmo", "enisa", "manifest", "manifestly", "unreasonable", "outward", "return", "journey", "dubai",
    "zurich", "dublin", "time", "times",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.Passenger, contract.TravelKind, contract.Settledness, contract.CostBearer, contract.Role,
                     contract.Subject, contract.Outcome]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section). Set to what each actually passes (README).
MAX_PASS_ALWAYS_FLAG = 2
MAX_PASS_ALWAYS_LOWEST = 6  # linden-harbour, pebble-moor, ochre-vale, ember-wharf, nettle-strand, rowan-sedge: the lowest seated fare, and no request declined

# Hand-built duration cases beyond the automatic both-sides tests: (rule, outbound scheduled minutes per
# flight, layovers, expected True / False / None for unclear).
DURATION_CASES = [
    ("business-segment", [240], [], True),
    ("business-segment", [239], [], False),
    ("business-segment", [200, 200], [60], False),  # 400 minutes in the air, but no continuous four hours
    ("business-segment", [150, 250], [60], True),  # one qualifying segment is enough
    ("business-segment", [239, 239], [45], False),
    ("tiring-journey", [600], [], True),
    ("tiring-journey", [599], [], False),
    ("tiring-journey", [300, 300], [90], True),  # the flights' minutes added
    ("tiring-journey", [290, 280], [60], None),  # 570 in the air, 630 elapsed: whether ground time counts is open
    ("tiring-journey", [200, 200], [60], False),
]
