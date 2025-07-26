import streamlit as st
import json
import os
from datetime import datetime, date, time
from dateutil.parser import parse as parse_datetime

CORRECT_PASSWORD = "YourStrongPassword123"

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
    st.title("🔐 Login Required")
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

TASKS_FILE = "tasks.json"
CATEGORIES = ["VedaLeaf", "Tazza", "Syracuse Halal Gyro", "Jagdish Express", "Personal", "Other"]

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
        "checklist": [],
        "order": len(tasks)
    })
    save_tasks(tasks)

def update_task(task_index, key, value):
    tasks = load_tasks()
    tasks[task_index][key] = value
    save_tasks(tasks)

def update_checklist_item(task_index, item_index, field, value):
    tasks = load_tasks()
    tasks[task_index]["checklist"][item_index][field] = value
    save_tasks(tasks)

def reorder_checklist(task_index):
    tasks = load_tasks()
    tasks[task_index]["checklist"] = sorted(
        tasks[task_index]["checklist"], key=lambda x: x.get("order", 0)
    )
    save_tasks(tasks)

def add_checklist_item(task_index, item_text):
    tasks = load_tasks()
    tasks[task_index]["checklist"].append({"item": item_text, "done": False, "order": len(tasks[task_index]["checklist"])})
    save_tasks(tasks)

def delete_task(index):
    tasks = load_tasks()
    tasks.pop(index)
    save_tasks(tasks)

def delete_checklist_item(task_index, item_index):
    tasks = load_tasks()
    tasks[task_index]["checklist"].pop(item_index)
    save_tasks(tasks)

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
            return f"🔸 Due Soon: {deadline.strftime('%b %d, %I:%M %p')}"
        elif deadline.date() == now.date():
            return f"🟡 Due Today: {deadline.strftime('%I:%M %p')}"
        else:
            return f"🗓️ {deadline.strftime('%b %d, %I:%M %p')}"
    except Exception:
        return "🗓️ Invalid deadline"

st.set_page_config("📝 Tasklist with Reordering", layout="centered")
st.title("🗂️ Multi-Business Task Manager")

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

all_tasks = load_tasks()
tasks_by_category = {}
for i, task in enumerate(all_tasks):
    cat = task.get("category", "Uncategorized")
    tasks_by_category.setdefault(cat, []).append((i, task))

for category, cat_tasks in tasks_by_category.items():
    sorted_tasks = sorted(cat_tasks, key=lambda x: x[1].get("order", 0))
    with st.expander(f"📁 {category}", expanded=False):
        for i, (task_index, task) in enumerate(sorted_tasks):
            with st.container():
                row = st.columns([0.07, 0.6, 0.23, 0.1])
                checked = row[0].checkbox("", value=task["completed"], key=f"complete-{task_index}")
                if checked != task["completed"]:
                    update_task(task_index, "completed", checked)

                new_title = row[1].text_input("Task", value=task["title"], key=f"title-{task_index}")
                if new_title != task["title"]:
                    update_task(task_index, "title", new_title)

                order_num = row[2].number_input("Order", min_value=0, value=task.get("order", i), key=f"order-{task_index}")
                if order_num != task.get("order", i):
                    update_task(task_index, "order", order_num)

                if row[3].button("❌", key=f"del-{task_index}"):
                    delete_task(task_index)
                    st.stop()

            new_desc = st.text_area("Description", value=task.get("description", ""), key=f"desc-{task_index}")
            if new_desc != task.get("description", ""):
                update_task(task_index, "description", new_desc)

            st.markdown("✅ **Checklist:**")
            checklist = task.get("checklist", [])
            sorted_checklist = sorted(checklist, key=lambda x: x.get("order", 0))
            for ci, item in enumerate(sorted_checklist):
                cl_cols = st.columns([0.07, 0.7, 0.1, 0.1])
                done = cl_cols[0].checkbox("", value=item["done"], key=f"chk-{task_index}-{ci}")
                label = cl_cols[1].text_input("", value=item["item"], key=f"item-{task_index}-{ci}")
                order = cl_cols[2].number_input("", min_value=0, value=item.get("order", ci), key=f"ord-{task_index}-{ci}")

                if done != item["done"]:
                    update_checklist_item(task_index, ci, "done", done)
                if label != item["item"]:
                    update_checklist_item(task_index, ci, "item", label)
                if order != item.get("order", ci):
                    update_checklist_item(task_index, ci, "order", order)
                    reorder_checklist(task_index)

                if cl_cols[3].button("❌", key=f"delcl-{task_index}-{ci}"):
                    delete_checklist_item(task_index, ci)
                    st.stop()

            with st.expander("➕ Add checklist item", expanded=False):
                new_item = st.text_input("New checklist item", key=f"new-{task_index}")
                if st.button("Add", key=f"add-{task_index}") and new_item.strip():
                    add_checklist_item(task_index, new_item.strip())
                    st.success("✅ Subtask added!")
                    st.stop()

            st.markdown("---")
