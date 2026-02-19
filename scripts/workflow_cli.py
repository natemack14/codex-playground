#!/usr/bin/env python3
"""Simple personal workflow manager.

Stores tasks in data/tasks.csv.
"""

import argparse
import csv
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "tasks.csv"
FIELDNAMES = [
    "id",
    "title",
    "priority",
    "status",
    "due_date",
    "created_date",
    "person",
    "waiting_on",
    "follow_up_date",
    "notes",
]


def ensure_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with DATA_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def read_tasks() -> list[dict]:
    ensure_file()
    with DATA_FILE.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_tasks(tasks: list[dict]) -> None:
    with DATA_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(tasks)


def next_id(tasks: list[dict]) -> int:
    if not tasks:
        return 1
    return max(int(t["id"]) for t in tasks if t["id"].isdigit()) + 1


def parse_date(value: str) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def add_task(args: argparse.Namespace) -> None:
    tasks = read_tasks()
    today = dt.date.today().isoformat()
    task = {
        "id": str(next_id(tasks)),
        "title": args.title,
        "priority": args.priority,
        "status": args.status,
        "due_date": args.due or "",
        "created_date": today,
        "person": args.person or "",
        "waiting_on": args.waiting_on or "",
        "follow_up_date": args.follow_up or "",
        "notes": args.notes or "",
    }
    tasks.append(task)
    write_tasks(tasks)
    print(f"Added task #{task['id']}: {task['title']}")


def list_tasks(args: argparse.Namespace) -> None:
    tasks = read_tasks()
    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    if args.priority:
        tasks = [t for t in tasks if t["priority"] == args.priority]

    print("ID | Pri | Status      | Due       | Title")
    print("---|-----|-------------|-----------|------")
    for t in tasks:
        print(
            f"{t['id']:>2} | {t['priority']:<3} | {t['status']:<11} | {t['due_date'] or '-':<9} | {t['title']}"
        )


def dashboard(_: argparse.Namespace) -> None:
    tasks = read_tasks()
    today = dt.date.today()

    open_tasks = [t for t in tasks if t["status"] != "done"]
    overdue = [
        t
        for t in open_tasks
        if (d := parse_date(t["due_date"])) is not None and d < today
    ]
    due_today = [
        t
        for t in open_tasks
        if (d := parse_date(t["due_date"])) is not None and d == today
    ]
    waiting = [t for t in open_tasks if t["status"] == "waiting"]
    p1 = [t for t in open_tasks if t["priority"] == "P1"]

    print("=== WORKFLOW DASHBOARD ===")
    print(f"Open tasks: {len(open_tasks)}")
    print(f"P1 tasks: {len(p1)}")
    print(f"Due today: {len(due_today)}")
    print(f"Overdue: {len(overdue)}")
    print(f"Waiting: {len(waiting)}")
    print()

    if overdue:
        print("Overdue tasks:")
        for t in overdue[:10]:
            print(f"- #{t['id']} [{t['priority']}] {t['title']} (due {t['due_date']})")
        print()

    followups = [
        t
        for t in open_tasks
        if (d := parse_date(t["follow_up_date"])) is not None and d <= today
    ]
    if followups:
        print("Follow-ups due:")
        for t in followups[:10]:
            person = t["person"] or "(no person)"
            print(f"- #{t['id']} {t['title']} -> follow up with {person}")


def init_data(_: argparse.Namespace) -> None:
    ensure_file()
    print(f"Initialized: {DATA_FILE}")
    
def mark_done(args: argparse.Namespace) -> None:
    tasks = read_tasks()
    target = str(args.id)
    updated = False

    for t in tasks:
        if t["id"] == target:
            t["status"] = "done"
            updated = True
            print(f"Marked task #{t['id']} done: {t['title']}")
            break

    if not updated:
        print(f"No task found with id {target}")
        return

    write_tasks(tasks)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Personal workflow manager")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="Initialize CSV data file")
    init_cmd.set_defaults(func=init_data)

    add_cmd = sub.add_parser("add", help="Add a task")
    add_cmd.add_argument("--title", required=True)
    add_cmd.add_argument("--priority", default="P2", choices=["P1", "P2", "P3"])
    add_cmd.add_argument(
        "--status",
        default="todo",
        choices=["todo", "in_progress", "waiting", "done"],
    )
    add_cmd.add_argument("--due", help="Due date YYYY-MM-DD")
    add_cmd.add_argument("--person", help="Relevant person")
    add_cmd.add_argument("--waiting-on", help="What/whom you are waiting on")
    add_cmd.add_argument("--follow-up", help="Follow-up date YYYY-MM-DD")
    add_cmd.add_argument("--notes", help="Optional notes")
    add_cmd.set_defaults(func=add_task)

    list_cmd = sub.add_parser("list", help="List tasks")
    list_cmd.add_argument("--status", choices=["todo", "in_progress", "waiting", "done"])
    list_cmd.add_argument("--priority", choices=["P1", "P2", "P3"])
    list_cmd.set_defaults(func=list_tasks)

    done_cmd = sub.add_parser("done", help="Mark a task as done")
    done_cmd.add_argument("id", type=int, help="Task id")
    done_cmd.set_defaults(func=mark_done)
    
    dash_cmd = sub.add_parser("dashboard", help="Show summary dashboard")
    dash_cmd.set_defaults(func=dashboard)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
