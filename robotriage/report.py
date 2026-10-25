"""Write the triage results as a Markdown report and a JSON file."""

import json

from .knowledge import describe


def _h(minutes: float) -> str:
    """Format minutes as '1 h 25 min' or '7 min'."""
    m = round(minutes)
    return f"{m // 60} h {m % 60} min" if m >= 60 else f"{m} min"


def build(result: dict) -> str:
    r = result
    out = []
    out.append(f"# Robot cell triage report: {r['period']}\n")
    out.append(f"Log lines read: {r['lines_ok']:,} · unreadable lines skipped: {r['lines_broken']} · "
               f"stoppages found: {r['n_stops']} · total downtime: {_h(r['downtime_min'])}\n")

    out.append("## Fix these first\n")
    out.append("Ranked by production time lost. Downtime of follow-on faults is counted under the fault that caused them.\n")
    out.append("| # | Fault | Where | Times | Downtime | of which caused on other machines |")
    out.append("|---|---|---|---|---|---|")
    for i, it in enumerate(r["issues"][:5], 1):
        caused = _h(it["caused_min"]) if it["caused_min"] else "–"
        out.append(f"| {i} | {it['code']} {describe(it['code'])['name']} | {', '.join(it['devices'])} | "
                   f"{it['count']} | {_h(it['total_min'])} | {caused} |")
    out.append("")

    top = r["issues"][0] if r["issues"] else None
    if top:
        info = describe(top["code"])
        out.append(f"**First checks for {top['code']} ({info['name']}):**\n")
        for c in info["checks"]:
            out.append(f"- {c}")
        out.append("")

    out.append("## One cause, many alarms\n")
    if not r["cascades"]:
        out.append("No chains of faults found.\n")
    for c in r["cascades"]:
        followers = ", ".join(f"{f['device']} ({f['code']})" for f in c["followers"])
        out.append(f"- **{c['start']}**: {c['root_code']} {describe(c['root_code'])['name']} on {c['root_device']} "
                   f"was followed within {c['spread_s']} s by {followers}. "
                   f"Treat it as one problem: {_h(c['minutes'])} of downtime in total.")
    out.append("")

    out.append("## Getting worse\n")
    if not r["worsening"]:
        out.append("Nothing is clearly getting more frequent.\n")
    for w in r["worsening"]:
        info = describe(w["code"])
        out.append(f"- **{w['device']} {w['code']} {info['name']}**: {w['first_half']} times in the first half of the period, "
                   f"{w['second_half']} in the second half. Likely: {info['causes'][0].lower()}. "
                   f"Plan maintenance before it turns into a long stop.")
    out.append("")

    out.append("## Availability\n")
    out.append("| Machine | Available |")
    out.append("|---|---|")
    for dev, pct in r["availability"].items():
        out.append(f"| {dev} | {pct} % |")
    out.append("")

    notes = []
    if r["inferred_ends"]:
        notes.append(f"{r['inferred_ends']} stoppage(s) had no RESUME line; the end was taken from the next cycle report.")
    if r["open_stops"]:
        notes.append(f"{r['open_stops']} stoppage(s) never ended in this log and are counted up to the last line.")
    if notes:
        out.append("## Data notes\n")
        out.extend(f"- {n}" for n in notes)
        out.append("")
    return "\n".join(out)


def write(result: dict, md_path: str, json_path: str) -> None:
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(build(result))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
