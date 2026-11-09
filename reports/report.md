# Robot cell triage report: 02 Nov 2026 – 08 Nov 2026

Log lines read: 4,154 · unreadable lines skipped: 10 · stoppages found: 44 · total downtime: 6 h 27 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 24 | 2 h 19 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 46 min | 1 h 39 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 25 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 23 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Wed 04 Nov 22:04:28**: E-PWR-01 Supply voltage dip on PLC was followed within 3.3 s by R1 (E-COMM-02), R3 (E-COMM-02), R4 (E-COMM-02). Treat it as one problem: 52 min of downtime in total.
- **Sat 07 Nov 06:00:31**: E-PWR-01 Supply voltage dip on PLC was followed within 3.6 s by R3 (E-COMM-02), R4 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 53 min of downtime in total.

### Which faults spread, learned from this log

Chains above are started by the list in knowledge.py. This table checks that list against the log: how often each fault was followed by a stop on another machine within seconds, compared with chance.

| Fault | Times | Followed by another stop | Lift over chance | Spreads? | In knowledge.py |
|---|---|---|---|---|---|
| E-PWR-01 Supply voltage dip | 2 | 2 | 1295.4x | yes | yes |
| E-COMM-02 Fieldbus timeout | 6 | 0 | 0.0x | no | yes |

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 6 times in the first half of the period, 18 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability, time between failures and time to repair

| Machine | Available | Stops | Mean time between failures | Mean time to repair |
|---|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.8 h | 7.7 min |
| PLC | 99.9 % | 2 | 83.9 h | 3.3 min |
| R1 | 99.4 % | 5 | 33.4 h | 12.7 min |
| R2 | 98.6 % | 26 | 6.4 h | 5.5 min |
| R3 | 99.7 % | 3 | 55.8 h | 11.2 min |
| R4 | 98.8 % | 5 | 33.2 h | 23.5 min |
