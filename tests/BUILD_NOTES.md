# Build notes: enisa-flight-policy

Wave 3 build of 2026-11-24 (overnight), following `pilot_work/tier_plan/build/WAVE3_BUILD_BRIEF.md`. No paid
calls, no network, no pushes. Decisions were taken without asking, as the brief says; each is recorded here.

## Handbook

- Frozen text: `pilot_work/originals/eu-enisa-missions/frozen/eu-enisa-missions_policy.txt`, 14,137 words, 1,247
  lines, sha256 `47a8fee4...8c6fc9` (raw PDF `60e8e66c...e88`). Over 10,000 words, so 32 scenarios.
- ENISA MB Decision MB/2018/6 applies the Commission's Guide to missions and authorised travel (C(2017) 5323) by
  analogy; the guide is the whole body of the text. Currency EUR; `background_offers: 0`, and every pinned search
  has `"background": 0`.
- Task id `book-enisa-flight` (no digits).
- Extraction defects kept as they are: split words ("to tal", "w ould", "Howeve r") and the private-use bullet glyph.
  Every `must_keep` quote copies the frozen words, split words included; ranges were chosen so that no rule a case
  rests on is garbled beyond reading.

## Which clause decides

| Topic | Clause | Lines |
|---|---|---|
| Air at all | 2.4.4.2: automatic when rail out and back would total at least 800 km; shorter only on grounds of cost-efficiency | 710-712 (rail fare basis 700-701) |
| Default fare | 2.4.4.2 point 1: economy incl. non-exchangeable/non-refundable, lowest available rates, taking meeting times into account | 723-726 |
| Flexible fare | point 2: lowest flexible rate only with an appreciable risk of cancellation or amendment | 727-729 |
| Business | point 3: outward or return journey includes a segment of at least four hours' continuous flying | 730-732 |
| Accompanying a Commissioner | derogation: the Member's class, if authorised; the AO approves derogations | 733-735, 291-295 |
| Direct flights | normally preferred; the AO may refuse a manifestly unreasonable one | 719-722 |
| Travel hours | cannot be required to take off before 8:00 or land after 22:00 without the line manager's ad hoc decision | 650-655 |
| Booking only after signature | final reservations once the AO has signed the mission order | 449-451 |
| Departure elsewhere | from validated leave: allowed (2.3.2.3); for personal reasons: AO authorisation, ad hoc signatures, cost comparison | 614-621; 440-443, 486-496, 672-678 |
| Scope | missions, authorised travel, the person concerned | 212-213, 218-220, 239-241, 384-387 |
| Authorised travel paid by an organiser | organiser may meet transport; the authorisation fixes who pays and the limits | 1111-1112, 1172-1176, 1189-1191 |

## Categories the handbook supports, and what it lacks

- Two duration thresholds: business at a segment of at least 240 minutes (`business-segment`, per segment,
  inclusive) and the rest period at 600 minutes of flights (`tiring-journey`, lines 862-863). The rest period
  changes no ticket; it is coded and tested but used only as a distractor (`yarrow-point`, `kestrel-plain`,
  `umber-glen`).
- No premium economy, no first-class rule, no advance-purchase window (line 663-664 is a soft "should book at the
  earliest opportunity"), no day-count rule: `date_arithmetic` and `month_end` are not in `OVERLAY_MINIMUMS`.
- The return-start rule (3.5 hours after the meeting, lines 656-659) is not tested as a decider: line 861 lets the
  mission be extended "to obtain cheaper travel", and "commenced" can mean take-off or leaving the venue, so a
  same-evening return could not pass the two-reader test without a flag, and the flag quota was used on clearer
  phrases. It appears as a distractor only.
- Low-cost airlines (line 738) cannot be modelled: the shared world has no low-cost carrier. Distractor only.
- No multi-traveller flight rule; `cedar-fjord` (a husband asking to join) carries the overlay.

## Design against the EU Rail guide (another builder)

This guide is the 2017 Commission text: the rail test is a flat 800 km out and back, business needs a segment of
four hours, and there is no premium economy. The scenarios are built around those: the 400/395 km rail twin, the
240/235-minute business twin, connections whose total flying is long but no segment reaches four hours
(`umber-glen`), a connection whose second segment qualifies (`kestrel-plain`), the "outward or return journey"
wording (`hazel-tide`), and the accompanied-Commissioner derogation.

## Decisions taken without asking

1. **Places of employment.** ENISA's own sites (Athens, Heraklion, Brussels) are not in the shared world, so the
   travellers work in Frankfurt, Paris, Madrid, Amsterdam or Munich. The cases are synthetic; see template change
   request 1.
2. **Approvers (SYNC_NOTES 4').** Every mission booking rests on the mission order signed by the line manager and the
   authorising officer (lines 449-451), so every BOOK accepts `AUTHORISING_OFFICER`, `LINE_MANAGER` and `NONE`
   (lesson 1: a BOOK relying on two sign-offs accepts both plus NONE). Refusals accept `NONE` plus any sign-off on
   file that goes unused. Holds accept only the awaited roles: both signers for the personal departure
   (`iris-bluff`), the authorising officer for the derogation (`magpie-hollow`), and NOT_NAMED plus the roles the
   text points to for the two unclear holds.
3. **Unclear holds also accept APPROVAL_REQUIRED** (lesson 2), since each names the authorising officer as the one
   who would resolve it, and each holds the offer of either reading.
4. **Travel hours.** The rule protects the traveller ("cannot be required"), so the cases that test it say the
   traveller does not want an early start or a late landing "unless the guide says I have to"; both twins use the
   same words. An arrival between midnight and 06:00 on a later date raises (`rules.within_hours`): whether it is
   "after 22:00" is left open, and no case has one.
5. **Meeting times.** Same-day cases give `must_land_by` and say it in the request (lesson 4); every other case has
   its first meeting the next day or later.
6. **Cost-efficiency below 800 km** is read as the flight costing less than the first-class rail fare the guide would
   otherwise reimburse (lines 700-701). Both cases are far from the line: 9600 against 14800 cents
   (`rowan-sedge`, book) and 21200 against 12900 (`quartz-fell`, refuse); `rules.air_allowed` raises for a flight
   within a third above the rail fare.
7. **Direct flights.** With no refusal on file, a nonstop at most 1.5 times the connection is booked
   (`violet-shoal`, 1.16x); at three times or more the words are open (`fennel-rock`, 3.7x); between is not modelled.
   With the authorising officer's refusal on file the connection is booked (`indigo-brae`), and LOWEST_FARE is not
   accepted there (the ground is the officer's refusal; lesson 12).
8. **Scheduled times as take-off and landing.** Line 654 measures take-off and landing; the world shows scheduled
   times. A handbook convention (`rules.CONVENTIONS`) says scheduled departure and arrival are the take-off and
   landing moments, so 240 scheduled minutes is four hours' flying.
9. **Decisions.** 24 BOOK, 4 REFUSE, 4 FLAG. The brief asks for about 26 BOOK; the 32-row mix needs 3 refusals and
   4 flags, and the rail twin's short side is itself a refusal, so 24 is the most this mix allows with a twin on
   the 800 km rule.
10. Reason-code decoys (grep of the frozen text found none of their subjects): WEEKEND_TRAVEL_HOME,
    WEEKEND_TRIP_NOT_EARNED, NEXT_OF_KIN_TRAVEL, FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT,
    CREATIVE_TICKETING, CHANCELLOR_WRITTEN_AUTHORIZATION, PRIVATE_AIRCRAFT_NOT_APPROVED, CANDIDATE_TRIP_NOT_COVERED,
    AIRLINE_CREDIT_MUST_BE_USED, CONNECTION_SAVINGS_REQUIRED. DOUBLE_BOOKING_PROHIBITED is not a decoy here: it is a
    fair reason on `dahlia-spur` (the organiser's ticket is already issued) and is accepted there.
11. The first scenario in enum order is a BOOK (`linden-harbour`), so the shared tamper test has something to tamper
    (georgia template change request 1).

## Scenarios (32)

Mix: 6 easy, 8 boundary twins, 5 multi-rule, 3 hidden clause, 3 distractor, 3 refusal, 4 flags (12.5%). Overlays:
multi_leg 5, personal_travel 4, multi_traveller 1, dearer_option 8, upgrade_not_taken 4, outside_air_section 6.

Boundary twins (one fact each): 240/235 scheduled minutes (`garnet-sound`/`tamarind-gate`), 400/395 km of rail one
way (`ochre-vale`/`quartz-fell`), take-off 08:00/07:55 (`juniper-bay`/`marigold-tor`), landing 22:00/22:05
(`ember-wharf`/`sorrel-heath`). Also `heather-quay`/`willow-crest` (the meeting may move, or is confirmed).

Flags and the clauses they test:
- `fennel-rock` (unclear): "manifestly unreasonable expense" (lines 719-722): nonstop 114000 against a 31000
  connection, no decision on file. Holds either. Twins `indigo-brae` (refused: connection), `violet-shoal`
  (small premium: nonstop).
- `hazel-tide` (unclear): "if the outward or return journey includes" (lines 730-732): 160-minute outward
  nonstop, 375-minute planned return. Holds business or economy. Twins `garnet-sound`, `tamarind-gate`.
- `iris-bluff` (approval): departure from Zurich for personal reasons with no authorisation or ad hoc signatures
  (lines 440-443, 672-678). Twins `lotus-cairn` (signed), `nettle-strand` (validated leave).
- `magpie-hollow` (approval): the accompanied-Commissioner derogation is pending with the authorising officer
  (lines 733-735, 291-295). Twins `falcon-mere` (granted), `zephyr-knoll` (economy).

Degenerate agents: always-flag passes 2 (`fennel-rock`, `hazel-tide`); always-cheapest with LOWEST_FARE and NONE
passes 6 of 32 (18.75%): `linden-harbour`, `pebble-moor`, `ochre-vale`, `ember-wharf`, `nettle-strand`,
`rowan-sedge`.

## Hosted-cap estimate

Handbook 14,137 words, 92,039 bytes: about 18,800 tokens at 1.33 a word (about 23,000 at 4 characters a token).
First call under `full`: about 21,000 input tokens (handbook, about 330 of instructions, about 1,800 of tool and
submit schemas, the request). A 3-call run (`get_trip`, `search_flights`, `submit`): about 65,000 input tokens, at
the 65,536 cap; at 4 characters a token about 77,000, over. `lotus-cairn` and `iris-bluff` may add the comparison
search (4 calls, about 87,000). Run `full` locally with a raised cap.

## Blind read (no agents; re-derived from the handbook text and the tool outputs, not from rules.py)

I printed every scenario's `get_trip` record and every pinned `search_flights` result, then answered each from the
frozen text. This is a self-read by the builder, not an independent auditor's: treat it as a consistency check.

| Scenario | My answer from the text and offers | Agrees |
|---|---|---|
| linden-harbour | Rail 1,850 km each way: air automatic (710-711); lowest economy, Iberia 12:40, 18900 (723-726) | yes |
| cobalt-ridge | Must land by 11:00; 10:30 and 13:00 land late; LH 08:20 22800 (723-726, meeting times) | yes |
| saffron-dune | 495-minute nonstop qualifies (730-732); cheapest business KQ 278000, lands 07:30 | yes |
| heather-quay | Host may move the meeting: appreciable risk; lowest flexible fare IB 30500 (727-729) | yes |
| willow-crest | Meeting confirmed: no flexible fare; lowest fare KLM 15900 (723-726) | yes |
| pebble-moor | Day before 10 Dec is 9 Dec; KLM 13:10 17900 | yes |
| garnet-sound | 240 minutes is "at least four hours": business; EgyptAir 129000 | yes |
| tamarind-gate | 235 out, 235 back: no business; EgyptAir economy 28500 | yes |
| ochre-vale | 400 x 2 = 800, "at least 800": air automatic though rail is cheaper; LH 12:15 21200 | yes |
| quartz-fell | 790 km: not automatic; 21200 against 12900 rail, a 4-hour train: not cost-efficient; refuse | yes |
| juniper-bay | 08:00 is not before 8:00; 16:05 lands after 12:45; IB 08:00 17600 | yes |
| marigold-tor | 07:55 is before 8:00 and no ad hoc decision; traveller declines it; IB 10:15 21400 | yes |
| ember-wharf | Lands 22:00, not after 22:00: cheapest KLM 19:45 18300 | yes |
| sorrel-heath | Lands 22:05: cannot be required; Iberia 16:40 22100 | yes |
| aspen-loch | Only the 06:45 lands by 10:00; line manager's reasoned ad hoc decision on file: AF 06:45 16200 | yes |
| falcon-mere | 110 minutes: no business by duration; derogation authorised by the AO: AF business 62000 | yes |
| indigo-brae | AO refused the nonstop: TK connection 31000 | yes |
| kestrel-plain | No nonstop listed; Istanbul-Dubai segments of 250/245 minutes qualify; TK 09:40 business 165000 | yes |
| lotus-cairn | Personal departure authorised and both ad hoc signatures on file; lowest Zurich fare LX 17:45 15200 (Paris 13900 is only the comparison) | yes |
| nettle-strand | Mission on validated leave: depart from Dublin (614-616); lowest IB 13700 | yes |
| rowan-sedge | 630 km out and back, but 9600 against 14800 rail: cost-efficient; LX 9600 | yes |
| umber-glen | Segments 225 and 230 (back 235 and 230): no business; TK 08:30 economy 43000 | yes |
| violet-shoal | Direct preferred; 26500 against 22800 is not manifestly unreasonable; AF nonstop | yes |
| yarrow-point | Rest day is a distractor; 765-minute segment: business; SQ 378000 | yes |
| zephyr-knoll | First-class rail says nothing of air; 150 minutes: economy IB 18700 | yes |
| bramble-isle | Family holiday is neither mission nor authorised travel: refuse | yes |
| cedar-fjord | Husband is not the person concerned: refuse | yes |
| dahlia-spur | Authorised travel with transport met by the organiser, ticket already issued: refuse | yes |

Points I weighed and kept:
- `quartz-fell`: REFUSE means no flight; the traveller would go by train, which the agency buys outside this tool.
  The decision field reads "the organisation buys no ticket at all for this request", and the request is for a
  flight. A model that answers FLAG for the authorising officer to justify air would be taking a reading the record
  does not support (the flight is dearer than first-class rail on a journey under four hours by train).
- `dahlia-spur`: lines 1201-1204 (cancel an authorisation without expenses and enter a new one) are the line
  manager's and AO's own wish, not something the traveller's request sets off; REFUSE stands.
- `ember-wharf` and `juniper-bay`: the traveller's "unless the guide says I have to" is answered by the
  lowest-available-rates rule, since the hours rule does not reach exactly 08:00 or 22:00. A model that books the
  dearer flight there is reading "middle of the night" as a veto; that would be a slip, not a defect.

## Template change requests

1. Add Athens (ATH), Heraklion (HER) and Brussels (BRU) to `world.py` `AIRPORTS`, and Aegean (A3, hub ATH) and
   Brussels Airlines (SN, hub BRU) to `AIRLINES`, so EU-agency handbooks can start trips at their real seats. Run
   `tools/world_diff.py` across plugins first; no existing route touches these airports.
2. Optional: a European low-cost carrier (e.g. FR or U2, flagged as low-cost) would let the low-cost booking
   clauses of the EU mission guides (line 738 here) be tested.

## Check outputs (final commit)

The notes live under `tests/` because stock `nanoagent plugin inspect` rejects extra root files; inspect exits 0.

```
$ uv run pytest -q
258 passed
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .   (stock checkout, exit 0)
id enisa-flight-policy | tools 4 | tasks ['booking-requirements', 'search-flights', 'book-enisa-flight']
$ nanoagent plugin pack . <scratch>/enisa-flight-policy.tar.gz
packed (191108 bytes)
$ <stock>/.venv/bin/python ../_template/tools/stock_verify.py .
32 scenarios, 0 failures (every scenario right=True score=1.00 identical=True wrong-decision-rejected=True)
```
