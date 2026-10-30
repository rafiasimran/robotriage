# Changelog

## 1.0.0 (2026-10-30)

First release.

- Reads robot cell logs, skips and counts broken lines
- Finds every stoppage, from fault to resume, without double counting
- Groups chains of faults behind the fault that caused them (power dips, bus timeouts)
- Ranks problems by downtime, with first checks from a small fault knowledge base
- Flags faults that are getting more frequent
- Availability and mean time between failures per machine
- Markdown and JSON report, plus a dashboard on GitHub Pages
- Daily GitHub Actions run, 16 tests

### Fixed before release

- Faults that only happened close together in time were grouped as one chain
  (a light curtain trip on R3 and a gripper fault on R2). Now only faults that
  can actually spread through the cell can start a chain.
