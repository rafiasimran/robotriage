# Robot cell triage report: 25 Oct 2026 – 31 Oct 2026

Log lines read: 4,157 · unreadable lines skipped: 10 · stoppages found: 45 · total downtime: 6 h 8 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 23 | 2 h 7 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 38 min | 1 h 32 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 22 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 25 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Tue 27 Oct 06:05:49**: E-PWR-01 Supply voltage dip on PLC was followed within 3.6 s by R1 (E-COMM-02), R4 (E-COMM-02), R3 (E-COMM-02). Treat it as one problem: 47 min of downtime in total.
- **Fri 30 Oct 22:03:38**: E-PWR-01 Supply voltage dip on PLC was followed within 3.6 s by R4 (E-COMM-02), R3 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 51 min of downtime in total.

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 3 times in the first half of the period, 20 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability and time between failures

| Machine | Available | Stops | Mean time between failures |
|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.8 h |
| PLC | 99.9 % | 2 | 83.9 h |
| R1 | 99.4 % | 3 | 55.6 h |
| R2 | 98.7 % | 25 | 6.6 h |
| R3 | 99.7 % | 6 | 27.9 h |
| R4 | 98.8 % | 6 | 27.7 h |
