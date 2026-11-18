import os

import requests
import streamlit as st

# ---------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Nova | Personal Assistant",
    page_icon="✨",
    layout="centered",
)

# The webhook URL is never shown in the UI. Paste your Production URL below,
# or set the N8N_WEBHOOK_URL environment variable to override it.
DEFAULT_WEBHOOK = "http://localhost:5678/webhook/PASTE-YOUR-PRODUCTION-URL-ID-HERE"
webhook_url = os.environ.get("N8N_WEBHOOK_URL", DEFAULT_WEBHOOK)

# ---------------------------------------------------------------
# Theme (custom CSS)
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #1e1b4b 0%, transparent 60%),
                    radial-gradient(900px 500px at 100% 0%, #064e3b 0%, transparent 55%),
                    #0b1020;
        color: #e5e7eb;
    }
    header[data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] {
        background: #0e1428;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    .hero { padding: 28px 8px 8px 8px; text-align: center; }
    .hero h1 {
        font-size: 2.6rem;
        margin: 0;
        background: linear-gradient(90deg, #a78bfa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .hero p { color: #9ca3af; margin-top: 6px; font-size: 1.02rem; }

    .section-title {
        margin: 26px 0 4px 0;
        font-weight: 700;
        font-size: 1.05rem;
        color: #d1d5db;
    }
    .hint { color: #6b7280; font-size: .8rem; margin-bottom: 10px; }

    /* Capability cards: hover to see everything a card can do */
    .cap-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 14px 14px 12px 14px;
        margin-bottom: 12px;
        transition: transform .15s ease, border-color .15s ease, background .15s ease;
    }
    .cap-card:hover {
        transform: translateY(-2px);
        border-color: #a78bfa;
        background: rgba(167,139,250,0.08);
    }
    .cap-card .ic { font-size: 1.5rem; }
    .cap-card .tt { font-weight: 700; margin-top: 4px; color: #f3f4f6; }
    .cap-card .ds { font-size: .82rem; color: #9ca3af; margin-top: 2px; }
    .cap-card .more {
        max-height: 0;
        opacity: 0;
        overflow: hidden;
        transition: max-height .25s ease, opacity .25s ease, margin .25s ease;
        font-size: .8rem;
        color: #d1d5db;
    }
    .cap-card:hover .more { max-height: 220px; opacity: 1; margin-top: 10px; }
    .cap-card .more ul { margin: 0; padding-left: 18px; }
    .cap-card .more li { margin: 2px 0; }

    div[data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 10px 14px;
    }
    div.stButton > button {
        border-radius: 999px;
        border: 1px solid rgba(167,139,250,0.5);
        background: rgba(167,139,250,0.10);
        color: #e5e7eb;
    }
    div.stButton > button:hover {
        border-color: #34d399;
        background: rgba(52,211,153,0.12);
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# State
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### ✨ Nova")
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------
# Hero
# ---------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>✨ Nova</h1>
        <p>Your personal assistant for calendar, mail, tasks, notes and money.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# What I can do (hover a card to see every function behind it)
# ---------------------------------------------------------------
CARDS = [
    ("🔎", "Ask anything", "Answers and live web search",
     ["Answer general questions", "Search Google for current facts"]),
    ("📅", "Calendar", "Create and look up events",
     ["Create an event", "Get the details of one event", "List events (today, this week)",
      "Delete an event"]),
    ("✉️", "Email", "Read, summarize and send mail",
     ["Read recent emails", "Read a single email", "Summarize emails", "Send or reply to an email"]),
    ("✅", "Tasks", "Manage your to-do lists",
     ["Create a task", "Get one task", "List all tasks", "Delete a task"]),
    ("📝", "Notes", "Save quick notes to Docs",
     ["Create a new notes file", "Add text to a note", "Read a note"]),
    ("💰", "Expenses", "Log and review spending",
     ["Add an expense", "Get expense history", "Calculate totals and budgets"]),
]

st.markdown('<div class="section-title">What I can do</div>', unsafe_allow_html=True)
st.markdown('<div class="hint">Hover over a card to see everything it can do.</div>', unsafe_allow_html=True)

for row in range(0, len(CARDS), 3):
    cols = st.columns(3)
    for col, (icon, title, desc, items) in zip(cols, CARDS[row : row + 3]):
        li = "".join(f"<li>{item}</li>" for item in items)
        col.markdown(
            f"""
            <div class="cap-card">
                <div class="ic">{icon}</div>
                <div class="tt">{title}</div>
                <div class="ds">{desc}</div>
                <div class="more"><ul>{li}</ul></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------
# Chat
# ---------------------------------------------------------------
st.markdown('<div class="section-title">💬 Chat</div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "✨"):
        st.markdown(message["content"])


def ask_assistant(text: str) -> str:
    """Send the message to the n8n webhook and return the agent's reply."""
    try:
        response = requests.post(webhook_url, json={"message": text}, timeout=180)
    except requests.exceptions.ConnectionError:
        return "⚠️ Can't reach the assistant. Make sure Docker and n8n are running."
    except requests.exceptions.Timeout:
        return "⚠️ The assistant took too long to answer. Please try again."

    if response.status_code == 404:
        return "⚠️ The assistant's workflow wasn't found (404). Check that it is published and the webhook URL in app.py is correct."
    if response.status_code == 429 or "too many requests" in response.text.lower():
        return "⚠️ The AI model is rate limited right now. Wait a bit or switch the Gemini model."
    if not response.ok:
        return f"⚠️ The workflow returned an error ({response.status_code}). Check Executions in n8n for details."

    try:
        data = response.json()
        if isinstance(data, list) and data:
            data = data[0]
        if isinstance(data, dict):
            return data.get("output") or data.get("text") or str(data)
        return str(data)
    except ValueError:
        return response.text or "⚠️ Empty reply from the workflow."


prompt = st.chat_input("Message Nova…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Thinking…"):
            reply = ask_assistant(prompt)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
