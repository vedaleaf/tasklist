# Secure Tasklist App

A secure tasklist app for managing multiple businesses using Streamlit.

## Features
- 🔐 Login-protected with a master password
- 🗂️ Categorized tasks (VedaLeaf, Tazza, etc.)
- 📅 Deadlines with color-coded labels
- ✅ Completion tracking
- 💾 Local file-based storage

## How to Use

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run tasklist_app.py
```

3. Use the login password to access your tasks.

## Customize Password
Edit the top of `tasklist_app.py` and replace:
```python
CORRECT_PASSWORD = "YourStrongPassword123"
```
