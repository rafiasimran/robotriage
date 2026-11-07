# Robot cell triage report: 31 Oct 2026 – 06 Nov 2026

Log lines read: 4,150 · unreadable lines skipped: 10 · stoppages found: 43 · total downtime: 5 h 50 min

## Fix these first

Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.

| # | Fault | Where | Times | Downtime | of which caused on other machines |
|---|---|---|---|---|---|
| 1 | E-GRIP-01 Gripper vacuum below threshold | R2 | 23 | 1 h 53 min | – |
| 2 | E-PWR-01 Supply voltage dip | PLC | 2 | 1 h 37 min | 1 h 31 min |
| 3 | E-JNT-03 Joint 3 over-temperature | R4 | 3 | 1 h 25 min | – |
| 4 | E-COLL-01 Collision detected | R1 | 1 | 25 min | – |
| 5 | E-CONV-01 Conveyor jam | CV1 | 3 | 20 min | – |

**First checks for E-GRIP-01 (Gripper vacuum below threshold):**

- Inspect and replace the suction cup
- Leak-test the vacuum line
- Clean the ejector filter

## One cause, many alarms

- **Mon 02 Nov 22:04:28**: E-PWR-01 Supply voltage dip on PLC was followed within 2.8 s by R1 (E-COMM-02), R4 (E-COMM-02), R3 (E-COMM-02). Treat it as one problem: 46 min of downtime in total.
- **Thu 05 Nov 06:00:56**: E-PWR-01 Supply voltage dip on PLC was followed within 2.5 s by R3 (E-COMM-02), R4 (E-COMM-02), R1 (E-COMM-02). Treat it as one problem: 51 min of downtime in total.

### Which faults spread, learned from this log

Chains above are started by the list in knowledge.py. This table checks that list against the log: how often each fault was followed by a stop on another machine within seconds, compared with chance.

| Fault | Times | Followed by another stop | Lift over chance | Spreads? | In knowledge.py |
|---|---|---|---|---|---|
| E-PWR-01 Supply voltage dip | 2 | 2 | 1345.2x | yes | yes |
| E-COMM-02 Fieldbus timeout | 6 | 0 | 0.0x | no | yes |

## Getting worse

- **R2 E-GRIP-01 Gripper vacuum below threshold**: 6 times in the first half of the period, 17 in the second half. Likely: worn suction cup. Plan maintenance before it turns into a long stop.

## Availability, time between failures and time to repair

| Machine | Available | Stops | Mean time between failures | Mean time to repair |
|---|---|---|---|---|
| CV1 | 99.8 % | 3 | 55.8 h | 6.5 min |
| PLC | 99.9 % | 2 | 83.9 h | 3.1 min |
| R1 | 99.4 % | 5 | 33.4 h | 11.4 min |
| R2 | 98.9 % | 23 | 7.2 h | 4.9 min |
| R3 | 99.7 % | 2 | 83.6 h | 16.3 min |
| R4 | 98.8 % | 8 | 20.7 h | 15.1 min |
