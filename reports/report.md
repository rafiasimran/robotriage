# Robot cell triage report: 06 Nov 2026 – 12 Nov 2026

Log lines read: 4,154 · unreadable lines skipped: 10 · stoppages found: 45 · total downtime: 6 h 4 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 25 | 2 h 13 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 33 min | 1 h 28 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 22 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 22 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Sun 08 Nov 06:05:36**: E-PWR-01 Supply voltage dip on PLC was followed within 3.7 s by R3 (E-COMM-02), R4 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 50 min of downtime in total.
- **Wed 11 Nov 14:05:58**: E-PWR-01 Supply voltage dip on PLC was followed within 1.7 s by R1 (E-COMM-02), R4 (E-COMM-02), R3 (E-COMM-02). Treat it as one problem: 44 min of downtime in total.

### Which faults spread, learned from this log

Chains above are started by the list in knowledge.py. This table checks that list against the log: how often each fault was followed by a stop on another machine within seconds, compared with chance.

| Fault | Times | Followed by another stop | Lift over chance | Spreads? | In knowledge.py |
|---|---|---|---|---|---|
| E-PWR-01 Supply voltage dip | 2 | 2 | 1313.9x | yes | yes |
| E-COMM-02 Fieldbus timeout | 6 | 0 | 0.0x | no | yes |

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 4 times in the first half of the period, 21 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability, time between failures and time to repair

| Machine | Available | Stops | Mean time between failures | Mean time to repair |
|---|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.8 h | 7.3 min |
| PLC | 100.0 % | 2 | 83.9 h | 2.5 min |
| R1 | 99.4 % | 6 | 27.8 h | 10.2 min |
| R2 | 98.7 % | 26 | 6.4 h | 5.2 min |
| R3 | 99.7 % | 3 | 55.8 h | 10.0 min |
| R4 | 98.9 % | 5 | 33.2 h | 22.2 min |
