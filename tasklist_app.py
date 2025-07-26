import streamlit as st
import json
import os
from datetime import datetime, date, time
from dateutil.parser import parse as parse_datetime

TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(title, deadline):
    tasks = load_tasks()
    tasks.append({
        "title": title,
        "completed": False,
        "created_at": str(datetime.now()),
        "deadline": deadline if deadline else None
    })
    save_tasks(tasks)

def update_task_status(index, completed):
    tasks = load_tasks()
    tasks[index]["completed"] = completed
    save_tasks(tasks)

def delete_task(index):
    tasks = load_tasks()
    tasks.pop(index)
    save_tasks(tasks)

def sort_tasks(tasks):
    def task_sort_key(task):
        try:
            return parse_datetime(task["deadline"]) if task.get("deadline") else datetime.max
        except:
            return datetime.max
    return sorted(tasks, key=task_sort_key)

def format_deadline(deadline_str):
    if not deadline_str:
        return ""
    try:
        deadline = parse_datetime(deadline_str)
        now = datetime.now()
        delta = (deadline - now).total_seconds()

        if deadline.date() < now.date():
            return f"🟥 Overdue: {deadline.strftime('%b %d, %I:%M %p')}"
        elif 0 <= delta <= 86400:
            return f"🕒 Due Soon: {deadline.strftime('%b %d, %I:%M %p')}"
        elif deadline.date() == now.date():
            return f"🟨 Due Today: {deadline.strftime('%I:%M %p')}"
        else:
            return f"📅 {deadline.strftime('%b %d, %I:%M %p')}"
    except Exception:
        return "📅 Invalid deadline"

st.set_page_config("📝 Tasklist with Deadlines")
st.title("📝 Daily Tasklist")

st.subheader("➕ Add a New Task")
new_task = st.text_input("Task Title")
deadline_date = st.date_input("Deadline Date", value=None)
deadline_time = st.time_input("Deadline Time (optional)", value=time(12, 0))

deadline = None
if deadline_date:
    deadline = datetime.combine(deadline_date, deadline_time).isoformat()

if st.button("Add Task"):
    if new_task.strip():
        add_task(new_task.strip(), deadline)
        st.experimental_rerun()

tasks = sort_tasks(load_tasks())

if not tasks:
    st.info("No tasks yet. Add one above! 👆")
else:
    st.subheader("Your Tasks:")
    for i, task in enumerate(tasks):
        cols = st.columns([0.05, 0.6, 0.25, 0.1])
        checked = cols[0].checkbox("", value=task["completed"], key=f"task-{i}")
        if checked != task["completed"]:
            update_task_status(i, checked)

        title_display = f"~~{task['title']}~~" if checked else task['title']
        cols[1].markdown(title_display)

        deadline_display = format_deadline(task.get("deadline"))
        cols[2].markdown(deadline_display)

        if cols[3].button("❌", key=f"del-{i}"):
            delete_task(i)
            st.experimental_rerun()
