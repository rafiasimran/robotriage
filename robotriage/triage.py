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
    planned_s: float = 0.0  # part of the stop that fell inside a planned break

    @property
    def minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60

    @property
    def lost_minutes(self) -> float:
        """Production time actually lost: the stop minus any planned break inside it."""
        return self.minutes - self.planned_s / 60


@dataclass
class Cascade:
    root: Stoppage
    followers: list = field(default_factory=list)

    @property
    def minutes(self) -> float:
        return self.root.lost_minutes + sum(s.lost_minutes for s in self.followers)


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


def learn_spreaders(stops: list[Stoppage], window_s: float = 10, min_count: int = 2,
                    min_share: float = 0.5, min_lift: float = 10) -> list[dict]:
    """Learn from the log which fault codes knock out other machines.

    For each code, look at the stops where it came first, with no other
    machine already stopping in the seconds before it, and count how often a
    stop on a different machine followed within `window_s` seconds.

    That share is compared with chance: how likely is it that some other
    machine starts a stop in any `window_s`-second slot of this log? The
    ratio is the lift. A code is a candidate when it was followed by another
    stop at least `min_count` times, at least `min_share` of the time, and
    the lift is at least `min_lift`. Asking for repeats matters: in a short
    log a single coincidence already gives a huge lift.

    Looking only at stops that came first matters. Three robots losing the
    fieldbus within seconds all follow each other, but none of them caused
    the others; the power dip before them did.

    Returns every code with its numbers, sorted by lift, with a 'spreads'
    flag. An engineer should confirm the list before it replaces the fixed
    one in knowledge.py.
    """
    if len(stops) < 2:
        return []
    span = (stops[-1].start - stops[0].start).total_seconds() or 1
    chance = min(1.0, len(stops) * window_s / span)

    def gap(a, b):
        return (b.start - a.start).total_seconds()

    stats = defaultdict(lambda: {"count": 0, "first": 0, "followed": 0})
    for i, s in enumerate(stops):
        st = stats[s.code]
        st["count"] += 1
        before = any(0 < gap(p, s) <= window_s and p.device != s.device for p in stops[max(0, i - 50):i])
        if before:
            continue
        st["first"] += 1
        if any(0 <= gap(s, n) <= window_s and n.device != s.device for n in stops[i + 1:i + 51]):
            st["followed"] += 1

    out = []
    for code, st in stats.items():
        share = st["followed"] / st["count"]
        lift = share / chance
        out.append({"code": code, "count": st["count"], "followed": st["followed"],
                    "share": round(share, 2), "lift": round(lift, 1),
                    "spreads": st["followed"] >= min_count and share >= min_share and lift >= min_lift})
    return sorted(out, key=lambda r: (-r["lift"], r["code"]))


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
        it.own_minutes += s.lost_minutes
    for c in groups:
        it = issue(c.root.code)
        it.devices.add(c.root.device)
        it.count += 1
        it.own_minutes += c.root.lost_minutes
        it.caused_minutes += sum(f.lost_minutes for f in c.followers)
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


def mark_planned(stops: list[Stoppage], wins) -> None:
    """Record how much of each stop fell inside a planned window (see shifts.py)."""
    from .shifts import overlap_s
    for s in stops:
        s.planned_s = overlap_s(s.start, s.end, wins)


def availability(stops: list[Stoppage], devices: set[str], start: datetime, end: datetime,
                 planned_s: float = 0.0) -> dict[str, float]:
    """Share of planned production time each device was running (0-100%).

    Planned production time is the logged period minus planned breaks.
    Only lost time counts against it, so a stop during a break does not.
    """
    production = ((end - start).total_seconds() - planned_s) or 1
    lost = defaultdict(float)
    for s in stops:
        lost[s.device] += s.lost_minutes * 60
    return {d: round(100 * (1 - lost[d] / production), 1) for d in sorted(devices)}


def mtbf(stops: list[Stoppage], devices: set[str], start: datetime, end: datetime,
         planned_s: float = 0.0) -> dict[str, dict]:
    """Mean time between failures (hours) and mean time to repair (minutes) per machine.

    Running time is planned production time minus the time lost to stops.
    MTBF = running time / number of stops, MTTR = lost time / number of stops.
    Machines that never stopped get None for both, because the period is too
    short to say anything about them.
    """
    production_h = ((end - start).total_seconds() - planned_s) / 3600
    count = defaultdict(int)
    lost_min = defaultdict(float)
    for s in stops:
        count[s.device] += 1
        lost_min[s.device] += s.lost_minutes
    out = {}
    for d in sorted(devices):
        n = count[d]
        out[d] = {"stops": n,
                  "mtbf_h": round((production_h - lost_min[d] / 60) / n, 1) if n else None,
                  "mttr_min": round(lost_min[d] / n, 1) if n else None}
    return out


def daily_counts(stops: list[Stoppage]) -> dict[str, int]:
    days = defaultdict(int)
    for s in stops:
        days[s.start.date().isoformat()] += 1
    return dict(sorted(days.items()))
