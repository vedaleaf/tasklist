import streamlit as st
import json
import os
from datetime import datetime, date, time
from dateutil.parser import parse as parse_datetime

# --- Login Setup ---
CORRECT_PASSWORD = "veda12"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "just_logged_in" not in st.session_state:
    st.session_state.just_logged_in = False
if "just_logged_out" not in st.session_state:
    st.session_state.just_logged_out = False

if st.session_state.get("logged_in"):
    top = st.columns([0.85, 0.15])
    with top[1]:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.just_logged_out = True
            st.stop()

if not st.session_state.get("logged_in"):
    st.title("🔒 Login Required")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password == CORRECT_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.just_logged_in = True
            st.stop()
        else:
            st.error("Incorrect password")
    st.stop()

if st.session_state.just_logged_in:
    st.session_state.just_logged_in = False
    st.success("✅ Logged in!")

if st.session_state.just_logged_out:
    st.session_state.just_logged_out = False
    st.info("🚪 Logged out successfully.")

# --- App Setup ---
TASKS_FILE = "tasks.json"
CATEGORIES = ["VedaLeaf", "Tazza", "Syracuse Halal Gyro", "Personal", "Other"]

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(title, deadline, category, description):
    tasks = load_tasks()
    tasks.append({
        "title": title,
        "completed": False,
        "created_at": str(datetime.now()),
        "deadline": deadline if deadline else None,
        "category": category,
        "description": description,
        "checklist": []
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

def add_checklist_item(task_index, item_text):
    tasks = load_tasks()
    if "checklist" not in tasks[task_index]:
        tasks[task_index]["checklist"] = []
    tasks[task_index]["checklist"].append({"item": item_text, "done": False})
    save_tasks(tasks)

def update_checklist_status(task_index, item_index, done):
    tasks = load_tasks()
    tasks[task_index]["checklist"][item_index]["done"] = done
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

# --- UI ---
st.set_page_config("📝 Tasklist with Categories", layout="centered")
st.title("🗂️ My Task Manager")

# --- Add Task Form ---
with st.expander("➕ Add a New Task", expanded=True):
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task Title")
        description = st.text_area("Description (optional)")
        category = st.selectbox("Select Category", CATEGORIES)
        col1, col2 = st.columns(2)
        with col1:
            deadline_date = st.date_input("Deadline Date", value=None)
        with col2:
            deadline_time = st.time_input("Deadline Time (optional)", value=time(12, 0))

        submitted = st.form_submit_button("Add Task")
        if submitted and title.strip():
            deadline = None
            if deadline_date:
                deadline = datetime.combine(deadline_date, deadline_time).isoformat()
            add_task(title.strip(), deadline, category, description.strip())
            st.session_state["just_added"] = True
            st.stop()

if st.session_state.get("just_added"):
    st.success("✅ Task added!")
    del st.session_state["just_added"]

# --- Display Tasks ---
tasks = sort_tasks(load_tasks())
tasks_by_category = {}
for i, task in enumerate(tasks):
    cat = task.get("category", "Uncategorized")
    tasks_by_category.setdefault(cat, []).append((i, task))  # store original index too

st.markdown("---")
if not tasks:
    st.info("No tasks yet. Add one above! 👆")
else:
    for category, cat_tasks in tasks_by_category.items():
        st.subheader(f"📁 {category}")
        for i, (task_index, task) in enumerate(cat_tasks):
            with st.container():
                row = st.columns([0.07, 0.65, 0.23, 0.05])
                checked = row[0].checkbox("", value=task["completed"], key=f"check-{category}-{i}")
                if checked != task["completed"]:
                    update_task_status(task_index, checked)

                title_display = f"~~{task['title']}~~" if checked else task['title']
                row[1].markdown(f"**{title_display}**")

                row[2].markdown(format_deadline(task.get("deadline")))

                if row[3].button("❌", key=f"del-{category}-{i}"):
                    delete_task(task_index)
                    st.stop()

            # Description
            if task.get("description"):
                st.markdown(f"📝 _{task['description']}_")

            # Checklist Items
            st.markdown("✅ **Checklist:**")
            checklist = task.get("checklist", [])
            for ci, item in enumerate(checklist):
                checked = st.checkbox(item["item"], value=item["done"], key=f"cl-{task_index}-{ci}")
                if checked != item["done"]:
                    update_checklist_status(task_index, ci, checked)

            # Add checklist item input
            with st.expander("➕ Add checklist item", expanded=False):
                new_item = st.text_input(f"New item for task {task_index}", key=f"input-{task_index}")
                if st.button("Add", key=f"add-{task_index}") and new_item.strip():
                    add_checklist_item(task_index, new_item.strip())
                    st.experimental_rerun()

            st.markdown("---")
