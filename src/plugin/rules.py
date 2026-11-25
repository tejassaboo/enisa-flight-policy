"""The answer key's rules for ENISA Management Board Decision MB/2018/6, which applies the Commission's Guide to
missions and authorised travel (C(2017) 5323) by analogy to ENISA staff, as exact integer code. Byte-identical
in src/plugin/rules.py and verifier/rules.py; it imports only modules a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. Business class needs an outward or return journey that "includes at least one segment
involving at least four hours' continuous flying time" (lines 730-732): measured per segment, on scheduled
minutes, inclusive; a layover breaks the continuous flying, so two shorter flights never add up. The guide's
other duration threshold, "the total duration of the flights is at least ten hours (tiring journey)" (lines
862-863), allows a rest period and changes no ticket; it is coded for completeness (flights' minutes added,
ground time left out; unclear when only the elapsed journey reaches it).

Approvers (template SYNC_NOTES 4'): every mission booking rests on the mission order signed by the line
manager and the authorising officer for commitments (lines 449-451), so a BOOK accepts both roles and NONE; a
hold awaiting a sign-off accepts only the awaited roles; a refusal accepts NONE beside any sign-off on file that
it does not use.
"""

from contract import (
    Approver,
    Cabin,
    Clause,
    CostBearer,
    Decision,
    Outcome,
    Passenger,
    ReasonCode,
    Role,
    Settledness,
    Subject,
    TravelKind,
)

from .world import clock_minutes

HANDBOOK = "ENISA MB Decision MB/2018/6: Commission Guide to missions and authorised travel, C(2017) 5323"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.SCOPE: "1.1. Scope",
    Clause.ROLES: "1.2. Roles2",
    Clause.MISSION_DEFINITION: "2.1. Definition",
    Clause.BOOKING_METHODS: "2.2.1.2. Booking methods",
    Clause.MISSION_ORDERS: "2.2.2. Mission orders",
    Clause.MISSION_ORDER_RULES: "2.2.2.1. General rules",
    Clause.PERSONAL_CHANGES: "2.2.2.4. Changes made for personal reasons",
    Clause.DATE_CHANGES: "2.3.1.2. Changes to the dates of the mission",
    Clause.LEAVE_INTERRUPTED: "2.3.2.3. Leave interrupted by a mission",
    Clause.TRANSPORT_RULES: "2.4. Rules on transport",
    Clause.DEPARTURE_RETURN: "2.4.1. Departure / return",
    Clause.TRANSPORT_TO_MISSION: "2.4.4. Transport between the place of employment and the place of the mission",
    Clause.RAIL_TRAVEL: "2.4.4.1. Travel by rail",
    Clause.AIR_TRAVEL: "2.4.4.2. Travel by air",
    Clause.ACCOMMODATION: "2.5. Rules on accommodation",
    Clause.MISSION_DURATION: "2.6.1. Duration of the mission",
    Clause.ORGANISER_EXPENSES: "2.9. Expenses paid by organisers; accommodation and meals provided by others",
    Clause.AUTHORISED_TRAVEL: "3. AUTHORISED TRAVEL",
    Clause.AUTHORISED_TRAVEL_GENERAL: "3.1. General rules",
    Clause.EXTERNAL_EVENTS: "3.3. Participation in other external events",
    Clause.AUTHORISED_TRAVEL_TRANSPORT: "3.3.3. Rules on transport",
    Clause.TRAVEL_AUTHORISATION_REQUEST: "3.4.1.1. Request for authorisation to travel",
    Clause.SECURITY: "4.3. Security",
}

# The handbook's duration thresholds (the per-handbook duration hook; tests/test_duration.py tests both sides
# of each). operator ">=" is inclusive ("at least").
DURATION_RULES = (
    {"name": "business-segment", "minutes": 240, "operator": ">=", "lines": [730, 732],
     "quote": "at least one segment involving at least four hours' continuous flying time"},
    {"name": "tiring-journey", "minutes": 600, "operator": ">=", "lines": [862, 863],
     "quote": "if the total duration of the flights is at least ten hours (tiring journey)"},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's.
CONVENTIONS = ("Each flight's scheduled times are the moments it takes off and lands.",)

# Lines 710-711: air is automatically authorised "if the outward and return journeys by rail would to tal at
# least 800 kilometres" (inclusive; both journeys added).
RAIL_TOTAL_KM = 800
# Lines 650-655: a staff member "cannot be required to leave before 8:00 or arrive after 22:00" (both strict),
# take-off and landing local at the place of employment and at the place of the mission.
EARLIEST_MINUTE, LATEST_MINUTE = 8 * 60, 22 * 60
# Lines 719-722: the authorising officer "may refuse to authorise a direct flight if it w ould represent a
# manifestly unreasonable expense". With no refusal on file, a nonstop at most 1.5 times the connecting fare is
# plainly not manifestly unreasonable; at three times or more the words leave the answer open; between is not
# modelled.
DIRECT_CLEAR_PERCENT, DIRECT_UNCLEAR_PERCENT = 150, 300

DIRECT_PHRASE = "manifestly unreasonable expense"
JOURNEY_PHRASE = "if the outward or return journey includes"
# Who may resolve a gap in the air rules: the authorising officer for commitments approves the practical
# arrangements and any derogation (lines 291-295) and decides on a direct flight (lines 719-722); the line
# manager checks arrangements against the guide (lines 258-260); NOT_NAMED since no clause names a role for the
# gap itself.
GAP_APPROVERS = [Approver.NOT_NAMED, Approver.AUTHORISING_OFFICER, Approver.LINE_MANAGER]
SIGNERS = [Approver.AUTHORISING_OFFICER, Approver.LINE_MANAGER]
ROLE_APPROVER = {Role.LINE_MANAGER: Approver.LINE_MANAGER, Role.AUTHORISING_OFFICER: Approver.AUTHORISING_OFFICER}
UNCLEAR_REASONS = [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED]
AIR = [Clause.AIR_TRAVEL, Clause.TRANSPORT_TO_MISSION]


def over(rule, offer):
    """True, False or None (unclear): whether ``offer`` reaches the handbook's ``rule`` duration."""
    limit = LIMITS[rule]
    if rule == "business-segment":
        return any(segment.scheduled_minutes >= limit for segment in offer.segments)
    if offer.flying_minutes >= limit:
        return True
    if offer.elapsed_minutes < limit:
        return False
    return None


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def one(offers, what):
    if len(offers) != 1:
        raise ValueError(f"{len(offers)} offers tie for {what}; a scenario gives exactly one")
    return offers[0]


def records(trip, subject, outcome=None):
    return [record for record in trip.approvals if record.subject == subject
            and (outcome is None or record.outcome == outcome)]


def roles(trip, subject, outcome=Outcome.GRANTED):
    return {ROLE_APPROVER[record.role] for record in records(trip, subject, outcome)}


def roles_on_file(trip):
    return [ROLE_APPROVER[record.role] for record in trip.approvals if record.outcome == Outcome.GRANTED]


def refuse(trip, reasons, clauses, why):
    """A refusal relies on no sign-off; a sign-off on file goes unused (SYNC_NOTES 4(b))."""
    return answer(Decision.REFUSE, [], reasons, [Approver.NONE, *roles_on_file(trip)], clauses, why)


def booked(offers, reasons, clauses, why):
    """A BOOK rests on the mission order signed by both roles (lines 449-451) and any special sign-off they
    gave: both roles and NONE are accepted (SYNC_NOTES 4'). A BOOK that declines what the traveller asked for
    accepts only the codes for the ground of declining, not LOWEST_FARE."""
    return answer(Decision.BOOK, offers, reasons, [*SIGNERS, Approver.NONE], clauses, why)


def minute_of(text):
    return clock_minutes(text[11:])


def within_hours(offer):
    """Lines 650-655: take-off not before 08:00 and landing not after 22:00, local time at each end. A landing
    after midnight on a later local date is not modelled (whether it is "after 22:00" is left open)."""
    first, last = offer.segments[0], offer.segments[-1]
    land = minute_of(last.arrive_local)
    if last.arrive_local[:10] != first.depart_local[:10] and land < 6 * 60:
        raise ValueError("a landing between midnight and 06:00 is not modelled")
    return minute_of(first.depart_local) >= EARLIEST_MINUTE and land <= LATEST_MINUTE


def lands_in_time(trip, offer):
    return not trip.must_land_by or offer.segments[-1].arrive_local <= trip.must_land_by


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers of its pinned searches: the decision, and every accepted
    offer id, cabin, reason, approver and section. ``hidden`` (answer_key_inputs) is unused here."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if trip.passenger == Passenger.FAMILY_MEMBER:
        return refuse(trip, [ReasonCode.COMPANION_NOT_COVERED, ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                      [Clause.SCOPE, Clause.ROLES, Clause.MISSION_DEFINITION],
                      "Lines 212-213 and 239-241: the guide covers missions and authorised travel of the person "
                      "concerned, a staff member; a mission is travel 'solely in the interests of the service' "
                      "(lines 384-385). A relative joining a mission is neither, so the agency buys no ticket.")
    if trip.travel_kind == TravelKind.PRIVATE_TRIP:
        return refuse(trip, [ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      [Clause.SCOPE, Clause.MISSION_DEFINITION],
                      "Lines 212-213, 218-220 and 384-387: the guide covers missions, travel solely in the "
                      "interests of the service under a mission order, and authorised travel under an "
                      "authorisation to travel. A private holiday is neither, so the agency buys no ticket.")
    if trip.travel_kind == TravelKind.AUTHORISED_TRAVEL:
        return authorised(trip)
    if trip.costs_met_by != CostBearer.AGENCY:
        raise ValueError("a mission whose ticket the agency does not pay is not modelled")
    if roles(trip, Subject.MISSION_ORDER) != set(SIGNERS):
        raise ValueError("a mission without its order signed by both roles is not modelled (lines 449-451)")
    return mission(trip, offers)


def authorised(trip):
    """Lines 1111-1112: the organiser may meet the transport costs; lines 1174-1175 and 1189-1191: the
    authorisation says who meets each cost, and the traveller may incur expenses only within its limits."""
    if trip.costs_met_by != CostBearer.ORGANISER or not roles(trip, Subject.AUTHORISATION_TO_TRAVEL):
        raise ValueError("only authorised travel with the organiser paying the transport is modelled")
    return refuse(trip, [ReasonCode.TRANSPORT_PAID_BY_ORGANISER, ReasonCode.DOUBLE_BOOKING_PROHIBITED],
                  [Clause.AUTHORISED_TRAVEL_TRANSPORT, Clause.TRAVEL_AUTHORISATION_REQUEST, Clause.EXTERNAL_EVENTS,
                   Clause.AUTHORISED_TRAVEL_GENERAL, Clause.AUTHORISED_TRAVEL, Clause.ORGANISER_EXPENSES],
                  "Lines 1111-1112: the organiser may meet the transport costs of authorised travel; the signed "
                  "authorisation says the organiser meets them and the agency none (lines 1174-1175), and the "
                  "traveller may incur expenses only within its limits (lines 1189-1191). The organiser's ticket is "
                  "already issued, so the agency buys no second ticket.")


def mission(trip, offers):
    """A mission: the place it leaves from, whether air is authorised at all, then the class, fare type and
    routing rules of section 2.4.4.2, each among the offers the traveller can be required to take."""
    by_origin = [offer for offer in offers if offer.segments[0].origin == trip.origin.code]
    others = [offer for offer in offers if offer not in by_origin]
    if trip.origin.city not in trip.place_of_employment:
        return elsewhere(trip, by_origin, others)
    if others:
        raise ValueError("a comparison search on a trip from the place of employment is not modelled")
    return from_home(trip, offers, [], [])


def elsewhere(trip, offers, comparison):
    """A departure from somewhere other than the place of employment: from the place of validated leave
    (lines 614-621) it needs nothing more; for personal reasons it needs the authorising officer's
    authorisation (lines 672-678) and the line manager's and authorising officer's ad hoc signatures (lines
    440-443), with a cost comparison and any extra cost met by the traveller (lines 486-496)."""
    leave = roles(trip, Subject.VALIDATED_LEAVE)
    if leave:
        if comparison or records(trip, Subject.DEPARTURE_ELSEWHERE):
            raise ValueError("a leave departure with a personal-change record is not modelled")
        return from_home(trip, offers, [ReasonCode.LEAVE_PLACE_DEPARTURE],
                         [Clause.LEAVE_INTERRUPTED, Clause.DEPARTURE_RETURN],
                         "Lines 614-616 and 620-621: the mission falls on validated leave, so the traveller may keep "
                         "the leave and depart on mission from the place where they are on leave; the signed "
                         "mission order validates it (lines 617-619).")
    if not comparison:
        raise ValueError("a personal-reasons departure without the cost comparison search is not modelled")
    signed = roles(trip, Subject.DEPARTURE_ELSEWHERE)
    clauses = [Clause.PERSONAL_CHANGES, Clause.DEPARTURE_RETURN, Clause.MISSION_ORDER_RULES]
    if signed == set(SIGNERS):
        return from_home(trip, offers, [ReasonCode.PERSONAL_CHANGE_AUTHORISED], clauses,
                         "Lines 672-678: the authorising officer may authorise a departure from another place for "
                         "personal reasons, under section 2.2.2.4 (lines 486-496: a cost comparison, any extra cost "
                         "met by the traveller); the line manager's and authorising officer's ad hoc signatures for a "
                         "change for personal reasons are on file (lines 440-443).")
    if signed or records(trip, Subject.DEPARTURE_ELSEWHERE, Outcome.REFUSED):
        raise ValueError("a partly signed or refused personal departure is not modelled")
    held = cheapest_in_rules(trip, offers)
    return answer(Decision.FLAG_FOR_APPROVAL, [held], [ReasonCode.APPROVAL_REQUIRED], SIGNERS, clauses,
                  "Lines 672-678: a departure from a place other than the place of employment for personal reasons "
                  "needs the authorising officer's authorisation, and lines 440-443 need the line manager's and the "
                  "authorising officer's ad hoc signatures for a change for personal reasons. Neither is on file: "
                  "hold the lowest fare from that place.")


def cheapest_in_rules(trip, offers):
    usable = [offer for offer in offers if offer.seats_available and offer.cabin == Cabin.ECONOMY
              and not offer.refundable and within_hours(offer) and lands_in_time(trip, offer)]
    return one(cheapest(usable), "the lowest usable economy fare")


def air_allowed(trip, offers):
    """Lines 710-712: air is automatically authorised when rail out and back would total at least 800 km; for
    shorter distances only when justified on grounds of cost-efficiency (the flight costs less than the
    first-class rail fare that would be reimbursed, lines 700-701). Returns (allowed, reason) or raises."""
    if trip.rail_km == 0:
        return True, None
    if 2 * trip.rail_km >= RAIL_TOTAL_KM:
        return True, ReasonCode.AIR_AUTHORISED_RAIL_DISTANCE
    low = cheapest_in_rules(trip, offers)
    if low.fare_cents < trip.rail_fare_cents:
        return True, ReasonCode.AIR_COST_EFFICIENT
    if low.fare_cents * 3 < trip.rail_fare_cents * 4:
        raise ValueError("a short trip whose flight costs only a little more than the train is not modelled")
    return False, None


def from_home(trip, offers, extra, clauses, why=""):
    """The air rules for the mission's own flight. ``extra``, ``clauses`` and ``why`` carry a departure
    rule's grounds (leave, a personal change) into the booking."""
    allowed, rail_reason = air_allowed(trip, offers)
    if not allowed:
        if extra:
            raise ValueError("a refused flight from another departure place is not modelled")
        return refuse(trip, [ReasonCode.AIR_NOT_AUTHORISED, ReasonCode.RAIL_PREFERRED, ReasonCode.DISTANCE_BELOW_MINIMUM],
                      [Clause.AIR_TRAVEL, Clause.RAIL_TRAVEL, Clause.TRANSPORT_TO_MISSION],
                      f"Lines 710-712: rail out and back totals {2 * trip.rail_km} km, under 800, so air is not "
                      "automatically authorised; it is permitted for shorter distances only when justified on "
                      "grounds of cost-efficiency, and the lowest fare costs more than the first-class rail fare "
                      "(lines 700-701). The agency buys no flight.")
    rail = [rail_reason] if rail_reason else []
    seated = [offer for offer in offers if offer.seats_available]
    decisions = roles(trip, Subject.TRAVEL_TIMES)
    timed = [offer for offer in seated if lands_in_time(trip, offer)]
    usable = timed if decisions else [offer for offer in timed if within_hours(offer)]
    late = [offer for offer in seated if not lands_in_time(trip, offer) and offer.cabin == Cabin.ECONOMY]
    if late and not any(offer.fare_cents < min(o.fare_cents for o in usable) for offer in late):
        raise ValueError("an arrival limit that rules out no cheaper flight is not modelled")
    meeting = [ReasonCode.MEETING_TIMES] if late else []
    if trip.requested_cabin == Cabin.BUSINESS:
        if trip.wants_changeable_fare or trip.prefers_nonstop or extra or decisions:
            raise ValueError("a business request with another wish is not modelled")
        return business(trip, usable, rail)
    if trip.requested_cabin != Cabin.ECONOMY:
        raise ValueError(f"a {trip.requested_cabin.value} request is not modelled")
    economy = [offer for offer in usable if offer.cabin == Cabin.ECONOMY]
    plain = [offer for offer in economy if not offer.refundable]
    if trip.wants_changeable_fare:
        if trip.prefers_nonstop or extra or decisions or late:
            raise ValueError("a changeable-fare request with another wish is not modelled")
        return changeable(trip, economy, plain)
    if trip.prefers_nonstop:
        if extra or decisions or late:
            raise ValueError("a nonstop request with another wish is not modelled")
        return nonstop(trip, plain)
    low = one(cheapest(plain), "the lowest economy fare")
    if decisions:
        early = [offer for offer in plain if not within_hours(offer)]
        if low not in early or extra:
            raise ValueError("a travel-times decision that changes nothing is not modelled")
        return booked([low], [ReasonCode.TRAVEL_HOURS_DECISION, ReasonCode.LOWEST_FARE, *meeting],
                      [Clause.DEPARTURE_RETURN, Clause.AIR_TRAVEL],
                      "Lines 650-655: a staff member cannot be required to leave before 8:00 unless the line manager "
                      "adopts an ad hoc decision, giving reasons; that decision is on file, so the lowest fare that "
                      "lands in time for the meeting (lines 724-726) is required, though it leaves before 8:00.")
    protected = [offer for offer in seated if offer.cabin == Cabin.ECONOMY and not offer.refundable
                 and lands_in_time(trip, offer) and not within_hours(offer)]
    if protected and min(offer.fare_cents for offer in protected) < low.fare_cents:
        if extra:
            raise ValueError("a protected travel time from another departure place is not modelled")
        # The traveller's wish is met here (no flight outside the hours), so LOWEST_FARE and the air-authorisation
        # code are fair too: the booking is the lowest fare inside the hours (audit).
        return booked([low], [ReasonCode.TRAVEL_HOURS_PROTECTED, ReasonCode.LOWEST_FARE, *rail, *meeting],
                      [Clause.DEPARTURE_RETURN, Clause.TRANSPORT_RULES, *AIR],
                      "Lines 650-655: a staff member cannot be required to leave before 8:00 or arrive after 22:00 "
                      "(take-off and landing) unless the line manager adopts an ad hoc decision, and none is on "
                      "file. The traveller does not take the cheaper flight outside those hours, so the lowest fare "
                      "inside them.")
    if extra:
        return booked([low], [*extra, ReasonCode.LOWEST_FARE], [*clauses, Clause.AIR_TRAVEL],
                      why + " The lowest economy fare from there (lines 724-726).")
    # The hours clause is also a fair citation when it is what keeps the lowest fare (a take-off at exactly 08:00
    # or a landing at exactly 22:00).
    # TRAVEL_HOURS_PROTECTED is accepted there too: an agent that says the flight lies inside the protected hours
    # cites the right clause, and the offer alone separates it from the twin (audit).
    hours = [Clause.DEPARTURE_RETURN, Clause.TRANSPORT_RULES] if edge_of_hours(low) else []
    reasons = [ReasonCode.LOWEST_FARE, *rail, *meeting]
    if hours:
        reasons.append(ReasonCode.TRAVEL_HOURS_PROTECTED)
    text = "Lines 724-726: economy, including tickets that cannot be exchanged or refunded, at the lowest available "
    text += "rates, taking into account the times of meetings"
    if rail_reason == ReasonCode.AIR_COST_EFFICIENT:
        text += f"; lines 710-712: rail out and back totals {2 * trip.rail_km} km, under 800, but the flight costs " \
                "less than the first-class rail fare, so air is justified on grounds of cost-efficiency"
        return booked([low], reasons, [*AIR, Clause.RAIL_TRAVEL], text + ".")
    if rail_reason:
        text += f"; lines 710-711: rail out and back would total {2 * trip.rail_km} km, at least 800, so air is " \
                "automatically authorised"
    if late:
        text += "; a cheaper flight lands after the traveller must arrive"
    if hours:
        text += "; lines 650-655: a take-off at 8:00 is not before 8:00, and a landing at 22:00 is not after 22:00"
    return booked([low], reasons, [*AIR, *hours], text + ".")


def edge_of_hours(offer):
    """A flight that takes off at exactly 08:00 or lands at exactly 22:00 (the hours clause is what decides it)."""
    return (minute_of(offer.segments[0].depart_local) == EARLIEST_MINUTE
            or minute_of(offer.segments[-1].arrive_local) == LATEST_MINUTE)


def business(trip, usable, rail):
    """Lines 730-732: business class at the lowest available rates if the outward or return journey includes at
    least one segment of at least four hours' continuous flying; lines 733-735: by derogation, the class of the
    Member of the Commission accompanied, if authorised for overriding service-related reasons."""
    seated_business = [offer for offer in usable if offer.cabin == Cabin.BUSINESS]
    economy = [offer for offer in usable if offer.cabin == Cabin.ECONOMY and not offer.refundable]
    derogation = records(trip, Subject.CABIN_DEROGATION)
    if derogation:
        if any(over("business-segment", offer) for offer in usable) or not trip.accompanies:
            raise ValueError("a derogation on a trip that qualifies anyway, or with nobody accompanied, is not modelled")
        held = one(cheapest(seated_business), "the business seat on the accompanied flight")
        clauses = [Clause.AIR_TRAVEL]
        if roles(trip, Subject.CABIN_DEROGATION) == {Approver.AUTHORISING_OFFICER}:
            return booked([held], [ReasonCode.ACCOMPANYING_MEMBER_CLASS], [*clauses, Clause.ROLES],
                          "Lines 733-735: by derogation, staff may be authorised to travel in the same class as the "
                          "Member of the Commission they accompany, for overriding service-related reasons; the "
                          "authorising officer, who approves derogations (lines 291-295), authorised it: business on "
                          "the Member's flight.")
        if [record.outcome for record in derogation] != [Outcome.PENDING] or derogation[0].role != Role.AUTHORISING_OFFICER:
            raise ValueError("a derogation that is neither granted nor pending with the authorising officer is not modelled")
        return answer(Decision.FLAG_FOR_APPROVAL, [held], [ReasonCode.APPROVAL_REQUIRED, ReasonCode.ACCOMPANYING_MEMBER_CLASS],
                      [Approver.AUTHORISING_OFFICER], [*clauses, Clause.ROLES],
                      "Lines 733-735: staff 'may be authorised' to travel in the same class as the Member of the "
                      "Commission they accompany; the flight is short of four hours, so business needs that "
                      "derogation, which the authorising officer approves (lines 291-295) and has not yet decided. "
                      "Hold the business seat on the Member's flight.")
    outward = [offer for offer in seated_business if over("business-segment", offer)]
    long_back = any(minutes >= LIMITS["business-segment"] for minutes in trip.planned_return_minutes)
    if outward:
        if any(not over("business-segment", offer) for offer in usable):
            raise ValueError("a mix of qualifying and non-qualifying routings is not modelled")
        return booked([one(cheapest(outward), "the lowest business fare")],
                      [ReasonCode.BUSINESS_SEGMENT_QUALIFIES, ReasonCode.LONG_FLIGHT_APPROVED], [Clause.AIR_TRAVEL],
                      "Lines 730-732: the outward journey includes a segment of at least four hours' continuous "
                      "flying time (scheduled minutes, inclusive), so business class at the lowest available rate.")
    low = one(cheapest(economy), "the lowest economy fare")
    if long_back:
        held = [one(cheapest(seated_business), "the lowest business fare"), low]
        return answer(Decision.FLAG_FOR_APPROVAL, held, UNCLEAR_REASONS, GAP_APPROVERS, [Clause.AIR_TRAVEL],
                      "Lines 730-732 allow business 'if the outward or return journey includes' a segment of at "
                      "least four hours' continuous flying. The outward flight here has none, but the planned "
                      "return does. One reading lets that return open business class for the trip, the other "
                      "judges each journey by its own segments and books economy.", phrase=JOURNEY_PHRASE)
    multi = any(len(offer.segments) > 1 for offer in economy)
    why = "Lines 730-732: no segment of the outward or the planned return journey reaches four hours' continuous "
    why += "flying time"
    if multi:
        why += " (a layover breaks the flying, so the connecting flights do not add up)"
    return booked([low], [ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET, ReasonCode.UPGRADE_NOT_ELIGIBLE], [Clause.AIR_TRAVEL],
                  why + "; business is not allowed, so economy at the lowest available rate (lines 724-726).")


def changeable(trip, economy, plain):
    """Lines 727-729: economy at the lowest rates for flexible tickets if there is an appreciable risk that the
    mission will be cancelled or amended; otherwise lines 724-726, the lowest fare, which may be one that cannot
    be exchanged or refunded."""
    if trip.settledness == Settledness.UNSETTLED:
        flexible = [offer for offer in economy if offer.refundable]
        return booked([one(cheapest(flexible), "the lowest flexible fare")], [ReasonCode.FLEXIBLE_FARE_CHANGE_RISK],
                      [Clause.AIR_TRAVEL],
                      "Lines 727-729: there is an appreciable risk that the mission will be amended (the record says "
                      "its date may still move), so economy at the lowest available rate for flexible tickets.")
    return booked([one(cheapest(plain), "the lowest economy fare")],
                  [ReasonCode.FLEXIBLE_FARE_NOT_JUSTIFIED, ReasonCode.REFUNDABLE_FARE_NOT_ALLOWED], [Clause.AIR_TRAVEL],
                  "Lines 727-729 allow flexible tickets only if there is an appreciable risk that the mission will be "
                  "cancelled or amended; the mission is firm, so lines 724-726: the lowest fare, including one that "
                  "cannot be exchanged or refunded.")


def nonstop(trip, plain):
    """Lines 719-722: direct flights are normally preferred, but the authorising officer may refuse one that
    would be a manifestly unreasonable expense."""
    direct = one(cheapest([offer for offer in plain if offer.stops == 0]), "the lowest nonstop fare")
    connection = one(cheapest([offer for offer in plain if offer.stops > 0]), "the lowest connecting fare")
    if connection.fare_cents >= direct.fare_cents:
        raise ValueError("a nonstop request where the nonstop is also the lowest fare is not modelled")
    refused = records(trip, Subject.NONSTOP_FLIGHT, Outcome.REFUSED)
    if refused:
        if refused[0].role != Role.AUTHORISING_OFFICER:
            raise ValueError("a nonstop refused by someone other than the authorising officer is not modelled")
        return booked([connection], [ReasonCode.DIRECT_FLIGHT_REFUSED, ReasonCode.ALTERNATE_ROUTE_TOO_EXPENSIVE],
                      [Clause.AIR_TRAVEL],
                      "Lines 719-722: the authorising officer may refuse a direct flight that would represent a "
                      "manifestly unreasonable expense, and has refused this one; the lowest connecting fare.")
    if records(trip, Subject.NONSTOP_FLIGHT):
        raise ValueError("a nonstop record other than a refusal is not modelled")
    ratio = direct.fare_cents * 100
    if ratio <= DIRECT_CLEAR_PERCENT * connection.fare_cents:
        return booked([direct], [ReasonCode.DIRECT_FLIGHT_PREFERRED], [Clause.AIR_TRAVEL],
                      "Lines 719-722: direct flights are normally preferred; the authorising officer has not refused "
                      "this one, and a nonstop this close to the connecting fare is no manifestly unreasonable "
                      "expense: book the nonstop the traveller asks for.")
    if ratio >= DIRECT_UNCLEAR_PERCENT * connection.fare_cents:
        return answer(Decision.FLAG_FOR_APPROVAL, [direct, connection], UNCLEAR_REASONS,
                      [Approver.NOT_NAMED, Approver.AUTHORISING_OFFICER], [Clause.AIR_TRAVEL],
                      "Lines 719-722: direct flights are normally preferred, but the authorising officer may refuse one "
                      "that 'would represent a manifestly unreasonable expense', a term the guide does not define. The "
                      "nonstop costs several times the connection and no decision is on file: one reading books the "
                      "preferred nonstop, the other the connection.", phrase=DIRECT_PHRASE)
    raise ValueError("a nonstop premium between the clear and the unclear bands is not modelled")
