"""Generate a realistic log for a robot cell running 24/7.

The cell: four robots (R1-R4), a conveyor (CV1) and the cell controller (PLC).
Real production logs are confidential, so this simulator writes the kind of
log a cell like this produces, with problems hidden in it on purpose:

- R2's gripper vacuum faults become more frequent every day (a wearing suction cup)
- two supply voltage dips at the PLC knock out the fieldbus on the other robots
  within seconds (one root cause, several faults on screen)
- R4's joint 3 overheats after long runs of heavy parts
- the usual background: light curtain trips, a conveyor jam, a collision
- a few garbled lines, like any real log

The same seed always gives the same log, so results are reproducible.
"""

import argparse
import random
from datetime import datetime, timedelta

ROBOTS = ["R1", "R2", "R3", "R4"]


def line(t: datetime, device: str, level: str, code: str, msg: str) -> tuple:
    return (t, f"{t:%Y-%m-%d %H:%M:%S}.{t.microsecond // 1000:03d} | {device} | {level} | {code} | {msg}")


def stop(rows, t, device, code, msg, minutes, rng, warn=None, downs=None):
    """A fault, an optional warning before it, a reset and a resume."""
    if warn:
        rows.append(line(t - timedelta(seconds=rng.randint(20, 90)), device, "WARN", code, warn))
    rows.append(line(t, device, "FAULT", code, msg))
    reset = t + timedelta(minutes=minutes * rng.uniform(0.6, 0.8))
    rows.append(line(reset, device, "INFO", "RESET", "Fault acknowledged by operator"))
    rows.append(line(t + timedelta(minutes=minutes), device, "INFO", "RESUME", "Back in automatic mode"))
    if downs is not None:
        downs.append((device, t, t + timedelta(minutes=minutes)))


def generate(start: datetime, days: int = 7, seed: int = 7) -> list[str]:
    rng = random.Random(seed)
    rows = []
    downs = []  # (device, start, end) of every stop, to remove cycle reports while stopped
    end = start + timedelta(days=days)

    # Normal production: a cycle summary from each robot every 10 minutes.
    t = start
    while t < end:
        for r in ROBOTS:
            jitter = timedelta(seconds=rng.randint(0, 59))
            cycle = round(rng.gauss(42 if r != "R4" else 55, 1.5), 1)
            rows.append(line(t + jitter, r, "INFO", "CYCLE_OK", f"Last 10 min: {rng.randint(13, 15)} parts, avg cycle {cycle} s"))
        t += timedelta(minutes=10)
    rows.append(line(start, "PLC", "INFO", "START", "Cell started in automatic mode"))

    def at(day, hour, minute=0):
        return start + timedelta(days=day, hours=hour, minutes=minute, seconds=rng.randint(0, 59), milliseconds=rng.randint(0, 999))

    # 1. R2 gripper: 1 fault on day 1, rising to about 6 on day 7.
    for day in range(days):
        for _ in range(day + 1 + rng.randint(-1, 0)):
            t = at(day, rng.randint(0, 23), rng.randint(0, 59))
            p = round(rng.uniform(-0.48, -0.40), 2)
            stop(rows, t, "R2", "E-GRIP-01", f"Vacuum below threshold ({p} bar)", rng.uniform(3, 8), rng, downs=downs,
                 warn=f"Vacuum weak ({round(p - 0.12, 2)} bar)")

    # 2. Two supply dips at the PLC -> fieldbus timeouts on R1, R3, R4 within seconds.
    for day in (2, 5):
        t = at(day, rng.choice([6, 14, 22]), rng.randint(0, 5))
        stop(rows, t, "PLC", "E-PWR-01", f"Supply voltage dip ({rng.randint(171, 184)} V)", rng.uniform(2, 4), rng, downs=downs)
        for r in ("R1", "R3", "R4"):
            tr = t + timedelta(milliseconds=rng.randint(800, 4000))
            stop(rows, tr, r, "E-COMM-02", "Fieldbus timeout: no response from cell controller", rng.uniform(12, 20), rng, downs=downs)

    # 3. R4 joint 3 over-temperature after heavy-payload runs.
    for day in (1, 3, 6):
        t = at(day, rng.randint(10, 16), rng.randint(0, 59))
        rows.append(line(t - timedelta(minutes=45), "R4", "INFO", "PAYLOAD", "Switched to heavy part family (18 kg)"))
        temp = rng.randint(86, 92)
        stop(rows, t, "R4", "E-JNT-03", f"Joint 3 motor temperature {temp} °C (limit 85 °C)", rng.uniform(20, 35), rng, downs=downs,
             warn=f"Joint 3 motor temperature {temp - 6} °C")

    # 4. Background faults.
    for day in range(days):
        if rng.random() < 0.8:
            stop(rows, at(day, rng.randint(0, 23), rng.randint(0, 59)), rng.choice(ROBOTS), "E-SAFE-01",
                 "Light curtain interrupted, safe stop", rng.uniform(1, 3), rng, downs=downs)
    stop(rows, at(4, 9, 12), "R1", "E-COLL-01", "Collision detected on axis 2, torque 140% of model", 25, rng, downs=downs)
    for day in (0, 3, 5):
        stop(rows, at(day, rng.randint(0, 23), rng.randint(0, 59)), "CV1", "E-CONV-01",
             "Conveyor jam at transfer point 2", rng.uniform(4, 10), rng, downs=downs)

    # A stopped robot does not report finished cycles.
    def running(row):
        t, text = row
        if "| CYCLE_OK |" not in text:
            return True
        dev = text.split(" | ")[1]
        return not any(d == dev and a <= t <= b for d, a, b in downs)

    rows = [r for r in rows if running(r)]
    rows.sort(key=lambda r: r[0])
    out = [text for _, text in rows]

    # 5. A few garbled lines, as in any real log.
    for _ in range(max(1, len(out) // 400)):
        i = rng.randrange(len(out))
        out[i] = out[i][: rng.randint(10, 30)]
    return out


def main():
    p = argparse.ArgumentParser(description="Write a simulated robot cell log.")
    p.add_argument("out", help="output log file")
    p.add_argument("--start", default="2026-10-19", help="first day, YYYY-MM-DD")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()
    lines = generate(datetime.fromisoformat(a.start), a.days, a.seed)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {len(lines)} lines to {a.out}")


if __name__ == "__main__":
    main()
