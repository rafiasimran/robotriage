"""Turn parsed events into findings an engineer can act on.

Four questions, answered in order:
1. When was each machine stopped, and for how long?   -> stoppages()
2. Which faults were caused by another fault?          -> cascades()
3. Which problems cost the most production time?       -> rank_issues()
4. Which problems are getting worse?                   -> worsening()
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from .knowledge import CAN_CASCADE
from .parse import Event

RESUME = "RESUME"
RUNNING = "CYCLE_OK"  # a finished-cycle report proves the machine was running again


@dataclass
class Stoppage:
    device: str
    code: str
    start: datetime
    end: datetime
    still_open: bool = False
    end_inferred: bool = False

    @property
    def minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60


@dataclass
class Cascade:
    root: Stoppage
    followers: list = field(default_factory=list)

    @property
    def minutes(self) -> float:
        return self.root.minutes + sum(s.minutes for s in self.followers)


def stoppages(events: list[Event]) -> list[Stoppage]:
    """Pair each FAULT with the next RESUME on the same device.

    A second fault on a machine that is already stopped does not start a new
    stoppage, otherwise the same downtime would be counted twice.

    If the RESUME line is missing (a garbled line, a logger restart), the
    stop is closed at the next finished-cycle report from that machine and
    marked as inferred. Without this, one lost line would count days of
    downtime. A fault with no end at all is kept and marked as still open.
    """
    open_stops: dict[str, Stoppage] = {}
    done: list[Stoppage] = []
    for e in events:
        if e.level == "FAULT" and e.device not in open_stops:
            open_stops[e.device] = Stoppage(e.device, e.code, e.time, e.time)
        elif e.code in (RESUME, RUNNING) and e.device in open_stops:
            stop = open_stops.pop(e.device)
            stop.end = e.time
            stop.end_inferred = e.code == RUNNING
            done.append(stop)
    if events:
        last = events[-1].time
        for stop in open_stops.values():
            stop.end = last
            stop.still_open = True
            done.append(stop)
    return sorted(done, key=lambda s: s.start)


def cascades(stops: list[Stoppage], window_s: float = 10,
             can_start: set[str] = CAN_CASCADE) -> tuple[list[Cascade], list[Stoppage]]:
    """Group stoppages that start within `window_s` seconds after a fault that can spread.

    Only faults in `can_start` (power dips, bus timeouts) can be the root of a
    chain. Timing alone is not proof of cause: a light curtain trip on one
    robot and a gripper fault on the next one a few seconds later are a
    coincidence, not a chain. Returns (cascades, stoppages on their own).
    """
    groups, used = [], set()
    for i, root in enumerate(stops):
        if i in used or root.code not in can_start:
            continue
        followers, devices = [], {root.device}
        j = i + 1
        while j < len(stops) and (stops[j].start - root.start).total_seconds() <= window_s:
            if j not in used and stops[j].device not in devices:
                followers.append(stops[j])
                devices.add(stops[j].device)
                used.add(j)
            j += 1
        if followers:
            used.add(i)
            groups.append(Cascade(root, followers))
    alone = [s for k, s in enumerate(stops) if k not in used]
    return groups, alone


@dataclass
class Issue:
    code: str
    devices: set
    count: int
    own_minutes: float
    caused_minutes: float

    @property
    def total_minutes(self) -> float:
        return self.own_minutes + self.caused_minutes


def rank_issues(groups: list[Cascade], alone: list[Stoppage]) -> list[Issue]:
    """Rank fault codes by the production time they cost.

    Downtime of follow-on faults is charged to the root cause. A network
    timeout caused by a power dip is a power problem, not a network problem.
    """
    by_code: dict[str, Issue] = {}

    def issue(code):
        if code not in by_code:
            by_code[code] = Issue(code, set(), 0, 0.0, 0.0)
        return by_code[code]

    for s in alone:
        it = issue(s.code)
        it.devices.add(s.device)
        it.count += 1
        it.own_minutes += s.minutes
    for c in groups:
        it = issue(c.root.code)
        it.devices.add(c.root.device)
        it.count += 1
        it.own_minutes += c.root.minutes
        it.caused_minutes += sum(f.minutes for f in c.followers)
    return sorted(by_code.values(), key=lambda it: it.total_minutes, reverse=True)


def worsening(stops: list[Stoppage], min_count: int = 4) -> list[dict]:
    """Find device + fault combinations that happen more often in the second half of the log.

    Simple on purpose: split the time range in two and compare counts.
    Flag it if the second half has at least twice as many as the first.
    """
    if not stops:
        return []
    start, end = stops[0].start, stops[-1].start
    middle = start + (end - start) / 2
    counts = defaultdict(lambda: [0, 0])
    for s in stops:
        counts[(s.device, s.code)][0 if s.start < middle else 1] += 1
    found = []
    for (device, code), (first, second) in counts.items():
        if first + second >= min_count and second >= 2 * max(first, 1):
            found.append({"device": device, "code": code, "first_half": first, "second_half": second})
    return sorted(found, key=lambda f: f["second_half"], reverse=True)


def availability(stops: list[Stoppage], devices: set[str], start: datetime, end: datetime) -> dict[str, float]:
    """Share of the logged time each device was not stopped (0-100%)."""
    span = (end - start).total_seconds() or 1
    down = defaultdict(float)
    for s in stops:
        down[s.device] += (s.end - s.start).total_seconds()
    return {d: round(100 * (1 - down[d] / span), 1) for d in sorted(devices)}


def mtbf(stops: list[Stoppage], devices: set[str], start: datetime, end: datetime) -> dict[str, dict]:
    """Mean time between failures per machine, in hours.

    Running time is the logged period minus the time the machine was stopped.
    MTBF = running time / number of stops. Machines that never stopped get None,
    because the period is too short to say anything about them.
    """
    span_h = (end - start).total_seconds() / 3600
    count = defaultdict(int)
    down_h = defaultdict(float)
    for s in stops:
        count[s.device] += 1
        down_h[s.device] += (s.end - s.start).total_seconds() / 3600
    out = {}
    for d in sorted(devices):
        n = count[d]
        out[d] = {"stops": n, "mtbf_h": round((span_h - down_h[d]) / n, 1) if n else None}
    return out


def daily_counts(stops: list[Stoppage]) -> dict[str, int]:
    days = defaultdict(int)
    for s in stops:
        days[s.start.date().isoformat()] += 1
    return dict(sorted(days.items()))
