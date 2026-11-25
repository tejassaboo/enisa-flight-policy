# Validation notes: enisa-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/enisa-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head a0d7ba9. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

27/32 valid (84.4%), mean field score 0.932, **easy 6/6**. By category: boundary_twin 6/8, distractor 3/3, easy 6/6, flag 2/4, hidden_clause 3/3, multi_rule 5/5, refusal 2/3.
$0.00188 billed per run, 22,929 prompt tokens per call, 3.94 calls per run;
30 of 32 runs would exceed the hosted 65,536 cap.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| dahlia-spur | refusal | FLAG the 13:30 Air France, APPROVAL_REQUIRED, clause PERSONAL_CHANGES; key REFUSE | model slip | It treated the request as a change for personal reasons (2.2.2.4, lines 485-495) to be authorised by the line manager. The traveller wants the later flight "so I can finish some work first", and the signed authorisation reads "transport and accommodation met by the organiser; no cost for the agency's budget"; the organiser's ticket is issued (record note). Expenses are allowed only within the authorisation (lines 1189-1191), and even under 2.2.2.4 any extra cost is the traveller's, here the whole fare. Nothing is the agency's to buy. |
| fennel-rock | flag | BOOK KLM nonstop, LOWEST_FARE; key FLAG | model slip | "Among the nonstop economy options, KLM ... is the lowest fare at €1,140, so I booked it." It never weighed line 719-722 (the authorising officer may refuse a direct flight that "would represent a manifestly unreasonable expense") against a connection at €310. The twins indigo-brae and violet-shoal passed. |
| hazel-tide | flag | BOOK Turkish economy, LONG_FLIGHT_CONDITION_NOT_MET; key FLAG | model slip | "The Frankfurt–Istanbul leg is only 160 minutes, so the four-hour continuous flying time condition for business class is not met." It never weighed "if the outward or return journey includes" (lines 730-732) against the 375-minute planned return. The twins garnet-sound and tamarind-gate passed. |
| juniper-bay | boundary_twin | BOOK Iberia 10:15 ($214), MEETING_TIMES; key Iberia 08:00 ($176) | model slip | It read the rule right and let the preference win: "the guide says 'cannot be required to leave before 8:00' ... So 08:00 is allowed ... The 08:00 flight is cheaper (€176 vs €214)", then booked the 10:15 "to avoid a crack-of-dawn departure". The request asks to avoid one "unless the guide says I have to take it". The twin marigold-tor (07:55) passed. |
| sorrel-heath | boundary_twin | BOOK KLM 19:50 landing 22:05 ($183), LOWEST_FARE; key Iberia 16:40 ($221) | model slip | "It lands at 22:05, which is not the middle of the night, so it satisfies the traveller's request." It never applied lines 650-655 (a traveller cannot be required to arrive after 22:00 without the line manager's reasoned decision), which the request points to ("unless the guide leaves no choice"). The twin ember-wharf (22:00) passed. |

## Fixes

None. All 5 failures are model slips; no key was widened and no record changed.

## Q2

Unchanged: the always-cheapest agent passes **6/32 (19%)**.

## Re-score at the head (stored answers)

27/32 (no key changed). No re-run is required.

## Checks (at the notes commit)

`uv run pytest -q` (258 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, byte-identical `rules.py`,
`tools/stock_verify.py` (0 failures), stock `nanoagent plugin inspect .` (exit 0).
