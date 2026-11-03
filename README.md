# RoboTriage

[![Tests](https://github.com/rafiasimran/robotriage/actions/workflows/tests.yml/badge.svg)](https://github.com/rafiasimran/robotriage/actions/workflows/tests.yml) [![Daily triage](https://github.com/rafiasimran/robotriage/actions/workflows/triage.yml/badge.svg)](https://github.com/rafiasimran/robotriage/actions/workflows/triage.yml)

Automatic fault triage for a robot cell. It reads a week of machine logs and answers the three questions a maintenance team asks every Monday: **what stopped us, what actually caused it, and what should we fix first?**

**[Live dashboard](https://rafiasimran.github.io/robotriage/)** · **[Latest report](reports/report.md)**, both updated every morning by GitHub Actions.

![Dashboard](docs/screenshot.png)

## The problem

When something goes wrong on a production line, the screen fills with alarms. A short voltage dip at the cell controller can make three robots report network timeouts within seconds. Each alarm looks like its own problem, so people end up checking network cables when the real cause was the power supply.

Slow problems hide in the opposite way. A suction cup wearing out causes one short stop on Monday and six on Sunday. No single stop looks serious, but together it's the biggest loss of the week.

Engineers usually find these patterns by scrolling through logs by hand. RoboTriage does that part automatically.

## What it does

1. **Reads the log**, either the cell's text log or a CSV alarm history exported from an HMI or SCADA system (one row per alarm coming on or going off). Garbled lines are skipped but counted, so the report says how much couldn't be read.
2. **Finds every stoppage**: from the fault to the moment the machine was back in automatic mode. A second alarm on a machine that is already stopped isn't counted twice.
3. **Groups chains of faults**: when a fault that can spread (a power dip or a bus timeout) is followed within 10 seconds by stops on other machines, they are treated as one event with that fault as the root cause. It also checks the list of faults that can spread against the log itself (see below).
4. **Charges downtime to the root cause.** A network timeout caused by a power dip counts as power downtime.
5. **Ranks problems by production time lost** and adds first checks for the top one from a small fault knowledge base.
6. **Flags problems that are getting worse**, comparing the first and second half of the period.
7. **Calculates availability, mean time between failures (MTBF) and mean time to repair (MTTR)** for each machine, against planned production time if you give it a shift calendar.
8. **Writes a report** in Markdown and JSON.

```mermaid
flowchart LR
    A[Cell log] --> B[parse.py<br/>read + count bad lines]
    B --> C[stoppages<br/>fault to resume]
    C --> D[cascades<br/>one cause, many alarms]
    D --> E[rank by downtime<br/>+ getting worse]
    E --> F[report.md / report.json]
    K[knowledge.py<br/>causes + first checks] --> F
    G[GitHub Actions<br/>every morning] --> A
```

## Example: what it found in the sample week

Simulated week of 19–25 Oct 2026, 4,158 log lines. You get exactly this week with the default settings of the simulator (seed 7):

| # | Fault | Where | Times | Downtime |
|---|---|---|---|---|
| 1 | Gripper vacuum below threshold | R2 | 26 | 2 h 37 min |
| 2 | Supply voltage dip | PLC | 2 | 1 h 43 min, of which 1 h 38 min on other robots |
| 3 | Joint 3 over-temperature | R4 | 3 | 1 h 28 min |

- The two voltage dips each triggered fieldbus timeouts on R1, R3 and R4 within 4 seconds. Counted separately, those timeouts would look like a network problem. RoboTriage reports them as **two power events**.
- R2's gripper faults went from 8 in the first half of the week to 18 in the second half. The report flags it as **getting worse** and suggests checking the suction cup and vacuum line.

## Run it

Python 3.10+ and no extra packages needed to run it (pytest for the tests).

```bash
python -m robotriage.simulate logs/cell_week.log      # make a sample week
python -m robotriage logs/cell_week.log --out reports  # triage it
pytest -q
```

Options:

- `--window 10`: how many seconds apart faults can be to count as one chain.
- `--calendar shifts.json`: planned breaks, changeovers and maintenance, so they don't count as lost time. The format is in `robotriage/shifts.py`.
- `--learn-chains`: decide which faults start a chain from the log instead of the list in `knowledge.py`.
- A `.csv` file is read as an alarm history. If its columns have other names, map them: `--columns time=Timestamp,device=Source,code=AlarmID,state=Event`. The state column can say on/off, came/went, raised/cleared and similar.

The simulator takes `--start`, `--days` and `--seed`.

## Which faults spread: learned, not just written down

Which faults can knock out other machines is a list in `knowledge.py`. A plant engineer would ask how I know that list is right for their cell. So the report also learns it from the log.

For each fault code it looks at the times that fault came first (no other machine already stopping just before it) and counts how often another machine stopped within the next 10 seconds. That rate is compared with chance: how likely another machine is to stop in any 10-second slot of the log. A fault counts as spreading if it was followed at least twice, at least half the time, and at least 10 times more often than chance.

In the sample week this finds exactly one fault that spreads: the supply voltage dip (2 of 2 times, about 1,200 times more often than chance). The fieldbus timeouts that follow each dip are not picked up, because they always come after the dip. That disagrees with `knowledge.py`, which lists fieldbus timeouts as able to spread. I've kept them in the list, because a damaged network cable on one robot really could stop others, but the report now shows the disagreement next to the list instead of hiding it. It finds the same answer for every seed I tried.

## Automation

- **Tests** run on every push.
- **Daily triage** runs every morning at 05:30 UTC. If there's a `.log` file in `logs/`, it triages the newest one. If not, it simulates the last 7 days and triages that. The new report is committed back to the repo, and the dashboard in `docs/` (GitHub Pages) reads the same data. Dropping a log file into `logs/` and pushing also triggers a run.

## Tests

28 tests. The unit tests cover the tricky cases one by one: double faults on a stopped machine, a missing RESUME line, a stop that never ends, a real chain versus two faults that just happen close together, CSV alarm rows that came and went, a stop that runs into a lunch break, and one lucky coincidence that must not be learned as a chain. The end-to-end test generates a full week and checks that the pipeline finds every problem hidden in it, for several random seeds.

## Project structure

```
robotriage/
  parse.py       read text logs and CSV alarm exports, count broken lines
  triage.py      stoppages, cascades, learned chains, ranking, trends, availability, MTBF, MTTR
  shifts.py      planned breaks and maintenance from a shift calendar
  knowledge.py   fault codes: meaning, likely causes, first checks
  report.py      Markdown + JSON report
  simulate.py    realistic week of logs with known problems hidden in it
  __main__.py    command line entry point
tests/
reports/         latest report (updated by GitHub Actions)
docs/            dashboard page for GitHub Pages
```

## Design decisions

- **Learned chains are shown, not swapped in silently.** By default the report uses the reviewed list and prints the learned one next to it. An engineer decides when to trust the data over the list.
- **Downtime goes to the root cause.** Otherwise the team fixes the symptom (cables) and the cause (power) keeps coming back.
- **If a RESUME line is missing, the stop ends at the machine's next cycle report.** Without this, one lost line in the log would count days of downtime. The report says how many ends were inferred this way.
- **Timing alone is not proof of cause.** The first version grouped any faults that happened within 10 seconds, and a daily report blamed a light curtain trip on one robot for a gripper fault on the next. Now only faults that can actually spread through the cell start a chain, and a test covers that exact case.
- **The trend check is simple on purpose:** split the period in half and compare counts. It's easy to explain and hard to fool with one bad day.
- **Standard library only.** It should run on any machine in a plant without installing anything.

## Limitations

- **The logs are simulated.** Real controller logs are confidential, so `simulate.py` writes the kind of log a cell like this produces, with known problems hidden in it. Fault codes are generic examples, not a specific robot vendor's codes. The CSV adapter reads the alarm history format most HMI and SCADA systems export, but it hasn't been tried on a real plant export yet.
- **Learning chains needs history.** A power dip that happens twice a week is the minimum it can learn from. With only a few days of log it will miss rare faults that spread, which is why the reviewed list stays the default.
- **One alarm going off resumes the machine.** In a CSV export, if two alarms are active on one machine and one clears, the stop ends there.
- MTBF counts every stop on a machine, including ones caused by another machine's fault.

## Next steps

- Run it on a real public event log, such as the event data from the Kelmarsh wind farm (six turbines, 2016 to 2021), to see what holds up on real data
- MTBF that leaves out stops caused by another machine
- The same approach for solar inverter alarms

## Tech

Python · pytest · GitHub Actions · GitHub Pages · Chart.js

---

Built by **Rafia Imran** · [GitHub profile](https://github.com/rafiasimran)
