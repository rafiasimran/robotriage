# Robot cell triage report: 21 Oct 2026 – 27 Oct 2026

Log lines read: 4,151 · unreadable lines skipped: 10 · stoppages found: 45 · total downtime: 6 h 29 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 25 | 2 h 19 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 41 min | 1 h 34 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 30 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 23 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Fri 23 Oct 14:05:22**: E-PWR-01 Supply voltage dip on PLC was followed within 3.8 s by R1 (E-COMM-02), R3 (E-COMM-02), R4 (E-COMM-02). Treat it as one problem: 55 min of downtime in total.
- **Mon 26 Oct 06:04:02**: E-PWR-01 Supply voltage dip on PLC was followed within 2.3 s by R1 (E-COMM-02), R3 (E-COMM-02), R4 (E-COMM-02). Treat it as one problem: 46 min of downtime in total.

## Getting worse

Nothing is clearly getting more frequent.


## Availability

| Machine | Available |
|---|---|
| CV1 | 99.8 % |
| PLC | 99.9 % |
| R1 | 99.4 % |
| R2 | 98.6 % |
| R3 | 99.7 % |
| R4 | 98.8 % |
