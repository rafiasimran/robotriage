"""Read robot cell log lines into simple records.

Each line looks like this:

    2026-10-19 06:14:03.120 | R2 | FAULT | E-GRIP-01 | Vacuum below threshold (-0.42 bar)

Fields: timestamp | device | level | code | message
"""

from dataclasses import dataclass
from datetime import datetime

LEVELS = {"INFO", "WARN", "FAULT"}
TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


@dataclass
class Event:
    time: datetime
    device: str
    level: str
    code: str
    message: str


def parse_line(line: str) -> Event | None:
    """Turn one log line into an Event, or return None if the line is broken."""
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != 5:
        return None
    stamp, device, level, code, message = parts
    if level not in LEVELS or not device or not code:
        return None
    try:
        time = datetime.strptime(stamp, TIME_FORMAT)
    except ValueError:
        return None
    return Event(time, device, level, code, message)


def parse_lines(lines) -> tuple[list[Event], int]:
    """Parse many lines. Returns (events sorted by time, number of broken lines).

    Real logs always contain a few garbled lines (a reboot mid-write, a
    truncated buffer). We skip them but count them, so the report can say
    how much of the log could not be read.
    """
    events, broken = [], 0
    for line in lines:
        if not line.strip():
            continue
        event = parse_line(line)
        if event is None:
            broken += 1
        else:
            events.append(event)
    events.sort(key=lambda e: e.time)
    return events, broken


def read_log(path: str) -> tuple[list[Event], int]:
    with open(path, encoding="utf-8", errors="replace") as f:
        return parse_lines(f)
