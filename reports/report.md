# Robot cell triage report: 18 Oct 2026 – 24 Oct 2026

Log lines read: 4,160 · unreadable lines skipped: 10 · stoppages found: 46 · total downtime: 6 h 14 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 24 | 2 h 19 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 38 min | 1 h 32 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 7 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-SAFE-01 Light curtain tripped | R2, R3, R4 | 6 | 22 min | 3 min |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Tue 20 Oct 06:03:56**: E-PWR-01 Supply voltage dip on PLC was followed within 3.2 s by R3 (E-COMM-02), R1 (E-COMM-02), R4 (E-COMM-02). Treat it as one problem: 46 min of downtime in total.
- **Thu 22 Oct 12:04:49**: E-SAFE-01 Light curtain tripped on R3 was followed within 4.5 s by R2 (E-GRIP-01). Treat it as one problem: 4 min of downtime in total.
- **Fri 23 Oct 06:02:51**: E-PWR-01 Supply voltage dip on PLC was followed within 2.5 s by R1 (E-COMM-02), R4 (E-COMM-02), R3 (E-COMM-02). Treat it as one problem: 52 min of downtime in total.

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 8 times in the first half of the period, 17 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability

| Machine | Available |
|---|---|
| CV1 | 99.8 % |
| PLC | 99.9 % |
| R1 | 99.4 % |
| R2 | 98.4 % |
| R3 | 99.6 % |
| R4 | 99.0 % |

## Data notes

- 1 stoppage(s) had no RESUME line; the end was taken from the next cycle report.
