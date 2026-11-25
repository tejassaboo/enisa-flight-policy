"""Writes the ENISA Guide to missions scenario JSON files (authoring aid; the JSON files are the truth).

    python3 tests/build_scenarios.py

Every line number is a line of the frozen handbook (src/plugin/data/policy.txt). Not collected by pytest.
Quotes keep the frozen text's split words ("to tal", "w ould") and its bullet glyph as they are.
"""

import hashlib
import json
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
POLICY = (PLUGIN / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = PLUGIN / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, why, quote=None):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def near(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- the clauses the answers rest on -----
SCOPE = keep(212, 213, "the guide covers missions and authorised travel")
MISSION_IS = keep(218, 220, "a mission is travel solely in the interests of the service")
PERSON = keep(239, 241, "the person concerned is the staff member",
              "The person concerned is the staff member going on mission or the person carrying out the "
              "authorised travel.")
MISSION_DEF = keep(384, 387, "missions need a mission order")
AO_DEROGATION = keep(291, 295, "the authorising officer approves the arrangements, including derogations")
AD_HOC = keep(440, 443, "ad hoc signatures for changes for personal reasons and missions combined with leave")
RESERVE = keep(449, 451, "final reservations once the authorising officer has signed the mission order")
PERSONAL_CHANGE = keep(486, 490, "a change for personal reasons may be authorised, with a cost comparison")
PERSONAL_COST = keep(491, 495, "the traveller meets any extra cost of a personal change",
                     "any additional cost 15 arising from the changes made for personal reasons, including departure "
                     "from and/or return to another location, if the comparison indicates an increase in the cost of "
                     "the mission,")
LEAVE = keep(614, 616, "a mission on validated leave may depart from the place of leave")
LEAVE_COST = keep(617, 621, "leave interrupted: costs reimbursed, AO validation when the order is signed")
HOURS = keep(650, 655, "cannot be required to leave before 8:00 or arrive after 22:00 (take-off, landing)")
OTHER_PLACE = keep(672, 678, "departure from another location: exceptional, or for personal reasons")
RAIL_FARE = keep(700, 701, "rail is reimbursed at the first class fare")
AIR_AUTH = keep(710, 712, "air automatically authorised at 800 km of rail out and back; shorter if cost-efficient")
DIRECT = keep(719, 722, "direct flights normally preferred; the AO may refuse a manifestly unreasonable one")
TIER_ONE = keep(723, 726, "economy, non-refundable included, at the lowest available rates and meeting times")
TIER_TWO = keep(727, 729, "flexible economy if there is an appreciable risk of cancellation or amendment")
TIER_THREE = keep(730, 732, "business if a segment has at least four hours' continuous flying")
DEROGATION = keep(733, 735, "the class of the Member of the Commission accompanied, by derogation")
AUTH_COSTS = keep(1111, 1112, "the organiser may meet the transport costs of authorised travel")
AUTH_WHO = keep(1172, 1176, "the authorisation says who meets each cost, transport included",
                "it must specify, for each of the following, whether the staff member is requesting reimbursement "
                "from the Commission, and, if not, who will meet the corresponding cost:")
AUTH_LIMITS = keep(1189, 1191, "expenses only within the limits of the authorisation")

# ----- nearby clauses that must not change the answer -----
D_RETURN = near(656, 657, "in the case of travel by air, not more than three and a half hours after the end of the "
                "meeting(s);", "the return journey, booked separately")
D_EARLY = near(663, 664, "staff should book their tickets at the earliest opportunity in order to take advantage of "
               "the best rates available.", "book early: no bar on this booking")
D_LM_COST = near(263, 266, "the line manager may in particular ask the person concerned to use arrangements which "
                 "provide optimum cost efficiency", "the line manager has asked for nothing")
D_REST = near(862, 866, "if the total duration of the flights is at least ten hours (tiring journey), the authorising "
              "officer for commitments may decide to grant the staff member up to 24 hours' rest",
              "a rest period, not a cabin rule")
D_RAIL_CLASS = near(700, 701, "The cost of rail travel is reimbursed on the basis of the first class rail fare",
                    "first class on trains says nothing of air cabins")
D_LOW_COST = near(738, 739, "Staff members covered by a signed mission order may make ticket reservations with a low "
                  "-cost airline.", "booking channel, not the fare")
D_AGENCY = near(420, 422, "the agency fees will not be reimbursed except in exceptional circumstances",
                "another agency's fees, not the ticket")
D_EXTRA = near(741, 742, "The authorising officer for commitments authorises any additional travel cost",
               "baggage or seat charges, not the ticket")
D_HOTEL = near(836, 837, "If the maximum hotel allowance is exceeded, the amount will not be reimbur sed",
               "hotel ceiling, not the flight")
D_FAMILY = near(625, 626, "all costs arising from this recall from leave (including for accompanying family) are "
                "reimbursed", "a recall from leave, which this is not")
D_VISA = near(507, 508, "a t least eight working days before the plan ned departure date", "visa deadline, not booking")
D_SECURITY = near(1240, 1241, "In the case of high -risk destinations, staff members automatically receive travel "
                  "advice", "security advice, not the fare")

LM = {"signer_name": "", "signer_title": "Head of Unit", "role": "LINE_MANAGER"}
AO = {"signer_name": "", "signer_title": "Head of Resources, authorising officer for commitments",
      "role": "AUTHORISING_OFFICER"}
LINE_MANAGERS = {
    "Frankfurt": "Petra Hoffmann", "Paris": "Claire Dubois", "Madrid": "Javier Ortega", "Amsterdam": "Sanne de Vries",
    "Munich": "Lukas Brenner",
}
OFFICER = "Eleni Papadaki"


def sign(who, city, subject, wording, outcome="GRANTED", on="2026-11-20"):
    name = LINE_MANAGERS[city] if who is LM else OFFICER
    return {**who, "signer_name": name, "subject": subject, "outcome": outcome, "wording": wording,
            "given_on": "" if outcome == "PENDING" else on}


def order(city, itinerary):
    wording = f"Mission order signed: {itinerary}."
    return [sign(LM, city, "MISSION_ORDER", wording), sign(AO, city, "MISSION_ORDER", wording)]


WORK = {"Frankfurt": "Frankfurt am Main, Germany", "Paris": "Paris, France", "Madrid": "Madrid, Spain",
        "Amsterdam": "Amsterdam, Netherlands", "Munich": "Munich, Germany"}


def trip(city, **fields):
    base = {
        "traveller_name": "", "traveller_title": "", "passenger": "STAFF_MEMBER", "accompanies": "",
        "place_of_employment": WORK[city], "origin": "", "destination": "", "travel_date": "",
        "booking_date": "2026-11-24", "travel_kind": "MISSION", "purpose": "", "must_land_by": "",
        "settledness": "FIRM", "costs_met_by": "AGENCY", "rail_km": 0, "rail_fare_cents": 0, "rail_minutes": 0,
        "planned_return": "", "planned_return_minutes": [], "requested_cabin": "ECONOMY",
        "wants_changeable_fare": False, "prefers_nonstop": False, "approvals": [], "notes": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def fl(carrier, depart, minutes=None, via=None, layovers=None):
    spec = {"carrier": carrier, "depart": depart}
    if via:
        spec["via"] = via
    if minutes:
        spec["minutes"] = minutes
    if layovers:
        spec["layovers"] = layovers
    return spec


def of(slot, flight, cabin, cents, seats=True, refundable=False):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def search(name, origin, destination, date, flights, offers):
    return {"name": name, "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": 0, "flights": flights, "offers": offers}


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": sorted(slots), "cabins": sorted(cabins), "reason_codes": sorted(reasons),
            "approvers": sorted(approvers), "clauses": sorted(clauses), "unclear_phrase": phrase}


# A BOOK rests on the mission order signed by the line manager and the authorising officer (SYNC_NOTES 4').
SIGNED = ["AUTHORISING_OFFICER", "LINE_MANAGER", "NONE"]
AIR = ["AIR_TRAVEL", "TRANSPORT_TO_MISSION"]
S = []


def scenario(id, category, overlays, request, trip_, searches, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": overlays, "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": searches}, "expected": exp, "must_keep": must_keep, "distractors": list(distractors),
        "design_notes": notes,
    })


# ============================== easy ==============================
scenario(
    "linden-harbour", "easy", [],
    "I need to be in Madrid for the certification working group, which starts at 9:30 on Wednesday 9 December. "
    "Please book me a flight on Tuesday the 8th.",
    trip("Frankfurt", traveller_name="Markus Lehmann", traveller_title="Cybersecurity Officer", origin="FRA",
         destination="MAD", travel_date="2026-12-08",
         purpose="Certification working group at the Spanish national cybersecurity centre, Madrid, 9 December from "
                 "09:30", rail_km=1850, rail_fare_cents=38900, rail_minutes=780,
         planned_return="Madrid to Frankfurt nonstop on 9 December", planned_return_minutes=[135],
         approvals=order("Frankfurt", "Frankfurt to Madrid, 8-9 December, by air")),
    [search("out", "FRA", "MAD", "2026-12-08",
            {"lh-am": fl("LH", "09:10"), "ib": fl("IB", "12:40"), "lh-pm": fl("LH", "17:05")},
            [of("lh-am-economy", "lh-am", "ECONOMY", 21200), of("ib-economy", "ib", "ECONOMY", 18900),
             of("lh-pm-economy", "lh-pm", "ECONOMY", 24600)])],
    expected("BOOK", ["ib-economy"], ["ECONOMY"], ["AIR_AUTHORISED_RAIL_DISTANCE", "LOWEST_FARE"], SIGNED, AIR),
    [AIR_AUTH, TIER_ONE, RESERVE],
    "Rail out and back would total 3,700 km, so air is automatically authorised (710-711); the mission order is "
    "signed (449-451); economy at the lowest available rate (723-726): Iberia 18900 cents. The meeting is the "
    "next morning, so every flight lands in time.",
    distractors=[D_EARLY])

scenario(
    "cobalt-ridge", "easy", ["dearer_option"],
    "The incident-response workshop in Copenhagen starts at 12:00 on Thursday 3 December and I have to land by "
    "11:00 to get there. A same-day flight, please; the cheapest one that works.",
    trip("Frankfurt", traveller_name="Anja Becker", traveller_title="Incident Response Expert", origin="FRA",
         destination="CPH", travel_date="2026-12-03",
         purpose="Incident-response workshop, Copenhagen, 3 December from 12:00", must_land_by="2026-12-03 11:00",
         rail_km=860, rail_fare_cents=25400, rail_minutes=470,
         planned_return="Copenhagen to Frankfurt nonstop on 4 December", planned_return_minutes=[85],
         approvals=order("Frankfurt", "Frankfurt to Copenhagen, 3-4 December, by air")),
    [search("out", "FRA", "CPH", "2026-12-03",
            {"early": fl("LH", "08:20"), "mid": fl("LH", "10:30"), "late": fl("LH", "13:00")},
            [of("early-economy", "early", "ECONOMY", 22800), of("mid-economy", "mid", "ECONOMY", 17600),
             of("late-economy", "late", "ECONOMY", 15000)])],
    expected("BOOK", ["early-economy"], ["ECONOMY"], ["AIR_AUTHORISED_RAIL_DISTANCE", "LOWEST_FARE", "MEETING_TIMES"],
             SIGNED, AIR),
    [TIER_ONE, AIR_AUTH],
    "Economy at the lowest available rates 'taking into account the times of meetings' (723-726): the 10:30 and "
    "13:00 flights land at 11:50 and 14:20, after the 11:00 limit, so the 08:20 flight at 22800 cents.",
    distractors=[D_RETURN])

scenario(
    "saffron-dune", "easy", [],
    "I'm presenting at the African cyber capacity conference in Nairobi on Monday 7 December. Please book me on "
    "Saturday 5 December, business class if the guide allows it on this trip; otherwise economy.",
    trip("Paris", traveller_name="Amélie Laurent", traveller_title="Senior Policy Officer", origin="CDG",
         destination="NBO", travel_date="2026-12-05",
         purpose="Cyber capacity-building conference, Nairobi, 7-8 December", requested_cabin="BUSINESS",
         planned_return="Nairobi to Paris nonstop on 9 December", planned_return_minutes=[525],
         notes=["No train route links Paris and Nairobi."],
         approvals=order("Paris", "Paris to Nairobi, 5-9 December, by air")),
    [search("out", "CDG", "NBO", "2026-12-05",
            {"af": fl("AF", "10:30", minutes=[495]), "kq": fl("KQ", "21:15", minutes=[495])},
            [of("af-economy", "af", "ECONOMY", 69000), of("af-business", "af", "BUSINESS", 295000),
             of("kq-economy", "kq", "ECONOMY", 64000), of("kq-business", "kq", "BUSINESS", 278000)])],
    expected("BOOK", ["kq-business"], ["BUSINESS"], ["BUSINESS_SEGMENT_QUALIFIES", "LONG_FLIGHT_APPROVED"], SIGNED,
             ["AIR_TRAVEL"]),
    [TIER_THREE, RESERVE],
    "The nonstop is scheduled at 495 minutes, a segment of well over four hours' continuous flying (730-732): "
    "business at the lowest available rate, Kenya Airways 278000 cents (lands 07:30 on Sunday).",
    distractors=[D_SECURITY])

CHANGE_REQUEST = ("Please book me to Amsterdam on Tuesday 15 December for the threat-landscape meeting the next "
                  "morning, on a ticket I can change, just in case. If the guide doesn't allow a changeable one, "
                  "book what it allows; I have to be at the meeting.")


def change_trip(name, settled, note):
    return trip("Madrid", traveller_name=name, traveller_title="Threat Analyst", origin="MAD", destination="AMS",
                travel_date="2026-12-15", purpose="Threat-landscape working meeting, Amsterdam, 16 December",
                settledness=settled, rail_km=1770, rail_fare_cents=36500, rail_minutes=690,
                planned_return="Amsterdam to Madrid nonstop on 16 December", planned_return_minutes=[140],
                wants_changeable_fare=True, notes=[note],
                approvals=order("Madrid", "Madrid to Amsterdam, 15-16 December, by air"))


CHANGE_SEARCH = [search("out", "MAD", "AMS", "2026-12-15",
                        {"ib": fl("IB", "09:15"), "kl": fl("KL", "14:20")},
                        [of("ib-saver", "ib", "ECONOMY", 16800), of("ib-flex", "ib", "ECONOMY", 30500, refundable=True),
                         of("kl-saver", "kl", "ECONOMY", 15900), of("kl-flex", "kl", "ECONOMY", 33800, refundable=True)])]

scenario(
    "heather-quay", "easy", ["dearer_option"], CHANGE_REQUEST,
    change_trip("Lucía Romero", "UNSETTLED",
                "The host has said the meeting may still be moved to another week; the line manager expects a change."),
    CHANGE_SEARCH,
    expected("BOOK", ["ib-flex"], ["ECONOMY"], ["FLEXIBLE_FARE_CHANGE_RISK"], SIGNED, ["AIR_TRAVEL"]),
    [TIER_TWO, TIER_ONE],
    "The record says the meeting may still be moved: an appreciable risk that the mission will be amended, so "
    "economy at the lowest available rate for flexible tickets (727-729): Iberia's refundable fare, 30500 cents.",
    twin_of="willow-crest", twin_fact="the meeting may still move (UNSETTLED) or is confirmed (FIRM)",
    distractors=[D_LM_COST])

scenario(
    "willow-crest", "easy", [], CHANGE_REQUEST,
    change_trip("Lucía Romero", "FIRM", "The host has confirmed the meeting's date and programme."),
    CHANGE_SEARCH,
    expected("BOOK", ["kl-saver"], ["ECONOMY"], ["FLEXIBLE_FARE_NOT_JUSTIFIED", "REFUNDABLE_FARE_NOT_ALLOWED"], SIGNED,
             ["AIR_TRAVEL"]),
    [TIER_TWO, TIER_ONE],
    "Flexible tickets are for an appreciable risk of cancellation or amendment (727-729); the meeting is confirmed, "
    "so the lowest available rate including tickets that cannot be exchanged or refunded (723-726): KLM 15900 "
    "cents, which lands the afternoon before the meeting.",
    twin_of="heather-quay", twin_fact="the meeting may still move (UNSETTLED) or is confirmed (FIRM)",
    distractors=[D_LM_COST])

scenario(
    "pebble-moor", "easy", ["date_arithmetic"],
    "The cloud certification workshop in Rome starts on Thursday 10 December at 9:00. I'll fly the day before; "
    "please book it.",
    trip("Amsterdam", traveller_name="Daan Visser", traveller_title="Cloud Security Expert", origin="AMS",
         destination="FCO", travel_date="2026-12-09", purpose="Cloud certification workshop, Rome, 10-11 December",
         rail_km=1650, rail_fare_cents=34200, rail_minutes=840,
         planned_return="Rome to Amsterdam nonstop on 11 December", planned_return_minutes=[150],
         approvals=order("Amsterdam", "Amsterdam to Rome, 9-11 December, by air")),
    [search("out", "AMS", "FCO", "2026-12-09",
            {"am": fl("KL", "08:45"), "mid": fl("KL", "13:10"), "pm": fl("KL", "18:30")},
            [of("am-economy", "am", "ECONOMY", 20500), of("mid-economy", "mid", "ECONOMY", 17900),
             of("pm-economy", "pm", "ECONOMY", 19200)])],
    expected("BOOK", ["mid-economy"], ["ECONOMY"], ["AIR_AUTHORISED_RAIL_DISTANCE", "LOWEST_FARE"], SIGNED, AIR),
    [AIR_AUTH, TIER_ONE],
    "The day before Thursday 10 December is Wednesday 9 December. Rail out and back would total 3,300 km (710-711); "
    "economy at the lowest available rate (723-726): KLM 13:10 at 17900 cents.",
    distractors=[D_LOW_COST])

# ============================== boundary twins ==============================
CAIRO_REQUEST = ("The regional capacity-building meeting in Cairo is on Tuesday 8 December; I'll fly on Monday the "
                 "7th. Business class if the guide allows it on this trip; otherwise economy is fine.")


def cairo(name, minutes):
    return (trip("Frankfurt", traveller_name=name, traveller_title="Capacity Building Expert", origin="FRA",
                 destination="CAI", travel_date="2026-12-07",
                 purpose="Regional capacity-building meeting, Cairo, 8 December from 09:00", requested_cabin="BUSINESS",
                 planned_return="Cairo to Frankfurt nonstop on 9 December, scheduled at 235 minutes",
                 planned_return_minutes=[235], notes=["No train route links Frankfurt and Cairo."],
                 approvals=order("Frankfurt", "Frankfurt to Cairo, 7-9 December, by air")),
            [search("out", "FRA", "CAI", "2026-12-07",
                    {"lh": fl("LH", "10:05", minutes=[minutes]), "ms": fl("MS", "13:30", minutes=[minutes])},
                    [of("lh-economy", "lh", "ECONOMY", 31000), of("lh-business", "lh", "BUSINESS", 142000),
                     of("ms-economy", "ms", "ECONOMY", 28500), of("ms-business", "ms", "BUSINESS", 129000)])])


scenario(
    "garnet-sound", "boundary_twin", [], CAIRO_REQUEST, *cairo("Jonas Weber", 240),
    expected("BOOK", ["ms-business"], ["BUSINESS"], ["BUSINESS_SEGMENT_QUALIFIES", "LONG_FLIGHT_APPROVED"], SIGNED,
             ["AIR_TRAVEL"]),
    [TIER_THREE],
    "Both nonstops are scheduled at exactly 240 minutes: 'at least four hours' continuous flying time' is inclusive "
    "(730-732), so business at the lowest available rate, EgyptAir 129000 cents.",
    twin_of="tamarind-gate", twin_fact="scheduled minutes of each nonstop 240 or 235")

scenario(
    "tamarind-gate", "boundary_twin", ["upgrade_not_taken"], CAIRO_REQUEST, *cairo("Jonas Weber", 235),
    expected("BOOK", ["ms-economy"], ["ECONOMY"], ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"], SIGNED,
             ["AIR_TRAVEL"]),
    [TIER_THREE, TIER_ONE],
    "Both nonstops are scheduled at 235 minutes, and so is the planned return: no segment of either journey reaches "
    "four hours (730-732), so economy at the lowest available rate (723-726), EgyptAir 28500 cents.",
    twin_of="garnet-sound", twin_fact="scheduled minutes of each nonstop 240 or 235")

MUNICH_REQUEST = "Please book me a flight to Munich on Wednesday 9 December for Thursday morning's standards meeting."


def munich(km):
    return (trip("Frankfurt", traveller_name="Sabine Krüger", traveller_title="Standardisation Officer", origin="FRA",
                 destination="MUC", travel_date="2026-12-09",
                 purpose="Standards committee meeting, Munich, 10 December from 09:30", rail_km=km,
                 rail_fare_cents=12900, rail_minutes=230,
                 planned_return="Munich to Frankfurt nonstop on 10 December", planned_return_minutes=[60],
                 approvals=order("Frankfurt", "Frankfurt to Munich, 9-10 December, means of transport as the guide "
                                 "allows"),
                 notes=[("Any train ticket for this mission is bought separately through the rail desk, not through "
                         "this flight booking.")]),
            [search("out", "FRA", "MUC", "2026-12-09",
                    {"am": fl("LH", "08:30"), "mid": fl("LH", "12:15"), "pm": fl("LH", "18:40")},
                    [of("am-economy", "am", "ECONOMY", 23800), of("mid-economy", "mid", "ECONOMY", 21200),
                     of("pm-economy", "pm", "ECONOMY", 25600)])])


scenario(
    "ochre-vale", "boundary_twin", [], MUNICH_REQUEST, *munich(400),
    expected("BOOK", ["mid-economy"], ["ECONOMY"], ["AIR_AUTHORISED_RAIL_DISTANCE", "LOWEST_FARE"], SIGNED, AIR),
    [AIR_AUTH, TIER_ONE],
    "Rail is 400 km each way, so out and back would total exactly 800 km: 'at least 800 kilometres' (710-711) "
    "authorises air automatically, though the train is cheaper. Lowest economy fare (723-726): 21200 cents.",
    twin_of="quartz-fell", twin_fact="rail distance 400 or 395 km one way")

scenario(
    "quartz-fell", "boundary_twin", [], MUNICH_REQUEST, *munich(395),
    expected("REFUSE", [], ["NONE"], ["AIR_NOT_AUTHORISED", "DISTANCE_BELOW_MINIMUM", "RAIL_PREFERRED"], SIGNED,
             ["AIR_TRAVEL", "RAIL_TRAVEL", "TRANSPORT_TO_MISSION"]),
    [AIR_AUTH, RAIL_FARE],
    "Rail out and back totals 790 km, under 800 (710-711); air is permitted for shorter distances only on grounds of "
    "cost-efficiency (711-712), and the lowest fare (21200 cents) costs more than the first-class rail fare (12900, "
    "700-701) on a journey of under four hours. The agency buys no flight.",
    twin_of="ochre-vale", twin_fact="rail distance 400 or 395 km one way")

ROME_REQUEST = ("I have a meeting in Rome at 14:00 on Thursday 10 December and need to land by 12:45. Please "
                "don't put me on a crack-of-dawn departure unless the guide says I have to take it.")


def rome(depart):
    return (trip("Madrid", traveller_name="Carmen Vidal", traveller_title="Policy Analyst", origin="MAD",
                 destination="FCO", travel_date="2026-12-10",
                 purpose="Coordination meeting with the Italian cybersecurity agency, Rome, 10 December from 14:00",
                 must_land_by="2026-12-10 12:45", rail_km=1960, rail_fare_cents=41000, rail_minutes=960,
                 planned_return="Rome to Madrid nonstop on 11 December", planned_return_minutes=[150],
                 approvals=order("Madrid", "Madrid to Rome, 10-11 December, by air")),
            [search("out", "MAD", "FCO", "2026-12-10",
                    {"first": fl("IB", depart, minutes=[125]), "second": fl("IB", "10:15", minutes=[125]),
                     "third": fl("IB", "16:05", minutes=[125])},
                    [of("first-economy", "first", "ECONOMY", 17600), of("second-economy", "second", "ECONOMY", 21400),
                     of("third-economy", "third", "ECONOMY", 15900)])])


scenario(
    "juniper-bay", "boundary_twin", [], ROME_REQUEST, *rome("08:00"),
    expected("BOOK", ["first-economy"], ["ECONOMY"], ["AIR_AUTHORISED_RAIL_DISTANCE", "LOWEST_FARE", "MEETING_TIMES",
                                                      "TRAVEL_HOURS_PROTECTED"],
             SIGNED, [*AIR, "DEPARTURE_RETURN", "TRANSPORT_RULES"]),
    [HOURS, TIER_ONE],
    "The first flight takes off at exactly 08:00, which is not 'before 8:00' (650-651), so it can be required; the "
    "16:05 is cheaper but lands after 12:45 (723-726). Lowest fare that lands in time: 17600 cents.",
    twin_of="marigold-tor", twin_fact="first flight takes off 08:00 or 07:55")

scenario(
    "marigold-tor", "boundary_twin", ["dearer_option"], ROME_REQUEST, *rome("07:55"),
    expected("BOOK", ["second-economy"], ["ECONOMY"], ["AIR_AUTHORISED_RAIL_DISTANCE", "LOWEST_FARE", "MEETING_TIMES",
                                                       "TRAVEL_HOURS_PROTECTED"], SIGNED,
             [*AIR, "DEPARTURE_RETURN", "TRANSPORT_RULES"]),
    [HOURS, TIER_ONE],
    "The first flight takes off at 07:55, before 8:00; a staff member cannot be required to leave then without the "
    "line manager's ad hoc decision (650-655), and the traveller does not want it. The 10:15 lands in time: 21400 "
    "cents.",
    twin_of="juniper-bay", twin_fact="first flight takes off 08:00 or 07:55")

MADRID_REQUEST = ("I'll fly to Madrid on Monday 14 December for Tuesday morning's meeting. Please don't land me "
                  "in the middle of the night unless the guide leaves no choice.")


def madrid(depart):
    return (trip("Amsterdam", traveller_name="Pieter Bakker", traveller_title="Network Security Expert", origin="AMS",
                 destination="MAD", travel_date="2026-12-14",
                 purpose="Network security working meeting, Madrid, 15 December from 09:00", rail_km=1770,
                 rail_fare_cents=36500, rail_minutes=690,
                 planned_return="Madrid to Amsterdam nonstop on 15 December", planned_return_minutes=[140],
                 approvals=order("Amsterdam", "Amsterdam to Madrid, 14-15 December, by air")),
            [search("out", "AMS", "MAD", "2026-12-14",
                    {"am": fl("KL", "08:30", minutes=[135]), "ib": fl("IB", "16:40", minutes=[135]),
                     "eve": fl("KL", depart, minutes=[135])},
                    [of("am-economy", "am", "ECONOMY", 24800), of("ib-economy", "ib", "ECONOMY", 22100),
                     of("eve-economy", "eve", "ECONOMY", 18300)])])


scenario(
    "ember-wharf", "boundary_twin", [], MADRID_REQUEST, *madrid("19:45"),
    expected("BOOK", ["eve-economy"], ["ECONOMY"], ["AIR_AUTHORISED_RAIL_DISTANCE", "LOWEST_FARE",
                                                    "TRAVEL_HOURS_PROTECTED"], SIGNED,
             [*AIR, "DEPARTURE_RETURN", "TRANSPORT_RULES"]),
    [HOURS, TIER_ONE],
    "The evening KLM flight lands at exactly 22:00, which is not 'after 22:00' (650-651), so it can be required: "
    "the lowest fare, 18300 cents.",
    twin_of="sorrel-heath", twin_fact="evening flight lands 22:00 or 22:05")

scenario(
    "sorrel-heath", "boundary_twin", ["dearer_option"], MADRID_REQUEST, *madrid("19:50"),
    expected("BOOK", ["ib-economy"], ["ECONOMY"], ["AIR_AUTHORISED_RAIL_DISTANCE", "LOWEST_FARE",
                                                   "TRAVEL_HOURS_PROTECTED"], SIGNED,
             [*AIR, "DEPARTURE_RETURN", "TRANSPORT_RULES"]),
    [HOURS, TIER_ONE],
    "The evening KLM flight lands at 22:05, after 22:00 at the place of the mission; without the line manager's ad "
    "hoc decision the traveller cannot be required to take it (650-655). The lowest fare inside the hours: Iberia "
    "16:40, 22100 cents.",
    twin_of="ember-wharf", twin_fact="evening flight lands 22:00 or 22:05")

# ============================== multi-rule ==============================
scenario(
    "aspen-loch", "multi_rule", [],
    "I have to be at the Rome meeting at 11:00 on Wednesday 2 December and land by 10:00. I'm not a fan of the "
    "6:45 flight, but my head of unit has signed off on an early start for this one. Book whatever the guide says.",
    trip("Paris", traveller_name="Julien Moreau", traveller_title="Data Protection Officer", origin="CDG",
         destination="FCO", travel_date="2026-12-02",
         purpose="Data protection authorities' meeting, Rome, 2 December from 11:00", must_land_by="2026-12-02 10:00",
         rail_km=1420, rail_fare_cents=29800, rail_minutes=660,
         planned_return="Rome to Paris nonstop on 2 December, evening", planned_return_minutes=[125],
         approvals=[*order("Paris", "Paris to Rome and back, 2 December, by air"),
                    sign(LM, "Paris", "TRAVEL_TIMES", "Ad hoc decision, with reasons: departure before 8:00 on 2 "
                         "December is required, so that the day trip needs no hotel night and the traveller reaches "
                         "the 11:00 meeting.")]),
    [search("out", "CDG", "FCO", "2026-12-02",
            {"dawn": fl("AF", "06:45", minutes=[125]), "am": fl("AF", "09:30", minutes=[125]),
             "pm": fl("AF", "14:10", minutes=[125])},
            [of("dawn-economy", "dawn", "ECONOMY", 16200), of("am-economy", "am", "ECONOMY", 21900),
             of("pm-economy", "pm", "ECONOMY", 14900)])],
    expected("BOOK", ["dawn-economy"], ["ECONOMY"], ["LOWEST_FARE", "MEETING_TIMES", "TRAVEL_HOURS_DECISION"], SIGNED,
             ["AIR_TRAVEL", "DEPARTURE_RETURN"]),
    [HOURS, TIER_ONE],
    "Only the 06:45 lands by 10:00 (the 09:30 lands 11:35, the cheaper 14:10 later still, 723-726). A departure "
    "before 8:00 cannot be required unless the line manager adopts an ad hoc decision giving reasons (650-655); "
    "it is on file, so the 06:45 at 16200 cents.",
    distractors=[D_RETURN])

DEROGATION_REQUEST = ("I'm accompanying the Commissioner to Madrid on Thursday 10 December and need to be on her "
                      "09:15 Air France flight, in the same class as her.")


def commissioner(name, wording, outcome, on="2026-11-20"):
    return trip("Paris", traveller_name=name, traveller_title="Adviser to the Executive Director", origin="CDG",
                destination="MAD", travel_date="2026-12-10",
                purpose="Delegation to the EU cybersecurity ministers' conference, Madrid, 10 December from 14:00",
                accompanies="The Member of the Commission responsible for digital affairs, flying business class on "
                            "the 09:15 Air France flight", requested_cabin="BUSINESS", rail_km=1270,
                rail_fare_cents=27500, rail_minutes=560,
                planned_return="Madrid to Paris nonstop on 11 December", planned_return_minutes=[110],
                approvals=[*order("Paris", "Paris to Madrid, 10-11 December, by air, accompanying the Member of the "
                                  "Commission"),
                           sign(AO, "Paris", "CABIN_DEROGATION", wording, outcome, on)])


DEROGATION_SEARCH = [search("out", "CDG", "MAD", "2026-12-10",
                            {"af": fl("AF", "09:15", minutes=[110]), "ib": fl("IB", "12:30", minutes=[110])},
                            [of("af-economy", "af", "ECONOMY", 18400), of("af-business", "af", "BUSINESS", 62000),
                             of("ib-economy", "ib", "ECONOMY", 16900),
                             of("ib-business", "ib", "BUSINESS", 54000, seats=False)])]

scenario(
    "falcon-mere", "multi_rule", ["dearer_option", "synonym"], DEROGATION_REQUEST,
    commissioner("Nathalie Girard", "Authorised by derogation: travel in the same class as the Member of the Commission "
                 "accompanied, for overriding service-related reasons (briefing on board).", "GRANTED"),
    DEROGATION_SEARCH,
    expected("BOOK", ["af-business"], ["BUSINESS"], ["ACCOMPANYING_MEMBER_CLASS"], SIGNED, ["AIR_TRAVEL", "ROLES"]),
    [DEROGATION, AO_DEROGATION, TIER_THREE],
    "A 110-minute flight gives no business class (730-732), but by derogation staff may be authorised to travel in "
    "the class of the Member of the Commission they accompany (733-735); the authorising officer, who approves "
    "derogations (291-295), authorised it. The Commissioner's business seat: 62000 cents.",
    distractors=[D_EXTRA])

DUBAI_REQUEST = ("I'm speaking at the Gulf cyber resilience forum in Dubai on Tuesday 8 December. I'd like the "
                 "nonstop on Monday the 7th if possible; economy is fine.")


def dubai(name, approvals):
    return trip("Amsterdam", traveller_name=name, traveller_title="Resilience Expert", origin="AMS", destination="DXB",
                travel_date="2026-12-07", purpose="Gulf cyber resilience forum, Dubai, 8 December from 09:00",
                prefers_nonstop=True, planned_return="Dubai to Amsterdam on 9 December, booked separately",
                planned_return_minutes=[245, 185], notes=["No train route links Amsterdam and Dubai."],
                approvals=[*order("Amsterdam", "Amsterdam to Dubai, 7-9 December, by air"), *approvals])


DUBAI_SEARCH = [search("out", "AMS", "DXB", "2026-12-07",
                       {"kl": fl("KL", "10:20", minutes=[385]), "ek": fl("EK", "11:50", minutes=[385]),
                        "tk": fl("TK", "09:05", via=["IST"], minutes=[185, 245], layovers=[90])},
                       [of("kl-economy", "kl", "ECONOMY", 114000), of("ek-economy", "ek", "ECONOMY", 119000),
                        of("tk-economy", "tk", "ECONOMY", 31000)])]

scenario(
    "indigo-brae", "multi_rule", ["multi_leg", "upgrade_not_taken"], DUBAI_REQUEST,
    dubai("Thomas Jansen", [sign(AO, "Amsterdam", "NONSTOP_FLIGHT", "Refused: the nonstop flights to Dubai are a "
                                 "manifestly unreasonable expense for this mission; book the connection.", "REFUSED")]),
    DUBAI_SEARCH,
    expected("BOOK", ["tk-economy"], ["ECONOMY"], ["ALTERNATE_ROUTE_TOO_EXPENSIVE", "DIRECT_FLIGHT_REFUSED"], SIGNED,
             ["AIR_TRAVEL"]),
    [DIRECT, TIER_ONE],
    "Direct flights are normally preferred, but the authorising officer may refuse one that would be a manifestly "
    "unreasonable expense (719-722), and has refused it: Turkish via Istanbul, 31000 cents. Business would be "
    "allowed (a 245-minute segment, 730-732), but the traveller asks for economy.",
    distractors=[D_LM_COST])

scenario(
    "kestrel-plain", "multi_rule", ["multi_leg"],
    "Business class to Dubai on Monday 7 December if the guide allows it; I'm presenting at the forum on Tuesday "
    "morning. Otherwise economy.",
    trip("Frankfurt", traveller_name="Felix Schulz", traveller_title="Head of Sector, Operational Cooperation",
         origin="FRA", destination="DXB", travel_date="2026-12-07",
         purpose="Gulf cyber resilience forum, Dubai, 8 December from 09:00", requested_cabin="BUSINESS",
         planned_return="Dubai to Frankfurt via Istanbul on 9 December, booked separately",
         planned_return_minutes=[250, 195], notes=["No train route links Frankfurt and Dubai."],
         approvals=order("Frankfurt", "Frankfurt to Dubai, 7-9 December, by air")),
    [search("out", "FRA", "DXB", "2026-12-07",
            {"tk-am": fl("TK", "09:40", via=["IST"], minutes=[160, 250], layovers=[85]),
             "tk-mid": fl("TK", "10:30", via=["IST"], minutes=[160, 245], layovers=[80])},
            [of("tk-am-economy", "tk-am", "ECONOMY", 42000), of("tk-am-business", "tk-am", "BUSINESS", 165000),
             of("tk-mid-economy", "tk-mid", "ECONOMY", 39800), of("tk-mid-business", "tk-mid", "BUSINESS", 176000)])],
    expected("BOOK", ["tk-am-business"], ["BUSINESS"], ["BUSINESS_SEGMENT_QUALIFIES", "LONG_FLIGHT_APPROVED"], SIGNED,
             ["AIR_TRAVEL"]),
    [TIER_THREE],
    "No nonstop is listed; both connections include an Istanbul-Dubai segment of at least 240 minutes, so the "
    "outward journey 'includes at least one segment' of four hours' continuous flying (730-732): business at the "
    "lowest available rate, 165000 cents.",
    distractors=[D_REST])

ZURICH_REQUEST = ("I'm spending the weekend in Zurich before the Rome meeting on Monday 14 December at 10:00, so "
                  "please book me from Zurich to Rome on Sunday the 13th.")


def zurich(name, approvals, note):
    return trip("Paris", traveller_name=name, traveller_title="Market Certification Officer", origin="ZRH",
                destination="FCO", travel_date="2026-12-13",
                purpose="Certification scheme meeting, Rome, 14 December from 10:00", rail_km=1420,
                rail_fare_cents=29800, rail_minutes=660,
                planned_return="Rome to Paris nonstop on 14 December, evening", planned_return_minutes=[125],
                notes=[note], approvals=[*order("Paris", "Paris to Rome and back, 13-14 December, by air"), *approvals])


ZURICH_SEARCHES = [
    search("out", "ZRH", "FCO", "2026-12-13", {"am": fl("LX", "10:20"), "pm": fl("LX", "17:45")},
           [of("am-economy", "am", "ECONOMY", 16800), of("pm-economy", "pm", "ECONOMY", 15200)]),
    search("comparison", "CDG", "FCO", "2026-12-13", {"am": fl("AF", "11:05"), "pm": fl("AF", "18:10")},
           [of("paris-am-economy", "am", "ECONOMY", 13900), of("paris-pm-economy", "pm", "ECONOMY", 17100)]),
]

scenario(
    "lotus-cairn", "multi_rule", ["personal_travel", "outside_air_section", "dearer_option"], ZURICH_REQUEST,
    zurich("Hélène Fabre", [sign(LM, "Paris", "DEPARTURE_ELSEWHERE", "Ad hoc signature: departure from Zurich for "
                                 "personal reasons authorised; the cost comparison with Paris is attached and any extra "
                                 "cost is met by the traveller."),
                            sign(AO, "Paris", "DEPARTURE_ELSEWHERE", "Authorised: departure from Zurich for personal "
                                 "reasons; the cost comparison with Paris is attached and any extra cost is met by the "
                                 "traveller.")],
           "The traveller spends the weekend in Zurich privately; the comparison flight is Paris to Rome the same day."),
    ZURICH_SEARCHES,
    expected("BOOK", ["pm-economy"], ["ECONOMY"], ["LOWEST_FARE", "PERSONAL_CHANGE_AUTHORISED"], SIGNED,
             ["AIR_TRAVEL", "DEPARTURE_RETURN", "MISSION_ORDER_RULES", "PERSONAL_CHANGES"]),
    [OTHER_PLACE, PERSONAL_CHANGE, PERSONAL_COST, AD_HOC],
    "Departure from a place other than the place of employment may be authorised for personal reasons (672-678) "
    "under 2.2.2.4: a cost comparison, any extra cost met by the traveller (486-496); both ad hoc signatures are on "
    "file (440-443). The lowest fare from Zurich: Swiss 17:45, 15200 cents (the Paris flight at 13900 is the "
    "comparison, not the ticket).",
    distractors=[D_AGENCY])

# ============================== hidden clause ==============================
scenario(
    "nettle-strand", "hidden_clause", ["personal_travel", "outside_air_section"],
    "I'm on leave in Dublin when the Madrid workshop happens, so I'll go straight from there. The workshop starts "
    "at 9:30 on Thursday 10 December; please book me from Dublin on Wednesday the 9th.",
    trip("Frankfurt", traveller_name="Katrin Vogel", traveller_title="Awareness Programme Officer", origin="DUB",
         destination="MAD", travel_date="2026-12-09",
         purpose="Awareness-raising workshop, Madrid, 10 December from 09:30", rail_km=1850, rail_fare_cents=38900,
         rail_minutes=780, planned_return="Madrid to Frankfurt nonstop on 10 December", planned_return_minutes=[135],
         notes=["The workshop was scheduled after the traveller's leave had been validated."],
         approvals=[sign(LM, "Frankfurt", "VALIDATED_LEAVE", "Leave validated: 7-18 December, in Dublin.",
                         on="2026-10-30"),
                    *order("Frankfurt", "departure from Dublin, where the staff member is on leave, to Madrid on 9 "
                           "December; return to Frankfurt on 10 December; by air")]),
    [search("out", "DUB", "MAD", "2026-12-09", {"ei": fl("EI", "10:30"), "ib": fl("IB", "15:20")},
            [of("ei-economy", "ei", "ECONOMY", 14900), of("ib-economy", "ib", "ECONOMY", 13700)])],
    expected("BOOK", ["ib-economy"], ["ECONOMY"], ["LEAVE_PLACE_DEPARTURE", "LOWEST_FARE"], SIGNED,
             ["AIR_TRAVEL", "DEPARTURE_RETURN", "LEAVE_INTERRUPTED"]),
    [LEAVE, LEAVE_COST, TIER_ONE],
    "A mission organised for dates of validated leave may start from the place of leave (614-616, 620-621), subject "
    "to the authorising officer's validation when the order is signed (617-619), which it is. The lowest fare from "
    "Dublin: Iberia 13700 cents.",
    distractors=[D_FAMILY])

scenario(
    "rowan-sedge", "hidden_clause", [],
    "Please book me a flight to Zurich on Monday 7 December for the cyber exercise planning meeting on Tuesday "
    "morning.",
    trip("Munich", traveller_name="Tobias Wagner", traveller_title="Exercise Planner", origin="MUC", destination="ZRH",
         travel_date="2026-12-07", purpose="Cyber exercise planning meeting, Zurich, 8 December from 09:00",
         rail_km=315, rail_fare_cents=14800, rail_minutes=210,
         planned_return="Zurich to Munich nonstop on 8 December", planned_return_minutes=[60],
         approvals=order("Munich", "Munich to Zurich, 7-8 December, means of transport as the guide allows")),
    [search("out", "MUC", "ZRH", "2026-12-07", {"lx": fl("LX", "11:15"), "lh": fl("LH", "16:40")},
            [of("lx-economy", "lx", "ECONOMY", 9600), of("lh-economy", "lh", "ECONOMY", 11800)])],
    expected("BOOK", ["lx-economy"], ["ECONOMY"], ["AIR_COST_EFFICIENT", "LOWEST_FARE"], SIGNED,
             ["AIR_TRAVEL", "RAIL_TRAVEL", "TRANSPORT_TO_MISSION"]),
    [AIR_AUTH, RAIL_FARE, TIER_ONE],
    "Rail out and back totals 630 km, under 800, so air is not automatic; it is permitted for shorter distances when "
    "justified on grounds of cost-efficiency (710-712), and the 9600-cent fare is below the 14800-cent first-class "
    "rail fare that would otherwise be reimbursed (700-701).",
    distractors=[D_EARLY])

scenario(
    "umber-glen", "hidden_clause", ["multi_leg", "upgrade_not_taken"],
    "Business class to Doha on Wednesday 2 December, please; it's a long day of flying. If the guide doesn't allow "
    "it, economy; the workshop starts Thursday morning.",
    trip("Madrid", traveller_name="Alberto Sanz", traveller_title="Maritime Cybersecurity Expert", origin="MAD",
         destination="DOH", travel_date="2026-12-02", purpose="Port cybersecurity workshop, Doha, 3 December from 09:00",
         requested_cabin="BUSINESS",
         planned_return="Doha to Madrid via Istanbul on 4 December, booked separately, scheduled at 235 and 230 minutes",
         planned_return_minutes=[235, 230], notes=["No train route links Madrid and Doha."],
         approvals=order("Madrid", "Madrid to Doha, 2-4 December, by air")),
    [search("out", "MAD", "DOH", "2026-12-02",
            {"tk-am": fl("TK", "08:30", via=["IST"], minutes=[225, 230], layovers=[70]),
             "tk-mid": fl("TK", "10:05", via=["IST"], minutes=[225, 230], layovers=[70])},
            [of("tk-am-economy", "tk-am", "ECONOMY", 43000), of("tk-am-business", "tk-am", "BUSINESS", 149000),
             of("tk-mid-economy", "tk-mid", "ECONOMY", 45500), of("tk-mid-business", "tk-mid", "BUSINESS", 158000)])],
    expected("BOOK", ["tk-am-economy"], ["ECONOMY"], ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"], SIGNED,
             ["AIR_TRAVEL"]),
    [TIER_THREE, TIER_ONE],
    "Seven and a half hours of flying, but in segments of 225 and 230 minutes (and 235 and 230 back): none involves "
    "four hours' continuous flying time (730-732), so economy at the lowest available rate (723-726), 43000 cents.",
    distractors=[D_REST])

# ============================== distractors ==============================
scenario(
    "violet-shoal", "distractor", ["dearer_option"],
    "I'd like the nonstop to Copenhagen on Wednesday 9 December, please; the CSIRT network meeting is Thursday morning.",
    trip("Paris", traveller_name="Sophie Martin", traveller_title="CSIRT Network Officer", origin="CDG",
         destination="CPH", travel_date="2026-12-09", purpose="CSIRT network meeting, Copenhagen, 10 December from 09:30",
         prefers_nonstop=True, rail_km=1230, rail_fare_cents=31500, rail_minutes=720,
         planned_return="Copenhagen to Paris nonstop on 10 December", planned_return_minutes=[110],
         approvals=order("Paris", "Paris to Copenhagen, 9-10 December, by air")),
    [search("out", "CDG", "CPH", "2026-12-09",
            {"af": fl("AF", "11:20"), "kl": fl("KL", "10:05", via=["AMS"], layovers=[70])},
            [of("af-economy", "af", "ECONOMY", 26500), of("kl-economy", "kl", "ECONOMY", 22800)])],
    expected("BOOK", ["af-economy"], ["ECONOMY"], ["DIRECT_FLIGHT_PREFERRED"], SIGNED, ["AIR_TRAVEL"]),
    [DIRECT],
    "Direct flights are normally preferred (719); the authorising officer has refused nothing, and a nonstop 3700 "
    "cents above the connection is no manifestly unreasonable expense. The line manager's power to ask for cheaper "
    "arrangements (263-266) was not used: the nonstop, 26500 cents.",
    distractors=[D_LM_COST, D_EARLY])

scenario(
    "yarrow-point", "distractor", [],
    "Business class to Singapore on Saturday 5 December, please. The authorising officer has given me a rest day "
    "before Monday's meeting.",
    trip("Frankfurt", traveller_name="Stefan Richter", traveller_title="International Cooperation Officer",
         origin="FRA", destination="SIN", travel_date="2026-12-05",
         purpose="International cyber week, Singapore, 7 December from 09:00", requested_cabin="BUSINESS",
         planned_return="Singapore to Frankfurt nonstop on 9 December", planned_return_minutes=[790],
         notes=["No train route links Frankfurt and Singapore."],
         approvals=[*order("Frankfurt", "Frankfurt to Singapore, 5-9 December, by air"),
                    sign(AO, "Frankfurt", "REST_PERIOD", "Granted: up to 24 hours' rest at the place of the mission "
                         "before the meeting, the flights lasting more than ten hours.")]),
    [search("out", "FRA", "SIN", "2026-12-05",
            {"sq": fl("SQ", "11:30", minutes=[765]), "lh": fl("LH", "21:45", minutes=[765])},
            [of("sq-economy", "sq", "ECONOMY", 91000), of("sq-business", "sq", "BUSINESS", 378000),
             of("lh-economy", "lh", "ECONOMY", 88000), of("lh-business", "lh", "BUSINESS", 395000)])],
    expected("BOOK", ["sq-business"], ["BUSINESS"], ["BUSINESS_SEGMENT_QUALIFIES", "LONG_FLIGHT_APPROVED"], SIGNED,
             ["AIR_TRAVEL"]),
    [TIER_THREE],
    "The rest period (862-866) lengthens the mission and changes no ticket. The nonstop's 765-minute segment "
    "qualifies for business (730-732): the lowest business fare, Singapore Airlines 378000 cents.",
    distractors=[D_REST, D_SECURITY])

scenario(
    "zephyr-knoll", "distractor", ["upgrade_not_taken"],
    "The guide pays first class on trains, so I assume business class on the plane to Madrid is fine. Please book "
    "it for Wednesday 2 December; the meeting is Thursday morning. If it isn't allowed, book what the guide allows; "
    "I have to be there.",
    trip("Munich", traveller_name="Maximilian Huber", traveller_title="Supply Chain Security Expert", origin="MUC",
         destination="MAD", travel_date="2026-12-02", purpose="Supply chain security meeting, Madrid, 3 December from "
         "09:00", requested_cabin="BUSINESS", rail_km=2050, rail_fare_cents=43500, rail_minutes=900,
         planned_return="Madrid to Munich nonstop on 3 December, scheduled at 155 minutes",
         planned_return_minutes=[155], approvals=order("Munich", "Munich to Madrid, 2-3 December, by air")),
    [search("out", "MUC", "MAD", "2026-12-02",
            {"lh": fl("LH", "09:50", minutes=[150]), "ib": fl("IB", "14:30", minutes=[150])},
            [of("lh-economy", "lh", "ECONOMY", 20500), of("lh-business", "lh", "BUSINESS", 64000),
             of("ib-economy", "ib", "ECONOMY", 18700), of("ib-business", "ib", "BUSINESS", 59000)])],
    expected("BOOK", ["ib-economy"], ["ECONOMY"], ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"], SIGNED,
             ["AIR_TRAVEL"]),
    [TIER_THREE, TIER_ONE],
    "First-class rail (700-701) says nothing about air: business needs a segment of four hours' continuous flying "
    "(730-732), and the 150-minute nonstop has none. Economy at the lowest available rate (723-726): 18700 cents.",
    distractors=[D_RAIL_CLASS])

# ============================== refusals ==============================
scenario(
    "bramble-isle", "refusal", ["personal_travel", "outside_air_section"],
    "Could you book me a flight to Rome on Saturday 19 December? It's for a family holiday.",
    trip("Frankfurt", traveller_name="Miriam Schneider", traveller_title="Finance Assistant", origin="FRA",
         destination="FCO", travel_date="2026-12-19", travel_kind="PRIVATE_TRIP", purpose="Family holiday in Rome",
         costs_met_by="NO_DOCUMENT", rail_km=1330, rail_fare_cents=27900, rail_minutes=720,
         planned_return="Rome to Frankfurt nonstop on 2 January"),
    [search("out", "FRA", "FCO", "2026-12-19", {"lh": fl("LH", "10:15")}, [of("lh-economy", "lh", "ECONOMY", 14500)])],
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"],
             ["MISSION_DEFINITION", "SCOPE"]),
    [SCOPE, MISSION_IS, MISSION_DEF],
    "The guide covers missions (travel solely in the interests of the service, under a mission order) and "
    "authorised travel (212-213, 218-220, 384-387). A family holiday is neither: the agency buys no ticket.")

scenario(
    "cedar-fjord", "refusal", ["multi_traveller", "outside_air_section"],
    "My husband would like to come with me to Copenhagen for my mission on Wednesday 9 December. Could you book him "
    "on my flight?",
    trip("Amsterdam", traveller_name="Willem de Jong", traveller_title="Husband of Eva de Jong, Policy Officer",
         passenger="FAMILY_MEMBER", accompanies="Eva de Jong, Policy Officer, on mission to Copenhagen",
         origin="AMS", destination="CPH", travel_date="2026-12-09", travel_kind="PRIVATE_TRIP",
         purpose="Joining his wife's mission to Copenhagen", costs_met_by="NO_DOCUMENT", rail_km=780,
         rail_fare_cents=22500, rail_minutes=660, planned_return="Copenhagen to Amsterdam nonstop on 11 December",
         approvals=order("Amsterdam", "Eva de Jong: Amsterdam to Copenhagen, 9-11 December, by air")),
    [search("out", "AMS", "CPH", "2026-12-09", {"kl": fl("KL", "09:40")}, [of("kl-economy", "kl", "ECONOMY", 16200)])],
    expected("REFUSE", [], ["NONE"], ["COMPANION_NOT_COVERED", "PERSONAL_TRAVEL_NOT_COVERED"], SIGNED,
             ["MISSION_DEFINITION", "ROLES", "SCOPE"]),
    [SCOPE, PERSON, MISSION_IS],
    "The guide covers the person concerned, the staff member on mission (212-213, 239-241); a mission is travel in "
    "the interests of the service (218-220). The husband's trip is neither; the staff member's own signed order "
    "goes unused. The agency buys no ticket.")

scenario(
    "dahlia-spur", "refusal", ["outside_air_section"],
    "The conference organisers booked me on the 09:05 flight to Paris on Thursday 10 December, but I'd rather take "
    "the 13:30 so I can finish some work first. Could the agency buy that one for me instead?",
    trip("Madrid", traveller_name="Raquel Iglesias", traveller_title="Research Officer", origin="MAD",
         destination="CDG", travel_date="2026-12-10", travel_kind="AUTHORISED_TRAVEL",
         purpose="Speaker at an academic security conference in Paris, 11 December", costs_met_by="ORGANISER",
         rail_km=1270, rail_fare_cents=27500, rail_minutes=560,
         planned_return="Paris to Madrid on 11 December, booked by the organiser",
         notes=["The organiser has issued an e-ticket on the 09:05 Iberia flight on 10 December."],
         approvals=[sign(LM, "Madrid", "AUTHORISATION_TO_TRAVEL", "Authorisation to travel signed: speaker at the "
                         "conference, 10-11 December; transport and accommodation met by the organiser; no cost for the "
                         "agency's budget.")]),
    [search("out", "MAD", "CDG", "2026-12-10", {"ib": fl("IB", "09:05"), "af": fl("AF", "13:30")},
            [of("ib-economy", "ib", "ECONOMY", 15600), of("af-economy", "af", "ECONOMY", 17400)])],
    expected("REFUSE", [], ["NONE"], ["DOUBLE_BOOKING_PROHIBITED", "TRANSPORT_PAID_BY_ORGANISER"], ["LINE_MANAGER", "NONE"],
             ["AUTHORISED_TRAVEL", "AUTHORISED_TRAVEL_GENERAL", "AUTHORISED_TRAVEL_TRANSPORT", "EXTERNAL_EVENTS",
              "ORGANISER_EXPENSES", "TRAVEL_AUTHORISATION_REQUEST"]),
    [AUTH_COSTS, AUTH_WHO, AUTH_LIMITS],
    "Authorised travel whose transport the organiser meets (1111-1112), as the signed authorisation states "
    "(1172-1176); the traveller may incur expenses only within its limits (1189-1191). The organiser's ticket is "
    "issued: the agency buys nothing.")

# ============================== flags ==============================
scenario(
    "fennel-rock", "flag", ["multi_leg", "unclear_phrase"], DUBAI_REQUEST,
    dubai("Thomas Jansen", []), DUBAI_SEARCH,
    expected("FLAG_FOR_APPROVAL", ["kl-economy", "tk-economy"], ["ECONOMY"], ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"],
             ["AUTHORISING_OFFICER", "NOT_NAMED"], ["AIR_TRAVEL"], "manifestly unreasonable expense"),
    [DIRECT, TIER_ONE],
    "The nonstop (114000 cents) is over three times the connection (31000). Direct flights are normally preferred, "
    "but the authorising officer may refuse one that 'would represent a manifestly unreasonable expense' (719-722), "
    "undefined, and no decision is on file.",
    flag_twins=["indigo-brae", "violet-shoal"],
    ambiguity={"phrase": "manifestly unreasonable expense",
               "readings": [("Direct flights are normally preferred and the authorising officer has refused nothing: "
                             "the nonstop is booked (KLM, 114000 cents)."),
                            ("A nonstop at more than three times the connection is a manifestly unreasonable expense: "
                             "the connection via Istanbul is booked (31000 cents).")]})

scenario(
    "hazel-tide", "flag", ["unclear_phrase"],
    "Business class on the flight to Istanbul on Monday 7 December if the guide allows it on this trip; otherwise "
    "economy.",
    trip("Frankfurt", traveller_name="Laura Fischer", traveller_title="Threat Intelligence Analyst", origin="FRA",
         destination="IST", travel_date="2026-12-07",
         purpose="Two-stop mission: threat intelligence meeting, Istanbul, 8 December; then the Gulf forum, Dubai, "
                 "10 December", requested_cabin="BUSINESS",
         planned_return="Dubai to Frankfurt nonstop on 11 December, booked separately, scheduled at 375 minutes",
         planned_return_minutes=[375], rail_km=2550, rail_fare_cents=52000, rail_minutes=2160,
         notes=["The flight from Istanbul to Dubai on 9 December is booked separately."],
         approvals=order("Frankfurt", "Frankfurt to Istanbul (7 December), Istanbul to Dubai (9 December), Dubai to "
                         "Frankfurt (11 December), by air")),
    [search("out", "FRA", "IST", "2026-12-07",
            {"tk": fl("TK", "10:10", minutes=[160]), "lh": fl("LH", "14:25", minutes=[160])},
            [of("tk-economy", "tk", "ECONOMY", 23800), of("tk-business", "tk", "BUSINESS", 89000),
             of("lh-economy", "lh", "ECONOMY", 26500), of("lh-business", "lh", "BUSINESS", 96000)])],
    expected("FLAG_FOR_APPROVAL", ["tk-business", "tk-economy"], ["BUSINESS", "ECONOMY"],
             ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], ["AUTHORISING_OFFICER", "LINE_MANAGER", "NOT_NAMED"],
             ["AIR_TRAVEL"], "if the outward or return journey includes"),
    [TIER_THREE],
    "The outward nonstop is 160 minutes; the planned return from Dubai is a 375-minute nonstop. Lines 730-732 allow "
    "business 'if the outward or return journey includes' a qualifying segment, without saying whether that opens "
    "business on the other journey too.",
    flag_twins=["garnet-sound", "tamarind-gate"],
    ambiguity={"phrase": "if the outward or return journey includes",
               "readings": [("The condition is met by the trip as a whole: the return includes a 375-minute segment, so "
                             "business may be booked on the outward flight too (Turkish, 89000 cents)."),
                            ("Each journey is judged by its own segments: the outward flight has none of four hours, so "
                             "economy (Turkish, 23800 cents).")]})

scenario(
    "iris-bluff", "flag", ["personal_travel", "approval_required", "outside_air_section"], ZURICH_REQUEST,
    zurich("Hélène Fabre", [], "The traveller spends the weekend in Zurich privately; no leave is booked, and no "
                               "request to depart from Zurich has been signed."),
    ZURICH_SEARCHES,
    expected("FLAG_FOR_APPROVAL", ["pm-economy"], ["ECONOMY"], ["APPROVAL_REQUIRED"],
             ["AUTHORISING_OFFICER", "LINE_MANAGER"], ["DEPARTURE_RETURN", "MISSION_ORDER_RULES", "PERSONAL_CHANGES"]),
    [OTHER_PLACE, PERSONAL_CHANGE, AD_HOC],
    "Departure from another place for personal reasons needs the authorising officer's authorisation (672-678) and "
    "the line manager's and authorising officer's ad hoc signatures (440-443); the mission order is for Paris. "
    "Hold the lowest Zurich fare, 15200 cents.",
    flag_twins=["lotus-cairn", "nettle-strand"],
    ambiguity="none: the signatures for a personal change of departure place are missing; the text is clear")

scenario(
    "magpie-hollow", "flag", ["approval_required", "synonym"], DEROGATION_REQUEST,
    commissioner("Nathalie Girard", "Requested: travel in the same class as the Member of the Commission accompanied, "
                 "for overriding service-related reasons (briefing on board).", "PENDING"),
    DEROGATION_SEARCH,
    expected("FLAG_FOR_APPROVAL", ["af-business"], ["BUSINESS"], ["ACCOMPANYING_MEMBER_CLASS", "APPROVAL_REQUIRED"],
             ["AUTHORISING_OFFICER"], ["AIR_TRAVEL", "ROLES"]),
    [DEROGATION, AO_DEROGATION, TIER_THREE],
    "Business on a 110-minute flight needs the derogation of 733-735 ('may be authorised'), which the authorising "
    "officer approves (291-295); it is requested, not decided. Hold the Commissioner's business seat.",
    flag_twins=["falcon-mere", "zephyr-knoll"],
    ambiguity="none: the authorising officer's derogation is awaited; the text is clear")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.glob("*.json"):
        path.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios")


if __name__ == "__main__":
    main()
