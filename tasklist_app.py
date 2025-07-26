import streamlit as st
import json
import os
from datetime import datetime, date, time
from dateutil.parser import parse as parse_datetime

TASKS_FILE = "tasks.json"

CATEGORIES = ["VedaLeaf", "Tazza", "Syracuse Halal Gyro", "Personal", "Other"]

# ---------- Utilities ----------
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(title, deadline, category):
    tasks = load_tasks()
    tasks.append({
        "title": title,
        "completed": False,
        "created_at": str(datetime.now()),
        "deadline": deadline if deadline else None,
        "category": category
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
            return f"🔴 Overdue: {deadline.strftime('%b %d, %I:%M %p')}"
        elif 0 <= delta <= 86400:
            return f"🟠 Due Soon: {deadline.strftime('%b %d, %I:%M %p')}"
        elif deadline.date() == now.date():
            return f"🟡 Due Today: {deadline.strftime('%I:%M %p')}"
        else:
            return f"📅 {deadline.strftime('%b %d, %I:%M %p')}"
    except Exception:
        return "📅 Invalid deadline"

# ---------- Streamlit UI ----------
st.set_page_config("📝 Tasklist with Categories", layout="centered")
st.title("🗂️ My Task Manager")

with st.expander("➕ Add a New Task", expanded=True):
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task Title", placeholder="e.g. Payroll for Tazza, reorder from vendor...")
        category = st.selectbox("Select Category", CATEGORIES)
        deadline_col1, deadline_col2 = st.columns(2)
        with deadline_col1:
            deadline_date = st.date_input("Deadline Date", value=None)
        with deadline_col2:
            deadline_time = st.time_input("Deadline Time (optional)", value=time(12, 0))

        submitted = st.form_submit_button("Add Task")
        if submitted and title.strip():
            deadline = None
            if deadline_date:
                deadline = datetime.combine(deadline_date, deadline_time).isoformat()
            add_task(title.strip(), deadline, category)
            st.success("✅ Task added!")
            st.experimental_rerun()

# Group tasks by category
tasks = sort_tasks(load_tasks())
tasks_by_category = {}
for task in tasks:
    cat = task.get("category", "Uncategorized")
    tasks_by_category.setdefault(cat, []).append(task)

st.markdown("---")
if not tasks:
    st.info("No tasks yet. Add one above! 👆")
else:
    for category, cat_tasks in tasks_by_category.items():
        st.subheader(f"📁 {category}")
        for i, task in enumerate(cat_tasks):
            with st.container():
                row1 = st.columns([0.07, 0.65, 0.23, 0.05])
                checked = row1[0].checkbox("", value=task["completed"], key=f"check-{category}-{i}")
                if checked != task["completed"]:
                    task_index = tasks.index(task)
                    update_task_status(task_index, checked)

                title_display = f"~~{task['title']}~~" if checked else task['title']
                row1[1].markdown(f"**{title_display}**")

                deadline_display = format_deadline(task.get("deadline"))
                row1[2].markdown(deadline_display)

                if row1[3].button("❌", key=f"del-{category}-{i}"):
                    task_index = tasks.index(task)
                    delete_task(task_index)
                    st.stop()

        st.markdown("---")
