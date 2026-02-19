# Personal Workflow Management System

This system is designed for people with:
- high task volume,
- lots of inbound requests,
- many stakeholders to follow up with,
- a need to automate repetitive organization work.

## 1) Core workflow (simple and sustainable)

Use this cadence:

1. **Capture everything** into one inbox (`data/tasks.csv`) immediately.
2. **Triage twice daily** (morning + afternoon): prioritize, assign due dates, and set next actions.
3. **Execute from one prioritized view**: "today + overdue + urgent".
4. **Close loops daily**: review follow-ups and send pending replies.
5. **Review weekly**: clean up backlog, plan priorities, and reflect on workload.

If you're overwhelmed, reduce decisions: only decide **next action**, **priority**, and **deadline**.

---

## 2) Files in this system

- `data/tasks.csv` — single source of truth for tasks.
- `scripts/workflow_cli.py` — command-line helper to capture, list, and plan work.
- `templates/daily-plan.md` — daily planning template.
- `templates/weekly-review.md` — weekly planning/review template.

---

## 3) Recommended daily routine (30–45 minutes total admin)

### Morning (15 min)
- Run `python3 scripts/workflow_cli.py dashboard`.
- Pick top 3 outcomes for today.
- Time-block calendar for deep work and follow-up windows.

### Midday (5–10 min)
- Add new incoming requests with `add`.
- Reprioritize quickly if needed.

### End of day (10–15 min)
- Run `dashboard` again.
- Resolve what can be closed in <5 minutes.
- Schedule tomorrow’s top 3.

---

## 4) Communication management

For each task involving another person, set:
- `owner` (you or stakeholder),
- `waiting_on` (if blocked),
- `follow_up_date`.

Use `waiting_on` status to avoid dropped threads.

---

## 5) Automation ideas you can add next

- Calendar sync for due tasks.
- Slack/email reminders generated from `follow_up_date`.
- Recurring task generator (weekly reports, team check-ins).
- Lightweight dashboard in Google Sheets/Notion using exported CSV.

Start lightweight; only automate repeated pain points.

---

## 6) Quick start

```bash
python3 scripts/workflow_cli.py init
python3 scripts/workflow_cli.py add --title "Reply to onboarding questions" --priority P1 --due 2026-02-20 --person "Manager"
python3 scripts/workflow_cli.py dashboard
```

