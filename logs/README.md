# Logs

Drop a controller log (`.log`) or an alarm history export (`.csv`) here and push it. The daily triage workflow will analyse the newest file and update `reports/`.

A CSV needs a time, device and alarm code for each row, plus a state column saying whether the alarm came on or went off. If your export uses other column names, run it locally with `--columns` (see the main README).

If there is no log in this folder, the workflow simulates the last 7 days instead. Simulated files are not committed.
