# Robot cell triage report: 11 Nov 2026 – 17 Nov 2026

Log lines read: 4,155 · unreadable lines skipped: 10 · stoppages found: 44 · total downtime: 5 h 54 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 22 | 2 h 2 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 38 min | 1 h 33 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 13 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 20 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Fri 13 Nov 14:02:45**: E-PWR-01 Supply voltage dip on PLC was followed within 3.8 s by R4 (E-COMM-02), R3 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 50 min of downtime in total.
- **Mon 16 Nov 06:04:02**: E-PWR-01 Supply voltage dip on PLC was followed within 2.1 s by R1 (E-COMM-02), R4 (E-COMM-02), R3 (E-COMM-02). Treat it as one problem: 48 min of downtime in total.

### Which faults spread, learned from this log

Chains above are started by the list in knowledge.py. This table checks that list against the log: how often each fault was followed by a stop on another machine within seconds, compared with chance.

| Fault | Times | Followed by another stop | Lift over chance | Spreads? | In knowledge.py |
|---|---|---|---|---|---|
| E-PWR-01 Supply voltage dip | 2 | 2 | 1289.1x | yes | yes |
| E-COMM-02 Fieldbus timeout | 6 | 0 | 0.0x | no | yes |

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 7 times in the first half of the period, 15 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability, time between failures and time to repair

| Machine | Available | Stops | Mean time between failures | Mean time to repair |
|---|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.8 h | 6.7 min |
| PLC | 100.0 % | 2 | 83.9 h | 2.4 min |
| R1 | 99.4 % | 6 | 27.8 h | 9.4 min |
| R2 | 98.8 % | 22 | 7.5 h | 5.6 min |
| R3 | 99.6 % | 4 | 41.8 h | 9.8 min |
| R4 | 98.9 % | 7 | 23.7 h | 15.9 min |
