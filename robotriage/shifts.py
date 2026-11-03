"""Planned stops: breaks, changeovers and planned maintenance.

A machine standing still during a planned break costs no production, so it
should not count against availability or be ranked as a problem. Plants
measure availability against planned production time, not against the clock.

The calendar is a small JSON file:

    {
      "daily": [["12:00", "12:30", "Lunch break"], ["20:00", "20:30", "Shift handover"]],
      "once":  [["2026-10-21 06:00", "2026-10-21 10:00", "Planned maintenance R4"]]
    }

"daily" windows repeat every day. "once" windows are single dates, for
changeovers and maintenance. Without a calendar every hour counts as planned
production, which is right for a cell running 24/7.
"""

import json
from datetime import datetime, timedelta

Window = tuple[datetime, datetime, str]


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def windows(calendar: dict, start: datetime, end: datetime) -> list[Window]:
    """All planned windows that touch the period start..end, merged where they overlap."""
    found: list[Window] = []
    day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    while day <= end:
        for a, b, *label in calendar.get("daily", []):
            ws = datetime.combine(day.date(), datetime.strptime(a, "%H:%M").time())
            we = datetime.combine(day.date(), datetime.strptime(b, "%H:%M").time())
            if we <= ws:                      # a window over midnight, e.g. 23:30-00:15
                we += timedelta(days=1)
            found.append((ws, we, label[0] if label else "planned"))
        day += timedelta(days=1)
    for a, b, *label in calendar.get("once", []):
        found.append((datetime.fromisoformat(a), datetime.fromisoformat(b), label[0] if label else "planned"))

    clipped = sorted((max(a, start), min(b, end), lab) for a, b, lab in found if b > start and a < end)
    merged: list[Window] = []
    for a, b, lab in clipped:
        if merged and a <= merged[-1][1]:
            pa, pb, plab = merged[-1]
            merged[-1] = (pa, max(pb, b), plab)
        else:
            merged.append((a, b, lab))
    return merged


def overlap_s(start: datetime, end: datetime, wins: list[Window]) -> float:
    """Seconds of start..end that fall inside planned windows."""
    return sum(max(0.0, (min(end, b) - max(start, a)).total_seconds()) for a, b, _ in wins)


def total_s(wins: list[Window]) -> float:
    return sum((b - a).total_seconds() for a, b, _ in wins)
