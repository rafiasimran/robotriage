# Robot cell triage report: 27 Oct 2026 – 02 Nov 2026

Log lines read: 4,171 · unreadable lines skipped: 10 · stoppages found: 48 · total downtime: 6 h 12 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 26 | 2 h 12 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 37 min | 1 h 30 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 20 min | – |
| 4 | E-CONV-01 Conveyor jam | CV1 | 3 | 26 min | – |
| 5 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Thu 29 Oct 06:01:16**: E-PWR-01 Supply voltage dip on PLC was followed within 3.2 s by R1 (E-COMM-02), R3 (E-COMM-02), R4 (E-COMM-02). Treat it as one problem: 49 min of downtime in total.
- **Sun 01 Nov 14:00:42**: E-PWR-01 Supply voltage dip on PLC was followed within 3.2 s by R3 (E-COMM-02), R4 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 48 min of downtime in total.

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 8 times in the first half of the period, 18 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability and time between failures

| Machine | Available | Stops | Mean time between failures |
|---|---|---|---|
| CV1 | 99.7 % | 3 | 55.8 h |
| PLC | 99.9 % | 2 | 83.9 h |
| R1 | 99.5 % | 3 | 55.7 h |
| R2 | 98.7 % | 29 | 5.7 h |
| R3 | 99.7 % | 3 | 55.8 h |
| R4 | 98.8 % | 8 | 20.7 h |
