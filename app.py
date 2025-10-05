import streamlit as st
import speech_recognition as sr
import sqlite3
from datetime import datetime

# Initialize SQLite database
def init_db():
    with sqlite3.connect("grocery_list.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS groceries
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             item TEXT NOT NULL,
             category TEXT DEFAULT 'General',
             done BOOLEAN DEFAULT 0)
        """)
        # Migrate existing data if needed (add category and done if not present)
        try:
            conn.execute("ALTER TABLE groceries ADD COLUMN category TEXT DEFAULT 'General'")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE groceries ADD COLUMN done BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        conn.commit()

# Voice recognition function
def voice_to_text():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text.strip()
    except Exception as e:
        st.error("Could not understand audio. Please try again.")
        return None

# Database operations
def add_items(items_list, category):
    with sqlite3.connect("grocery_list.db") as conn:
        cursor = conn.cursor()
        for item in items_list:
            if item.strip():  # Only add non-empty items
                cursor.execute("INSERT INTO groceries (item, category, done) VALUES (?, ?, 0)", (item.strip(), category))
        conn.commit()

def delete_item(item_id):
    with sqlite3.connect("grocery_list.db") as conn:
        conn.execute("DELETE FROM groceries WHERE id = ?", (item_id,))
        conn.commit()

def toggle_done(item_id):
    with sqlite3.connect("grocery_list.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT done FROM groceries WHERE id = ?", (item_id,))
        current = cursor.fetchone()[0]
        conn.execute("UPDATE groceries SET done = ? WHERE id = ?", (not current, item_id))
        conn.commit()

def clear_done():
    with sqlite3.connect("grocery_list.db") as conn:
        conn.execute("DELETE FROM groceries WHERE done = 1")
        conn.commit()

def get_items(search=""):
    with sqlite3.connect("grocery_list.db") as conn:
        cursor = conn.cursor()
        query = "SELECT id, item, category, done FROM groceries WHERE item LIKE ? ORDER BY done ASC, id DESC"
        cursor.execute(query, (f"%{search}%",))
        return cursor.fetchall()

# Initialize database
init_db()

# Initialize session state for form
if 'form_data' not in st.session_state:
    st.session_state.form_data = ""
if 'should_clear' not in st.session_state:
    st.session_state.should_clear = False

# Page config
st.set_page_config(page_title="Shopping List", page_icon="🛒", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🛒 Shopping List")

def handle_voice_input():
    result = voice_to_text()
    if result:
        st.session_state.form_data = result
        return True
    return False

# Input form
col1, col2, col3 = st.columns([3, 2, 1])

with col1:
    text_input = st.text_input(
        "Add items (separate with spaces)",
        key="input_text",
        value=st.session_state.form_data,
        placeholder="Example: apple banana chicken"
    )

with col2:
    category_input = st.text_input("Category", value="General", placeholder="e.g., Fruits")

with col3:
    if st.button("🎤", help="Voice Input"):
        if handle_voice_input():
            st.rerun()

# Clear form data after it's been used
st.session_state.form_data = ""

# Add button
if st.button("Add To List", type="primary"):
    if text_input.strip():
        items = [item.strip() for item in text_input.split() if item.strip()]
        if items:
            add_items(items, category_input.strip() or "General")
            st.success(f"Added {len(items)} item(s) to the list!")
            st.session_state.input_text = ""
            st.rerun()

# Search and clear
search_query = st.text_input("Search items", placeholder="Type to filter...")
if st.button("Clear Purchased"):
    clear_done()
    st.rerun()

# Display items
items = get_items(search_query)

if items:
    st.divider()
    for item_id, item_text, category, done in items:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.checkbox(f"• {item_text} ({category})", value=done, key=f"chk_{item_id}", on_change=toggle_done, args=(item_id,))
        with col2:
            st.write("✅ Done" if done else "")
        with col3:
            if st.button("🗑️", key=f"del_{item_id}"):
                delete_item(item_id)
                st.rerun()
else:
    st.info("Your list is empty! Add some items above.")

# Footer
st.divider()
st.markdown(
    f"""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
    </div>
    """, 
    unsafe_allow_html=True
)
