# Robot cell triage report: 04 Nov 2026 – 10 Nov 2026

Log lines read: 4,154 · unreadable lines skipped: 10 · stoppages found: 45 · total downtime: 6 h 12 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 25 | 2 h 19 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 40 min | 1 h 33 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 12 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 25 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Fri 06 Nov 22:02:43**: E-PWR-01 Supply voltage dip on PLC was followed within 3.0 s by R4 (E-COMM-02), R3 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 51 min of downtime in total.
- **Mon 09 Nov 22:00:37**: E-PWR-01 Supply voltage dip on PLC was followed within 2.9 s by R4 (E-COMM-02), R3 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 49 min of downtime in total.

### Which faults spread, learned from this log

Chains above are started by the list in knowledge.py. This table checks that list against the log: how often each fault was followed by a stop on another machine within seconds, compared with chance.

| Fault | Times | Followed by another stop | Lift over chance | Spreads? | In knowledge.py |
|---|---|---|---|---|---|
| E-PWR-01 Supply voltage dip | 2 | 2 | 1283.0x | yes | yes |
| E-COMM-02 Fieldbus timeout | 6 | 0 | 0.0x | no | yes |

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 7 times in the first half of the period, 18 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability, time between failures and time to repair

| Machine | Available | Stops | Mean time between failures | Mean time to repair |
|---|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.8 h | 8.2 min |
| PLC | 99.9 % | 2 | 83.9 h | 3.3 min |
| R1 | 99.4 % | 3 | 55.6 h | 19.4 min |
| R2 | 98.6 % | 25 | 6.6 h | 5.6 min |
| R3 | 99.7 % | 3 | 55.8 h | 10.5 min |
| R4 | 98.9 % | 9 | 18.4 h | 12.4 min |
