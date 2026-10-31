# Robot cell triage report: 24 Oct 2026 – 30 Oct 2026

Log lines read: 4,159 · unreadable lines skipped: 10 · stoppages found: 44 · total downtime: 6 h 24 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 24 | 2 h 9 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 40 min | 1 h 34 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 35 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 23 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Mon 26 Oct 14:03:58**: E-PWR-01 Supply voltage dip on PLC was followed within 3.1 s by R3 (E-COMM-02), R4 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 47 min of downtime in total.
- **Thu 29 Oct 06:05:49**: E-PWR-01 Supply voltage dip on PLC was followed within 3.4 s by R3 (E-COMM-02), R4 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 52 min of downtime in total.

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 7 times in the first half of the period, 17 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability and time between failures

| Machine | Available | Stops | Mean time between failures |
|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.8 h |
| PLC | 99.9 % | 2 | 83.9 h |
| R1 | 99.4 % | 5 | 33.4 h |
| R2 | 98.7 % | 25 | 6.6 h |
| R3 | 99.7 % | 2 | 83.7 h |
| R4 | 98.7 % | 7 | 23.7 h |
