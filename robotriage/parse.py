"""Read machine logs into simple records.

Two formats are supported.

1. The cell log written by simulate.py, one event per line:

    2026-10-19 06:14:03.120 | R2 | FAULT | E-GRIP-01 | Vacuum below threshold (-0.42 bar)

   Fields: timestamp | device | level | code | message

2. A CSV alarm history, the kind most HMI and SCADA systems can export.
   Each row is one alarm going on or off ("came" / "went"). See read_csv.
"""

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

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


# ---------- CSV alarm history ----------

# Column names in the CSV. Override them with --columns when an export uses
# other names, e.g. time=Timestamp,device=Source,code=AlarmID
CSV_COLUMNS = {"time": "time", "device": "device", "code": "code",
               "state": "state", "level": "level", "message": "message"}

# An alarm history row says whether the alarm came on or went off. Vendors
# spell this differently, so accept the common words.
ON = {"on", "came", "come", "raised", "active", "set", "1", "true", "incoming"}
OFF = {"off", "went", "gone", "cleared", "inactive", "reset", "0", "false", "outgoing"}

CSV_TIME_FORMATS = ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S", "%d.%m.%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S")


def _csv_time(text: str) -> datetime | None:
    text = text.strip().replace("Z", "")
    for fmt in CSV_TIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def parse_csv_rows(rows, columns: dict | None = None) -> tuple[list[Event], int]:
    """Turn CSV alarm rows into Events.

    An alarm coming on becomes a FAULT. An alarm going off becomes a RESUME
    for that device, so the rest of the triage works unchanged. If the export
    has no state column, every row is taken as given by its level column
    (FAULT, WARN or INFO), or as a FAULT if there is no level either.
    Rows with a missing time, device or code, or an unknown state, are
    skipped and counted, like broken lines in the text log.
    """
    col = {**CSV_COLUMNS, **(columns or {})}
    events, broken = [], 0
    for row in rows:
        row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
        time = _csv_time(row.get(col["time"], ""))
        device, code = row.get(col["device"], ""), row.get(col["code"], "")
        if time is None or not device or not code:
            broken += 1
            continue
        message = row.get(col["message"], "")
        state = row.get(col["state"], "").lower()
        if state:
            if state in ON:
                events.append(Event(time, device, "FAULT", code, message))
            elif state in OFF:
                events.append(Event(time, device, "INFO", "RESUME", f"{code} cleared"))
            else:
                broken += 1
            continue
        level = row.get(col["level"], "").upper() or "FAULT"
        if level not in LEVELS:
            broken += 1
            continue
        events.append(Event(time, device, level, code, message))
    events.sort(key=lambda e: e.time)
    return events, broken


def read_csv(path: str, columns: dict | None = None) -> tuple[list[Event], int]:
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return parse_csv_rows(csv.DictReader(f, dialect=dialect), columns)


def read_log(path: str, fmt: str = "auto", columns: dict | None = None) -> tuple[list[Event], int]:
    """Read a log file. fmt is 'text', 'csv' or 'auto' (by file extension)."""
    if fmt == "csv" or (fmt == "auto" and Path(path).suffix.lower() == ".csv"):
        return read_csv(path, columns)
    with open(path, encoding="utf-8", errors="replace") as f:
        return parse_lines(f)
