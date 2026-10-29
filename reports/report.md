# Robot cell triage report: 22 Oct 2026 – 28 Oct 2026

Log lines read: 4,163 · unreadable lines skipped: 10 · stoppages found: 45 · total downtime: 6 h 12 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 24 | 2 h 9 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 42 min | 1 h 37 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 17 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 24 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Sat 24 Oct 06:00:36**: E-PWR-01 Supply voltage dip on PLC was followed within 2.9 s by R4 (E-COMM-02), R3 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 57 min of downtime in total.
- **Tue 27 Oct 22:05:02**: E-PWR-01 Supply voltage dip on PLC was followed within 1.6 s by R4 (E-COMM-02), R1 (E-COMM-02), R3 (E-COMM-02). Treat it as one problem: 45 min of downtime in total.

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 8 times in the first half of the period, 16 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.
- **R2 E-SAFE-01 Light curtain tripped**: 1 times in the first half of the period, 3 in the second half. Likely: operator entered the cell. Plan maintenance before it turns into a long stop.

## Availability

| Machine | Available |
|---|---|
| CV1 | 99.8 % |
| PLC | 99.9 % |
| R1 | 99.4 % |
| R2 | 98.6 % |
| R3 | 99.7 % |
| R4 | 98.9 % |

## Data notes

- 1 stoppage(s) had no RESUME line; the end was taken from the next cycle report.
