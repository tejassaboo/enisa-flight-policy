# ENISA Guide to Missions Flight Policy

**Source of the handbook:** https://enisa.europa.eu/sites/default/files/all_files/MB_Decision_No_2018_6_on_missions_guide.pdf. The agent reads it verbatim (bundled at `src/plugin/data/policy.txt`); flights, fares and trips are synthetic.

**No affiliation with ENISA or the European Commission.** The handbook is ENISA Management Board Decision
MB/2018/6, which applies the Commission's *Guide to missions and authorised travel* (Commission Decision
C(2017) 5323) by analogy to ENISA staff; it is a public EU agency decision, bundled verbatim for research. Treat it
like the other original handbooks: do not publish this plugin before the course staff confirm that a verbatim
handbook may be redistributed (MASTER_PLAN section 4).

A `nanoagent.plugin/v0001` plugin. An agent handles one staff member's flight request under the agency's real
guide to missions: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE**
or **FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and guide section. A deterministic Python
verifier, with no LLM, rebuilds the offers and the guide's answer itself and checks every field. Fares are in
euro cents. Built from the original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py`
writes the scenario files (the JSON files are the truth).

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 14,137 words, 1,247 lines, sha256 `47a8fee4...8c6fc9`, equal to
`pilot_work/originals/eu-enisa-missions/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no
rule. Its PDF extraction left about 45 split words ("to tal", "w ould") and a private-use bullet glyph; they are kept,
and `must_keep` quotes copy them as they are. Under stock NanoAgent the agent does not see the text: the plugin
then runs as the `off` baseline. The `harness.policy` switch of the NanoAgent fork
(github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system prompt: `harness.policy: full`
adds all of it, and the selection methods add parts of it. These plugins are meant to run with
`query: instructions+input`, so a selector sees the traveller's request.

**The rules it tests** (all in section 2.4 and around it): air is automatically authorised when rail out and back
would total at least 800 km, and for shorter distances only when cost-efficient (lines 710-712); economy at the
lowest available rates, taking meeting times into account (723-726); flexible economy only with an appreciable
risk of cancellation or amendment (727-729); business when the outward or return journey includes a segment of at
least four hours' continuous flying (730-732); the class of an accompanied Member of the Commission by derogation
(733-735); direct flights normally preferred unless the authorising officer refuses a manifestly unreasonable one
(719-722); no required take-off before 08:00 or landing after 22:00 without the line manager's ad hoc decision
(650-655); departures from a place of leave (614-621) or, for personal reasons, from elsewhere with authorisation
(440-443, 486-496, 672-678); and the scope of missions and authorised travel (212-220, 384-387, 1111-1191).

**Duration.** `rules.over("business-segment", offer)` is true when any segment's scheduled minutes reach 240
(per segment, inclusive; a layover breaks the continuous flying). `rules.over("tiring-journey", offer)` codes the
rest-period threshold of lines 862-863 (flights' minutes added; unclear when only the elapsed time reaches 600);
it changes no ticket and appears only as a distractor.

**Size.** At 1.33 tokens a word the handbook alone is about 18,800 tokens (about 23,000 at 4 characters a token).
Under `full` the first call carries about 21,000 input tokens (handbook, task instructions about 330, tool and
submit schemas about 1,800, the request), and later calls about 22,000-23,000 as tool results accumulate. A run
makes 3 calls (`get_trip`, `search_flights`, `submit`): about 65,000 input tokens, at the hosted cap of 65,536;
at 4 characters a token it is about 77,000 and over. `lotus-cairn` and `iris-bluff` may add the comparison
search (4 calls, about 87,000). Run `full` locally with a raised cap.

## Task

- **Input:** `TaskInput`: `scenario` (one of 32 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date (and the comparison route the record
  names, in two cases), then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is shared by every handbook
  plugin and holds codes for rules this handbook lacks, plus decoy codes from other handbooks' rules. Every
  mission booking rests on the mission order signed by the line manager and the authorising officer for
  commitments (lines 449-451), so a BOOK accepts `LINE_MANAGER`, `AUTHORISING_OFFICER` or `NONE` (template
  SYNC_NOTES 4'); a hold accepts only the role(s) it awaits.
- **Success:** every field is one the answer key accepts. Score = fields right / 6.

| Scenario | Category | Expected decision (offer) | Reason | Approver | Clause cited (frozen lines) |
|---|---|---|---|---|---|
| `cobalt-ridge` | easy | BOOK (early-economy; ECONOMY) | AIR_AUTHORISED_RAIL_DISTANCE or LOWEST_FARE or MEETING_TIMES | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or TRANSPORT_TO_MISSION (723-726, 710-712) |
| `heather-quay` | easy | BOOK (ib-flex; ECONOMY) | FLEXIBLE_FARE_CHANGE_RISK | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (727-729, 723-726) |
| `linden-harbour` | easy | BOOK (ib-economy; ECONOMY) | AIR_AUTHORISED_RAIL_DISTANCE or LOWEST_FARE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or TRANSPORT_TO_MISSION (710-712, 723-726, 449-451) |
| `pebble-moor` | easy | BOOK (mid-economy; ECONOMY) | AIR_AUTHORISED_RAIL_DISTANCE or LOWEST_FARE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or TRANSPORT_TO_MISSION (710-712, 723-726) |
| `saffron-dune` | easy | BOOK (kq-business; BUSINESS) | BUSINESS_SEGMENT_QUALIFIES or LONG_FLIGHT_APPROVED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (730-732, 449-451) |
| `willow-crest` | easy | BOOK (kl-saver; ECONOMY) | FLEXIBLE_FARE_NOT_JUSTIFIED or REFUNDABLE_FARE_NOT_ALLOWED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (727-729, 723-726) |
| `ember-wharf` | boundary_twin | BOOK (eve-economy; ECONOMY) | AIR_AUTHORISED_RAIL_DISTANCE or LOWEST_FARE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or DEPARTURE_RETURN or TRANSPORT_TO_MISSION (650-655, 723-726) |
| `garnet-sound` | boundary_twin | BOOK (ms-business; BUSINESS) | BUSINESS_SEGMENT_QUALIFIES or LONG_FLIGHT_APPROVED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (730-732) |
| `juniper-bay` | boundary_twin | BOOK (first-economy; ECONOMY) | AIR_AUTHORISED_RAIL_DISTANCE or LOWEST_FARE or MEETING_TIMES | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or DEPARTURE_RETURN or TRANSPORT_TO_MISSION (650-655, 723-726) |
| `marigold-tor` | boundary_twin | BOOK (second-economy; ECONOMY) | MEETING_TIMES or TRAVEL_HOURS_PROTECTED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or DEPARTURE_RETURN or TRANSPORT_RULES (650-655, 723-726) |
| `ochre-vale` | boundary_twin | BOOK (mid-economy; ECONOMY) | AIR_AUTHORISED_RAIL_DISTANCE or LOWEST_FARE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or TRANSPORT_TO_MISSION (710-712, 723-726) |
| `quartz-fell` | boundary_twin | REFUSE (none; NONE) | AIR_NOT_AUTHORISED or DISTANCE_BELOW_MINIMUM or RAIL_PREFERRED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or RAIL_TRAVEL or TRANSPORT_TO_MISSION (710-712, 700-701) |
| `sorrel-heath` | boundary_twin | BOOK (ib-economy; ECONOMY) | TRAVEL_HOURS_PROTECTED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or DEPARTURE_RETURN or TRANSPORT_RULES (650-655, 723-726) |
| `tamarind-gate` | boundary_twin | BOOK (ms-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (730-732, 723-726) |
| `aspen-loch` | multi_rule | BOOK (dawn-economy; ECONOMY) | LOWEST_FARE or MEETING_TIMES or TRAVEL_HOURS_DECISION | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or DEPARTURE_RETURN (650-655, 723-726) |
| `falcon-mere` | multi_rule | BOOK (af-business; BUSINESS) | ACCOMPANYING_MEMBER_CLASS | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or ROLES (733-735, 291-295, 730-732) |
| `indigo-brae` | multi_rule | BOOK (tk-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or DIRECT_FLIGHT_REFUSED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (719-722, 723-726) |
| `kestrel-plain` | multi_rule | BOOK (tk-am-business; BUSINESS) | BUSINESS_SEGMENT_QUALIFIES or LONG_FLIGHT_APPROVED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (730-732) |
| `lotus-cairn` | multi_rule | BOOK (pm-economy; ECONOMY) | LOWEST_FARE or PERSONAL_CHANGE_AUTHORISED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or DEPARTURE_RETURN or MISSION_ORDER_RULES or PERSONAL_CHANGES (672-678, 486-490, 491-495, 440-443) |
| `nettle-strand` | hidden_clause | BOOK (ib-economy; ECONOMY) | LEAVE_PLACE_DEPARTURE or LOWEST_FARE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or DEPARTURE_RETURN or LEAVE_INTERRUPTED (614-616, 617-621, 723-726) |
| `rowan-sedge` | hidden_clause | BOOK (lx-economy; ECONOMY) | AIR_COST_EFFICIENT or LOWEST_FARE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL or RAIL_TRAVEL or TRANSPORT_TO_MISSION (710-712, 700-701, 723-726) |
| `umber-glen` | hidden_clause | BOOK (tk-am-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (730-732, 723-726) |
| `violet-shoal` | distractor | BOOK (af-economy; ECONOMY) | DIRECT_FLIGHT_PREFERRED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (719-722) |
| `yarrow-point` | distractor | BOOK (sq-business; BUSINESS) | BUSINESS_SEGMENT_QUALIFIES or LONG_FLIGHT_APPROVED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (730-732) |
| `zephyr-knoll` | distractor | BOOK (ib-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | AUTHORISING_OFFICER or LINE_MANAGER or NONE | AIR_TRAVEL (730-732, 723-726) |
| `bramble-isle` | refusal | REFUSE (none; NONE) | OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED | NONE | MISSION_DEFINITION or SCOPE (212-213, 218-220, 384-387) |
| `cedar-fjord` | refusal | REFUSE (none; NONE) | COMPANION_NOT_COVERED or PERSONAL_TRAVEL_NOT_COVERED | AUTHORISING_OFFICER or LINE_MANAGER or NONE | MISSION_DEFINITION or ROLES or SCOPE (212-213, 239-241, 218-220) |
| `dahlia-spur` | refusal | REFUSE (none; NONE) | DOUBLE_BOOKING_PROHIBITED or TRANSPORT_PAID_BY_ORGANISER | LINE_MANAGER or NONE | AUTHORISED_TRAVEL or AUTHORISED_TRAVEL_GENERAL or AUTHORISED_TRAVEL_TRANSPORT or EXTERNAL_EVENTS or ORGANISER_EXPENSES or TRAVEL_AUTHORISATION_REQUEST (1111-1112, 1172-1176, 1189-1191) |
| `fennel-rock` | flag | FLAG_FOR_APPROVAL (kl-economy, tk-economy; ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | AUTHORISING_OFFICER or NOT_NAMED | AIR_TRAVEL (719-722, 723-726) |
| `hazel-tide` | flag | FLAG_FOR_APPROVAL (tk-business, tk-economy; BUSINESS or ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | AUTHORISING_OFFICER or LINE_MANAGER or NOT_NAMED | AIR_TRAVEL (730-732) |
| `iris-bluff` | flag | FLAG_FOR_APPROVAL (pm-economy; ECONOMY) | APPROVAL_REQUIRED | AUTHORISING_OFFICER or LINE_MANAGER | DEPARTURE_RETURN or MISSION_ORDER_RULES or PERSONAL_CHANGES (672-678, 486-490, 440-443) |
| `magpie-hollow` | flag | FLAG_FOR_APPROVAL (af-business; BUSINESS) | ACCOMPANYING_MEMBER_CLASS or APPROVAL_REQUIRED | AUTHORISING_OFFICER | AIR_TRAVEL or ROLES (733-735, 291-295, 730-732) |

Mix (EDGE_CASES.md 5.2, 32-scenario row): 6 easy, 8 boundary twins, 5 multi-rule, 3 hidden clause or synonym, 3
distractor, 3 refusal, 4 flags (12.5%). Decisions: 24 BOOK, 4 REFUSE, 4 FLAG_FOR_APPROVAL. Boundary twins:
nonstops of 240 against 235 scheduled minutes (`garnet-sound`, `tamarind-gate`); rail of 400 against 395 km each
way, so 800 against 790 out and back (`ochre-vale`, `quartz-fell`); a take-off at 08:00 against 07:55
(`juniper-bay`, `marigold-tor`); a landing at 22:00 against 22:05 (`ember-wharf`, `sorrel-heath`). The pair
`heather-quay` / `willow-crest` differs only in whether the meeting may still move. Unclear-text flags: "manifestly
unreasonable expense" (`fennel-rock`; twins `indigo-brae`, `violet-shoal`) and "if the outward or return journey
includes" (`hazel-tide`; twins `garnet-sound`, `tamarind-gate`). Approval holds: a departure from Zurich for
personal reasons without its signatures (`iris-bluff`; twins `lotus-cairn`, `nettle-strand`) and the
accompanied-Commissioner derogation still pending (`magpie-hollow`; twins `falcon-mere`, `zephyr-knoll`).

Degenerate agents: one that always holds the right offer as unclear passes the 2 unclear holds; one that always
books the cheapest seat with `LOWEST_FARE` and approver `NONE` passes 6 (18.75%): `linden-harbour`, `pebble-moor`,
`ochre-vale`, `ember-wharf`, `nettle-strand` and `rowan-sedge`, whose answer is the lowest seated fare and which
decline nothing the traveller asked for. A BOOK that declines what the traveller asked for (cabin, fare type,
nonstop) accepts only the reason codes for the guide's ground of declining, as the task instructions say.

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats, scheduled times as take-off and landing) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller and city of work, route and date, purpose and who pays, how settled the trip is, the train alternative, the planned way back, the cabin, fare type and routing asked for, signed documents, decisions and pending requests, notes | `src/plugin/tools.py` |
| `search_flights` | Every one-way offer on a route and local date: the pinned scenario offers; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-enisa-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this handbook's scenario ids, approvers, sections and trip record.
- `src/plugin/`: `world.py` (the simulated world: real airports and airline hubs, distance-based times
  and fares, opaque offer ids), `scenarios.py`, `guide.py`, `answer.py`, `tools.py`, `rules.py` (this
  handbook's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of `world.py`, `scenarios.py`, `guide.py`, `answer.py` and
  `rules.py`, plus `booking.py` (`verify_task`) and `tools.py` (`verify_input`, `verify_output`).
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this handbook's settings;
  `tests/build_scenarios.py` writes the scenario files.
- `tests/BUILD_NOTES.md`: build decisions, check outputs and the blind read.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 tests/build_scenarios.py   # rewrites src/plugin/data/scenarios/*.json
# from a NanoAgent checkout (stock NanoAgent runs this plugin as the `off` baseline;
# the fork's `harness.policy: full` flag adds the handbook):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/enisa-flight-policy.tar.gz
<nanoagent>/.venv/bin/python ../_template/tools/stock_verify.py
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
