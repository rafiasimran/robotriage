from robotriage.parse import parse_csv_rows, parse_line, parse_lines, read_log
from robotriage.triage import stoppages

GOOD = "2026-10-19 06:14:03.120 | R2 | FAULT | E-GRIP-01 | Vacuum below threshold (-0.42 bar)"


def test_good_line_is_parsed():
    e = parse_line(GOOD)
    assert e.device == "R2"
    assert e.level == "FAULT"
    assert e.code == "E-GRIP-01"
    assert e.time.hour == 6 and e.time.microsecond == 120000


def test_broken_lines_are_skipped_and_counted():
    lines = [
        GOOD,
        "2026-10-19 06:1",                                      # truncated
        "2026-10-19 06:15:00.000 | R2 | PANIC | X | bad level",  # unknown level
        "not a timestamp | R1 | INFO | RESUME | ok",            # bad time
        "",                                                     # empty lines are ignored, not counted
    ]
    events, broken = parse_lines(lines)
    assert len(events) == 1
    assert broken == 3


def test_events_come_back_sorted_by_time():
    late = "2026-10-19 08:00:00.000 | R1 | INFO | RESUME | ok"
    early = "2026-10-19 07:00:00.000 | R1 | FAULT | E-COLL-01 | hit"
    events, _ = parse_lines([late, early])
    assert [e.code for e in events] == ["E-COLL-01", "RESUME"]


# ---------- CSV alarm history ----------

def test_alarm_came_and_went_make_one_stoppage():
    rows = [
        {"time": "2026-10-19 10:00:00", "device": "R1", "code": "E-COLL-01", "state": "came", "message": "hit"},
        {"time": "2026-10-19 10:12:00", "device": "R1", "code": "E-COLL-01", "state": "went", "message": ""},
    ]
    events, broken = parse_csv_rows(rows)
    assert broken == 0
    stops = stoppages(events)
    assert len(stops) == 1 and stops[0].minutes == 12 and stops[0].code == "E-COLL-01"


def test_csv_column_names_can_be_mapped():
    rows = [{"Timestamp": "19.10.2026 10:00:00", "Source": "R2", "AlarmID": "E-GRIP-01", "Event": "Raised"}]
    events, broken = parse_csv_rows(rows, {"time": "Timestamp", "device": "Source", "code": "AlarmID", "state": "Event"})
    assert broken == 0 and events[0].device == "R2" and events[0].level == "FAULT"


def test_bad_csv_rows_are_skipped_and_counted():
    rows = [
        {"time": "not a time", "device": "R1", "code": "X", "state": "on"},
        {"time": "2026-10-19 10:00:00", "device": "", "code": "X", "state": "on"},
        {"time": "2026-10-19 10:00:00", "device": "R1", "code": "X", "state": "maybe"},
        {"time": "2026-10-19 10:00:00", "device": "R1", "code": "X", "state": "on"},
    ]
    events, broken = parse_csv_rows(rows)
    assert len(events) == 1 and broken == 3


def test_csv_file_is_picked_by_extension(tmp_path):
    path = tmp_path / "alarms.csv"
    path.write_text("time;device;code;state\n2026-10-19 10:00:00;R1;E-SAFE-01;on\n"
                    "2026-10-19 10:02:00;R1;E-SAFE-01;off\n", encoding="utf-8")
    events, broken = read_log(str(path))
    assert broken == 0 and [e.level for e in events] == ["FAULT", "INFO"]
