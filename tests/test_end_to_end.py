"""Run the whole pipeline on a simulated week and check it finds the problems hidden in it."""

from datetime import datetime

from robotriage.__main__ import analyse
from robotriage.report import build
from robotriage.simulate import generate


def week(tmp_path, seed=7, learn_chains=False):
    path = tmp_path / "cell.log"
    path.write_text("\n".join(generate(datetime(2026, 10, 19), days=7, seed=seed)) + "\n", encoding="utf-8")
    return analyse(str(path), learn_chains=learn_chains)


def test_finds_the_hidden_problems(tmp_path):
    r = week(tmp_path)
    codes = [i["code"] for i in r["issues"]]
    # The wearing gripper and the power dips are the two biggest problems.
    assert set(codes[:2]) == {"E-GRIP-01", "E-PWR-01"}
    # Network timeouts never appear as their own issue: they are charged to the power dips.
    assert "E-COMM-02" not in codes
    # Both power dips are found as chains with the PLC as root.
    assert len(r["cascades"]) == 2
    assert all(c["root_code"] == "E-PWR-01" for c in r["cascades"])
    # The gripper is flagged as getting worse.
    assert any(w["device"] == "R2" and w["code"] == "E-GRIP-01" for w in r["worsening"])
    # Garbled lines are counted, not silently dropped.
    assert r["lines_broken"] > 0


def test_works_for_other_seeds(tmp_path):
    for seed in (1, 2, 3):
        r = week(tmp_path, seed)
        assert len(r["cascades"]) == 2
        assert "E-COMM-02" not in [i["code"] for i in r["issues"]]


def test_learning_from_the_log_finds_the_same_chains(tmp_path):
    for seed in (7, 1, 2, 3):
        r = week(tmp_path, seed, learn_chains=True)
        assert [x["code"] for x in r["learned_spreaders"] if x["spreads"]] == ["E-PWR-01"]
        assert len(r["cascades"]) == 2
        assert r["issues"] == week(tmp_path, seed)["issues"]


def test_report_has_all_sections(tmp_path):
    text = build(week(tmp_path))
    for heading in ("## Fix these first", "## One cause, many alarms", "## Getting worse", "## Availability"):
        assert heading in text
