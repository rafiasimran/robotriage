# Changelog

## 1.1.0 (2026-11-03)

Closer to real plant data.

- Reads CSV alarm history exports from HMI and SCADA systems (one row per alarm
  coming on or going off), with `--columns` to map other column names. The daily
  run picks up `.csv` files in `logs/` too.
- Optional shift calendar (`--calendar`): planned breaks, changeovers and
  maintenance no longer count as lost time. Availability and MTBF are measured
  against planned production time.
- Mean time to repair (MTTR) per machine, in the report and on the dashboard.
- Learns from the log which faults spread to other machines, by comparing how
  often each fault is followed by another stop with chance. The result is shown
  next to the reviewed list in `knowledge.py`; `--learn-chains` uses it instead.
- 28 tests (was 16).

### Found along the way

- On the sample data, fieldbus timeouts never start a chain on their own, although
  `knowledge.py` lists them as able to. They stay in the list, and the report now
  shows the difference.
- A single coincidence in a short log gives a huge lift, so a fault now has to be
  followed by another stop at least twice before it counts as spreading.

## 1.0.0 (2026-10-30)

First release.

- Reads robot cell logs, skips and counts broken lines
- Finds every stoppage, from fault to resume, without double counting
- Groups chains of faults behind the fault that caused them (power dips, bus timeouts)
- Ranks problems by downtime, with first checks from a small fault knowledge base
- Flags faults that are getting more frequent
- Availability and mean time between failures per machine
- Markdown and JSON report, plus a dashboard on GitHub Pages
- Daily GitHub Actions run, 16 tests

### Fixed before release

- Faults that only happened close together in time were grouped as one chain
  (a light curtain trip on R3 and a gripper fault on R2). Now only faults that
  can actually spread through the cell can start a chain.
