"""Run the full triage on a log file.

    python -m robotriage logs/cell_week.log --out reports
    python -m robotriage alarms.csv --columns time=Timestamp,device=Source,code=AlarmID,state=Event
    python -m robotriage logs/cell_week.log --calendar logs/shifts.json
    python -m robotriage logs/cell_week.log --learn-chains
"""

import argparse
from pathlib import Path

from . import report, shifts
from .parse import read_log
from .knowledge import CAN_CASCADE
from .triage import (availability, cascades, daily_counts, learn_spreaders, mark_planned, mtbf, rank_issues,
                     stoppages, worsening)


def analyse(path: str, window_s: float = 10, fmt: str = "auto", columns: dict | None = None,
            calendar: dict | None = None, learn_chains: bool = False) -> dict:
    events, broken = read_log(path, fmt, columns)
    if not events:
        raise SystemExit(f"No readable events in {path}")
    start, end = events[0].time, events[-1].time
    stops = stoppages(events)
    wins = shifts.windows(calendar, start, end) if calendar else []
    mark_planned(stops, wins)
    planned_s = shifts.total_s(wins)
    learned = learn_spreaders(stops, window_s)
    spreaders = {r["code"] for r in learned if r["spreads"]} if learn_chains else CAN_CASCADE
    groups, alone = cascades(stops, window_s, spreaders)
    issues = rank_issues(groups, alone)
    devices = {e.device for e in events}
    return {
        "source": Path(path).name,
        "period": f"{start:%d %b %Y} – {end:%d %b %Y}",
        "lines_ok": len(events),
        "lines_broken": broken,
        "n_stops": len(stops),
        "downtime_min": round(sum(s.lost_minutes for s in stops), 1),
        "planned_min": round(planned_s / 60, 1),
        "stopped_in_planned_min": round(sum(s.planned_s for s in stops) / 60, 1),
        "inferred_ends": sum(s.end_inferred for s in stops),
        "open_stops": sum(s.still_open for s in stops),
        "issues": [
            {"code": it.code, "devices": sorted(it.devices), "count": it.count,
             "own_min": round(it.own_minutes, 1), "caused_min": round(it.caused_minutes, 1),
             "total_min": round(it.total_minutes, 1)}
            for it in issues
        ],
        "cascades": [
            {"start": f"{c.root.start:%a %d %b %H:%M:%S}", "root_device": c.root.device, "root_code": c.root.code,
             "followers": [{"device": f.device, "code": f.code} for f in c.followers],
             "spread_s": round(max((f.start - c.root.start).total_seconds() for f in c.followers), 1),
             "minutes": round(c.minutes, 1)}
            for c in groups
        ],
        "chains_from": "the faults learned from this log" if learn_chains else "the list in knowledge.py",
        "learned_spreaders": [{**r, "in_knowledge": r["code"] in CAN_CASCADE}
                              for r in learned if r["spreads"] or r["code"] in CAN_CASCADE],
        "worsening": worsening(stops),
        "availability": availability(stops, devices, start, end, planned_s),
        "mtbf": mtbf(stops, devices, start, end, planned_s),
        "stops_per_day": daily_counts(stops),
    }


def main():
    p = argparse.ArgumentParser(description="Triage a robot cell log: what stopped, why, and what to fix first.")
    p.add_argument("log")
    p.add_argument("--out", default="reports", help="folder for report.md and report.json")
    p.add_argument("--window", type=float, default=10, help="seconds between faults to count as one chain")
    p.add_argument("--format", choices=["auto", "text", "csv"], default="auto",
                   help="log format; auto picks csv for .csv files")
    p.add_argument("--columns", default="",
                   help="CSV column names if they differ, e.g. time=Timestamp,device=Source,code=AlarmID,state=Event")
    p.add_argument("--calendar", help="JSON file with planned breaks, changeovers and maintenance (see shifts.py)")
    p.add_argument("--learn-chains", action="store_true",
                   help="decide which faults start a chain from this log instead of the list in knowledge.py")
    a = p.parse_args()
    columns = dict(pair.split("=", 1) for pair in a.columns.split(",") if "=" in pair)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    result = analyse(a.log, a.window, a.format, columns, shifts.load(a.calendar) if a.calendar else None,
                     a.learn_chains)
    report.write(result, out / "report.md", out / "report.json")
    top = result["issues"][0]
    print(f"{result['n_stops']} stoppages, {result['downtime_min']:.0f} min downtime. "
          f"Top issue: {top['code']} ({top['total_min']:.0f} min). Report: {out / 'report.md'}")


if __name__ == "__main__":
    main()
