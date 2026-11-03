from datetime import datetime

from robotriage import shifts
from robotriage.parse import parse_lines
from robotriage.triage import availability, cascades, mark_planned, mtbf, rank_issues, stoppages

DAY = datetime(2026, 10, 19)


def log(*rows):
    lines = [f"2026-10-19 {t}.000 | {d} | {lvl} | {code} | test" for t, d, lvl, code in rows]
    return parse_lines(lines)[0]


def test_daily_and_one_off_windows_are_merged():
    cal = {"daily": [["12:00", "12:30", "Lunch"]], "once": [["2026-10-19 12:15", "2026-10-19 13:00", "Changeover"]]}
    wins = shifts.windows(cal, DAY, DAY.replace(hour=23))
    assert [(a.strftime("%H:%M"), b.strftime("%H:%M")) for a, b, _ in wins] == [("12:00", "13:00")]
    assert shifts.total_s(wins) == 3600


def test_window_over_midnight():
    wins = shifts.windows({"daily": [["23:30", "00:30"]]}, DAY, datetime(2026, 10, 20, 6))
    assert shifts.total_s(wins) == 3600


def test_stop_during_a_break_is_not_lost_time():
    events = log(("11:50:00", "R1", "FAULT", "E-SAFE-01"), ("12:20:00", "R1", "INFO", "RESUME"),
                 ("23:59:00", "R1", "INFO", "CYCLE_OK"))
    stops = stoppages(events)
    wins = shifts.windows({"daily": [["12:00", "12:30"]]}, events[0].time, events[-1].time)
    mark_planned(stops, wins)
    assert stops[0].minutes == 30 and stops[0].lost_minutes == 10
    issues = rank_issues(*cascades(stops))
    assert issues[0].total_minutes == 10


def test_availability_uses_planned_production_time():
    events = log(("00:00:00", "R1", "INFO", "START"), ("10:00:00", "R1", "FAULT", "E-COLL-01"),
                 ("11:00:00", "R1", "INFO", "RESUME"), ("20:00:00", "R1", "INFO", "CYCLE_OK"))
    stops = stoppages(events)
    start, end = events[0].time, events[-1].time
    # 20 h logged, 1 h lost: 95 % without a calendar
    assert availability(stops, {"R1"}, start, end)["R1"] == 95.0
    # with 10 h planned off, the same lost hour is 1 h out of 10 h planned production
    assert availability(stops, {"R1"}, start, end, planned_s=10 * 3600)["R1"] == 90.0


def test_mttr_is_average_lost_time_per_stop():
    events = log(("01:00:00", "R2", "FAULT", "E-GRIP-01"), ("01:04:00", "R2", "INFO", "RESUME"),
                 ("05:00:00", "R2", "FAULT", "E-GRIP-01"), ("05:08:00", "R2", "INFO", "RESUME"),
                 ("09:00:00", "R1", "INFO", "CYCLE_OK"))
    stops = stoppages(events)
    m = mtbf(stops, {"R1", "R2"}, events[0].time, events[-1].time)
    assert m["R2"]["mttr_min"] == 6.0
    assert m["R1"] == {"stops": 0, "mtbf_h": None, "mttr_min": None}
