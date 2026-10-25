from robotriage.parse import parse_line, parse_lines

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
