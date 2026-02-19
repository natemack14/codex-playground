import csv
import datetime as dt
from pathlib import Path

import streamlit as st

ROOT = find_project_root(Path(__file__))
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
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(tasks)


def next_id(tasks: list[dict]) -> int:
    if not tasks:
        return 1
    ids = [int(t["id"]) for t in tasks if str(t.get("id", "")).isdigit()]
    return (max(ids) + 1) if ids else 1


def parse_date(value: str) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def mark_done(task_id: str) -> bool:
    tasks = read_tasks()
    for t in tasks:
        if t.get("id") == str(task_id):
            t["status"] = "done"
            write_tasks(tasks)
            return True
    return False


def delete_task(task_id: str) -> bool:
    tasks = read_tasks()
    before = len(tasks)
    tasks = [t for t in tasks if t.get("id") != str(task_id)]
    if len(tasks) == before:
        return False
    write_tasks(tasks)
    return True


st.set_page_config(page_title="Workflow Dashboard", layout="wide")
st.title("Workflow Dashboard")

tasks = read_tasks()
today = dt.date.today()

open_tasks = [t for t in tasks if t.get("status") != "done"]
p1_tasks = [t for t in open_tasks if t.get("priority") == "P1"]
due_today = [
    t
    for t in open_tasks
    if (d := parse_date(t.get("due_date", ""))) is not None and d == today
]
overdue = [
    t
    for t in open_tasks
    if (d := parse_date(t.get("due_date", ""))) is not None and d < today
]
waiting = [t for t in open_tasks if t.get("status") == "waiting"]
followups = [
    t
    for t in open_tasks
    if (d := parse_date(t.get("follow_up_date", ""))) is not None and d <= today
]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Open", len(open_tasks))
c2.metric("P1", len(p1_tasks))
c3.metric("Due today", len(due_today))
c4.metric("Overdue", len(overdue))
c5.metric("Waiting", len(waiting))

st.divider()

# Add task: clears fields automatically after submit
with st.expander("Add a task", expanded=True):
    with st.form("add_task_form", clear_on_submit=True):
        colA, colB, colC = st.columns([2, 1, 1])
        title = colA.text_input("Title", placeholder="What is the next action?")
        priority = colB.selectbox("Priority", ["P1", "P2", "P3"], index=1)
        status = colC.selectbox("Status", ["todo", "in_progress", "waiting", "done"], index=0)

        colD, colE, colF = st.columns(3)
        due = colD.date_input("Due date (optional)", value=None)
        person = colE.text_input("Person (optional)")
        follow_up = colF.date_input("Follow up (optional)", value=None)

        notes = st.text_area("Notes (optional)", height=80)

        submitted = st.form_submit_button("Add task")

    if submitted:
        if not title.strip():
            st.error("Title is required.")
        else:
            new_task = {
                "id": str(next_id(tasks)),
                "title": title.strip(),
                "priority": priority,
                "status": status,
                "due_date": due.isoformat() if due else "",
                "created_date": dt.date.today().isoformat(),
                "person": person.strip() if person else "",
                "waiting_on": "",
                "follow_up_date": follow_up.isoformat() if follow_up else "",
                "notes": notes.strip() if notes else "",
            }
            tasks.append(new_task)
            write_tasks(tasks)
            st.success(f"Added task #{new_task['id']}")
            st.rerun()

st.divider()
st.subheader("Open tasks")

left, right = st.columns([3, 2])

with left:
    show = st.selectbox(
        "View",
        ["All open", "P1", "Due today", "Overdue", "Waiting", "Follow ups due"],
        index=0,
    )
    if show == "All open":
        view_tasks = open_tasks
    elif show == "P1":
        view_tasks = p1_tasks
    elif show == "Due today":
        view_tasks = due_today
    elif show == "Overdue":
        view_tasks = overdue
    elif show == "Waiting":
        view_tasks = waiting
    else:
        view_tasks = followups

with right:
    st.caption("Tip: use the View dropdown to focus on urgent tasks.")

st.write("")

# Header row (added Delete column)
h1, h2, h3, h4, h5, h6, h7 = st.columns([0.6, 0.7, 1.1, 3.5, 1.4, 0.9, 0.9])
h1.write("**ID**")
h2.write("**Pri**")
h3.write("**Due**")
h4.write("**Title**")
h5.write("**Person**")
h6.write("")
h7.write("")

st.divider()

if not view_tasks:
    st.info("No tasks in this view.")
else:
    for t in view_tasks:
        c1, c2, c3, c4, c5, c6, c7 = st.columns([0.6, 0.7, 1.1, 3.5, 1.4, 0.9, 0.9])

        task_id = t.get("id", "")
        pri = t.get("priority", "")
        due_val = t.get("due_date", "") or "-"
        title_val = t.get("title", "")
        person_val = t.get("person", "") or "-"

        c1.write(task_id)
        c2.write(pri)
        c3.write(due_val)
        c4.write(title_val)
        c5.write(person_val)

        if c6.button("Done", key=f"done_{task_id}"):
            if mark_done(task_id):
                st.success(f"Marked task #{task_id} done")
                st.rerun()
            else:
                st.error("Task not found.")

        if c7.button("Delete", key=f"del_{task_id}"):
            if delete_task(task_id):
                st.success(f"Deleted task #{task_id}")
                st.rerun()
            else:
                st.error("Task not found.")
