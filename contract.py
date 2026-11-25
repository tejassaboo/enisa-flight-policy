"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-enisa-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    AIR_AUTHORISED_RAIL_DISTANCE = "AIR_AUTHORISED_RAIL_DISTANCE"
    AIR_COST_EFFICIENT = "AIR_COST_EFFICIENT"
    AIR_NOT_AUTHORISED = "AIR_NOT_AUTHORISED"
    BUSINESS_SEGMENT_QUALIFIES = "BUSINESS_SEGMENT_QUALIFIES"
    FLEXIBLE_FARE_CHANGE_RISK = "FLEXIBLE_FARE_CHANGE_RISK"
    FLEXIBLE_FARE_NOT_JUSTIFIED = "FLEXIBLE_FARE_NOT_JUSTIFIED"
    DIRECT_FLIGHT_PREFERRED = "DIRECT_FLIGHT_PREFERRED"
    DIRECT_FLIGHT_REFUSED = "DIRECT_FLIGHT_REFUSED"
    MEETING_TIMES = "MEETING_TIMES"
    TRAVEL_HOURS_PROTECTED = "TRAVEL_HOURS_PROTECTED"
    TRAVEL_HOURS_DECISION = "TRAVEL_HOURS_DECISION"
    ACCOMPANYING_MEMBER_CLASS = "ACCOMPANYING_MEMBER_CLASS"
    LEAVE_PLACE_DEPARTURE = "LEAVE_PLACE_DEPARTURE"
    PERSONAL_CHANGE_AUTHORISED = "PERSONAL_CHANGE_AUTHORISED"
    TRANSPORT_PAID_BY_ORGANISER = "TRANSPORT_PAID_BY_ORGANISER"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    WEEKEND_TRAVEL_HOME = "WEEKEND_TRAVEL_HOME"
    WEEKEND_TRIP_NOT_EARNED = "WEEKEND_TRIP_NOT_EARNED"
    NEXT_OF_KIN_TRAVEL = "NEXT_OF_KIN_TRAVEL"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    CANDIDATE_TRIP_NOT_COVERED = "CANDIDATE_TRIP_NOT_COVERED"
    AIRLINE_CREDIT_MUST_BE_USED = "AIRLINE_CREDIT_MUST_BE_USED"
    CONNECTION_SAVINGS_REQUIRED = "CONNECTION_SAVINGS_REQUIRED"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: ENISA Management Board Decision MB/2018/6, applying the Commission's Guide to missions
# and authorised travel (C(2017) 5323) by analogy to ENISA staff.
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    LINDEN_HARBOUR = "linden-harbour"
    COBALT_RIDGE = "cobalt-ridge"
    SAFFRON_DUNE = "saffron-dune"
    HEATHER_QUAY = "heather-quay"
    WILLOW_CREST = "willow-crest"
    PEBBLE_MOOR = "pebble-moor"
    GARNET_SOUND = "garnet-sound"
    TAMARIND_GATE = "tamarind-gate"
    OCHRE_VALE = "ochre-vale"
    QUARTZ_FELL = "quartz-fell"
    JUNIPER_BAY = "juniper-bay"
    MARIGOLD_TOR = "marigold-tor"
    EMBER_WHARF = "ember-wharf"
    SORREL_HEATH = "sorrel-heath"
    ASPEN_LOCH = "aspen-loch"
    FALCON_MERE = "falcon-mere"
    INDIGO_BRAE = "indigo-brae"
    KESTREL_PLAIN = "kestrel-plain"
    LOTUS_CAIRN = "lotus-cairn"
    NETTLE_STRAND = "nettle-strand"
    ROWAN_SEDGE = "rowan-sedge"
    UMBER_GLEN = "umber-glen"
    VIOLET_SHOAL = "violet-shoal"
    YARROW_POINT = "yarrow-point"
    ZEPHYR_KNOLL = "zephyr-knoll"
    BRAMBLE_ISLE = "bramble-isle"
    CEDAR_FJORD = "cedar-fjord"
    DAHLIA_SPUR = "dahlia-spur"
    FENNEL_ROCK = "fennel-rock"
    HAZEL_TIDE = "hazel-tide"
    IRIS_BLUFF = "iris-bluff"
    MAGPIE_HOLLOW = "magpie-hollow"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    LINE_MANAGER = "LINE_MANAGER"
    AUTHORISING_OFFICER = "AUTHORISING_OFFICER"
    PMO = "PMO"
    MISSIONS_OFFICER = "MISSIONS_OFFICER"
    DG_HR = "DG_HR"
    MEDICAL_SERVICE = "MEDICAL_SERVICE"
    EXECUTIVE_DIRECTOR = "EXECUTIVE_DIRECTOR"
    HEAD_OF_DELEGATION = "HEAD_OF_DELEGATION"
    TRAVEL_AGENCY = "TRAVEL_AGENCY"


class Clause(Enum):
    """The handbook's sections, by heading."""

    SCOPE = "SCOPE"
    ROLES = "ROLES"
    MISSION_DEFINITION = "MISSION_DEFINITION"
    BOOKING_METHODS = "BOOKING_METHODS"
    MISSION_ORDERS = "MISSION_ORDERS"
    MISSION_ORDER_RULES = "MISSION_ORDER_RULES"
    PERSONAL_CHANGES = "PERSONAL_CHANGES"
    DATE_CHANGES = "DATE_CHANGES"
    LEAVE_INTERRUPTED = "LEAVE_INTERRUPTED"
    TRANSPORT_RULES = "TRANSPORT_RULES"
    DEPARTURE_RETURN = "DEPARTURE_RETURN"
    TRANSPORT_TO_MISSION = "TRANSPORT_TO_MISSION"
    RAIL_TRAVEL = "RAIL_TRAVEL"
    AIR_TRAVEL = "AIR_TRAVEL"
    ACCOMMODATION = "ACCOMMODATION"
    MISSION_DURATION = "MISSION_DURATION"
    ORGANISER_EXPENSES = "ORGANISER_EXPENSES"
    AUTHORISED_TRAVEL = "AUTHORISED_TRAVEL"
    AUTHORISED_TRAVEL_GENERAL = "AUTHORISED_TRAVEL_GENERAL"
    EXTERNAL_EVENTS = "EXTERNAL_EVENTS"
    AUTHORISED_TRAVEL_TRANSPORT = "AUTHORISED_TRAVEL_TRANSPORT"
    TRAVEL_AUTHORISATION_REQUEST = "TRAVEL_AUTHORISATION_REQUEST"
    SECURITY = "SECURITY"


class Passenger(Enum):
    STAFF_MEMBER = "STAFF_MEMBER"
    FAMILY_MEMBER = "FAMILY_MEMBER"


class TravelKind(Enum):
    """What the travel is under the guide's own terms."""

    MISSION = "MISSION"
    AUTHORISED_TRAVEL = "AUTHORISED_TRAVEL"
    PRIVATE_TRIP = "PRIVATE_TRIP"


class Settledness(Enum):
    """How settled the dates and programme of the trip are."""

    FIRM = "FIRM"
    UNSETTLED = "UNSETTLED"


class CostBearer(Enum):
    """Who pays for the ticket, as the signed documents for the trip say."""

    AGENCY = "AGENCY"
    ORGANISER = "ORGANISER"
    TRAVELLER = "TRAVELLER"
    NO_DOCUMENT = "NO_DOCUMENT"


class Role(Enum):
    """The signer's role towards the traveller."""

    LINE_MANAGER = "LINE_MANAGER"
    AUTHORISING_OFFICER = "AUTHORISING_OFFICER"


class Subject(Enum):
    """What a signed document or decision covers."""

    MISSION_ORDER = "MISSION_ORDER"
    AUTHORISATION_TO_TRAVEL = "AUTHORISATION_TO_TRAVEL"
    VALIDATED_LEAVE = "VALIDATED_LEAVE"
    TRAVEL_TIMES = "TRAVEL_TIMES"
    CABIN_DEROGATION = "CABIN_DEROGATION"
    NONSTOP_FLIGHT = "NONSTOP_FLIGHT"
    DEPARTURE_ELSEWHERE = "DEPARTURE_ELSEWHERE"
    REST_PERIOD = "REST_PERIOD"


class Outcome(Enum):
    GRANTED = "GRANTED"
    REFUSED = "REFUSED"
    PENDING = "PENDING"


@dataclass
class Approval(Output):
    signer_name: Annotated[str, "Who signed or decided; for a pending request, who it waits for"]
    signer_title: Annotated[str, "Their job title"]
    role: Annotated[Role, "Their role towards the traveller"]
    subject: Annotated[Subject, "What it covers"]
    outcome: Annotated[Outcome, "GRANTED or REFUSED when decided; PENDING when asked for and not yet decided"]
    wording: Annotated[str, "What it says, word for word"]
    given_on: Annotated[str, "The day it was signed or decided, YYYY-MM-DD; empty while pending"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title, or their relation to the staff member they go with"]
    passenger: Annotated[Passenger, "What the person flying is to the agency"]
    accompanies: Annotated[str, "Who the traveller goes with on this trip, by name and title; empty when nobody"]
    place_of_employment: Annotated[str, "The city where the staff member works, which every trip normally starts from"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where the traveller has to be"]
    travel_date: Annotated[str, "The day to fly, YYYY-MM-DD: the local date at the origin airport"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    travel_kind: Annotated[TravelKind, "What the trip is"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    must_land_by: Annotated[
        str, "The latest local date and time at the destination, YYYY-MM-DD HH:MM, at which the flight can land and the traveller still reach the first meeting; empty when the first meeting is on a later day"
    ]
    settledness: Annotated[Settledness, "How settled the trip's dates and programme are"]
    costs_met_by: Annotated[CostBearer, "Who meets the ticket's cost, as the signed documents say; NO_DOCUMENT when nothing is signed"]
    rail_km: Annotated[
        int, "Length in km of the shortest train route between the city of work and the place the trip goes to, one way; 0 when no train route links them"
    ]
    rail_fare_cents: Annotated[int, "The first-class train ticket for that route, one way, in cents of the search's currency; 0 when no train route"]
    rail_minutes: Annotated[int, "The fastest train's scheduled minutes for that route, one way; 0 when no train route"]
    planned_return: Annotated[str, "How the traveller is to fly back, booked separately, in plain words"]
    planned_return_minutes: Annotated[list[int], "The scheduled minutes of each flight of that planned return, in order"]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    wants_changeable_fare: Annotated[bool, "True when the traveller asks for a fare that can be changed or refunded"]
    prefers_nonstop: Annotated[bool, "True when the traveller asks for a nonstop flight"]
    approvals: Annotated[list[Approval], "Signed documents, decisions and pending requests on file for this trip"]
    notes: Annotated[list[str], "Other facts on file for this trip"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
