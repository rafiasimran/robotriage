# Robot cell triage report: 08 Nov 2026 – 14 Nov 2026

Log lines read: 4,158 · unreadable lines skipped: 10 · stoppages found: 43 · total downtime: 5 h 50 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 23 | 2 h 3 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 36 min | 1 h 30 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 17 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 17 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Tue 10 Nov 22:03:14**: E-PWR-01 Supply voltage dip on PLC was followed within 3.0 s by R1 (E-COMM-02), R3 (E-COMM-02), R4 (E-COMM-02). Treat it as one problem: 47 min of downtime in total.
- **Fri 13 Nov 14:04:29**: E-PWR-01 Supply voltage dip on PLC was followed within 3.1 s by R3 (E-COMM-02), R4 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 49 min of downtime in total.

### Which faults spread, learned from this log

Chains above are started by the list in knowledge.py. This table checks that list against the log: how often each fault was followed by a stop on another machine within seconds, compared with chance.

| Fault | Times | Followed by another stop | Lift over chance | Spreads? | In knowledge.py |
|---|---|---|---|---|---|
| E-PWR-01 Supply voltage dip | 2 | 2 | 1381.9x | yes | yes |
| E-COMM-02 Fieldbus timeout | 6 | 0 | 0.0x | no | yes |

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 4 times in the first half of the period, 19 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability, time between failures and time to repair

| Machine | Available | Stops | Mean time between failures | Mean time to repair |
|---|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.9 h | 5.7 min |
| PLC | 99.9 % | 2 | 83.9 h | 3.0 min |
| R1 | 99.5 % | 4 | 41.7 h | 13.6 min |
| R2 | 98.7 % | 25 | 6.6 h | 5.1 min |
| R3 | 99.7 % | 2 | 83.7 h | 15.3 min |
| R4 | 98.9 % | 7 | 23.7 h | 16.5 min |
