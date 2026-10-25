from robotriage.parse import parse_lines
from robotriage.triage import cascades, rank_issues, stoppages, worsening


def log(*rows):
    """rows are (time 'HH:MM:SS', device, level, code). All on the same day."""
    lines = [f"2026-10-19 {t}.000 | {d} | {lvl} | {code} | test" for t, d, lvl, code in rows]
    events, _ = parse_lines(lines)
    return events


def test_fault_and_resume_make_one_stoppage():
    stops = stoppages(log(("10:00:00", "R1", "FAULT", "E-COLL-01"), ("10:25:00", "R1", "INFO", "RESUME")))
    assert len(stops) == 1
    assert stops[0].minutes == 25
    assert not stops[0].end_inferred


def test_second_fault_while_stopped_is_not_double_counted():
    stops = stoppages(log(
        ("10:00:00", "R1", "FAULT", "E-COLL-01"),
        ("10:05:00", "R1", "FAULT", "E-SAFE-01"),
        ("10:20:00", "R1", "INFO", "RESUME"),
    ))
    assert len(stops) == 1
    assert stops[0].code == "E-COLL-01"
    assert stops[0].minutes == 20


def test_missing_resume_ends_at_next_cycle_report():
    stops = stoppages(log(("10:00:00", "R2", "FAULT", "E-GRIP-01"), ("10:08:00", "R2", "INFO", "CYCLE_OK")))
    assert stops[0].minutes == 8
    assert stops[0].end_inferred


def test_fault_without_any_end_is_marked_open():
    stops = stoppages(log(("10:00:00", "R3", "FAULT", "E-JNT-03"), ("11:00:00", "R1", "INFO", "CYCLE_OK")))
    assert stops[0].still_open
    assert stops[0].minutes == 60


def test_power_dip_cascade_charges_downtime_to_root_cause():
    events = log(
        ("14:00:00", "PLC", "FAULT", "E-PWR-01"),
        ("14:00:02", "R1", "FAULT", "E-COMM-02"),
        ("14:00:03", "R3", "FAULT", "E-COMM-02"),
        ("14:03:00", "PLC", "INFO", "RESUME"),
        ("14:15:00", "R1", "INFO", "RESUME"),
        ("14:15:00", "R3", "INFO", "RESUME"),
    )
    groups, alone = cascades(stoppages(events), window_s=10)
    assert len(groups) == 1 and not alone
    assert groups[0].root.code == "E-PWR-01"
    issues = rank_issues(groups, alone)
    assert [i.code for i in issues] == ["E-PWR-01"]   # no separate network problem
    assert issues[0].caused_minutes > issues[0].own_minutes


def test_faults_far_apart_are_not_a_cascade():
    events = log(
        ("09:00:00", "R1", "FAULT", "E-SAFE-01"), ("09:02:00", "R1", "INFO", "RESUME"),
        ("09:01:00", "R2", "FAULT", "E-GRIP-01"), ("09:05:00", "R2", "INFO", "RESUME"),
    )
    groups, alone = cascades(stoppages(events), window_s=10)
    assert groups == [] and len(alone) == 2


def test_rising_fault_is_flagged_as_worsening():
    rows = []
    # 1 fault in the first half of the day, 5 in the second half.
    for t in ["01:00:00", "13:00:00", "15:00:00", "17:00:00", "19:00:00", "21:00:00"]:
        rows.append((t, "R2", "FAULT", "E-GRIP-01"))
        rows.append((f"{t[:2]}:05:00", "R2", "INFO", "RESUME"))
    rows.append(("23:00:00", "R1", "FAULT", "E-SAFE-01"))
    rows.append(("23:01:00", "R1", "INFO", "RESUME"))
    found = worsening(stoppages(log(*rows)))
    assert found and found[0]["device"] == "R2" and found[0]["code"] == "E-GRIP-01"
