# Robot cell triage report: 21 Nov 2026 – 27 Nov 2026

Log lines read: 4,157 · unreadable lines skipped: 10 · stoppages found: 46 · total downtime: 6 h 24 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 25 | 2 h 16 min | – |
| 2 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 39 min | – |
| 3 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 38 min | 1 h 33 min |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 16 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Mon 23 Nov 06:04:25**: E-PWR-01 Supply voltage dip on PLC was followed within 4.0 s by R1 (E-COMM-02), R3 (E-COMM-02), R4 (E-COMM-02). Treat it as one problem: 45 min of downtime in total.
- **Thu 26 Nov 22:04:24**: E-PWR-01 Supply voltage dip on PLC was followed within 3.6 s by R4 (E-COMM-02), R3 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 53 min of downtime in total.

### Which faults spread, learned from this log

Chains above are started by the list in knowledge.py. This table checks that list against the log: how often each fault was followed by a stop on another machine within seconds, compared with chance.

| Fault | Times | Followed by another stop | Lift over chance | Spreads? | In knowledge.py |
|---|---|---|---|---|---|
| E-PWR-01 Supply voltage dip | 2 | 2 | 1232.4x | yes | yes |
| E-COMM-02 Fieldbus timeout | 6 | 0 | 0.0x | no | yes |

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 5 times in the first half of the period, 20 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability, time between failures and time to repair

| Machine | Available | Stops | Mean time between failures | Mean time to repair |
|---|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.9 h | 5.2 min |
| PLC | 99.9 % | 2 | 83.9 h | 2.8 min |
| R1 | 99.4 % | 6 | 27.8 h | 10.4 min |
| R2 | 98.6 % | 25 | 6.6 h | 5.4 min |
| R3 | 99.7 % | 3 | 55.8 h | 10.1 min |
| R4 | 98.7 % | 7 | 23.7 h | 19.2 min |
