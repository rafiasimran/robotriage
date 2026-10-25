"""Run the full triage on a log file.

    python -m robotriage logs/cell_week.log --out reports
"""

import argparse
from pathlib import Path

from . import report
from .parse import read_log
from .triage import availability, cascades, daily_counts, rank_issues, stoppages, worsening


def analyse(path: str, window_s: float = 10) -> dict:
    events, broken = read_log(path)
    if not events:
        raise SystemExit(f"No readable events in {path}")
    stops = stoppages(events)
    groups, alone = cascades(stops, window_s)
    issues = rank_issues(groups, alone)
    devices = {e.device for e in events}
    start, end = events[0].time, events[-1].time
    return {
        "source": Path(path).name,
        "period": f"{start:%d %b %Y} – {end:%d %b %Y}",
        "lines_ok": len(events),
        "lines_broken": broken,
        "n_stops": len(stops),
        "downtime_min": round(sum(s.minutes for s in stops), 1),
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
        "worsening": worsening(stops),
        "availability": availability(stops, devices, start, end),
        "stops_per_day": daily_counts(stops),
    }


def main():
    p = argparse.ArgumentParser(description="Triage a robot cell log: what stopped, why, and what to fix first.")
    p.add_argument("log")
    p.add_argument("--out", default="reports", help="folder for report.md and report.json")
    p.add_argument("--window", type=float, default=10, help="seconds between faults to count as one chain")
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    result = analyse(a.log, a.window)
    report.write(result, out / "report.md", out / "report.json")
    top = result["issues"][0]
    print(f"{result['n_stops']} stoppages, {result['downtime_min']:.0f} min downtime. "
          f"Top issue: {top['code']} ({top['total_min']:.0f} min). Report: {out / 'report.md'}")


if __name__ == "__main__":
    main()
