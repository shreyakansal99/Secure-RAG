import requests
import streamlit as st

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Secure RAG", page_icon="🔒")
st.title("🔒 Secure RAG Chatbot")

# ---------- session state ----------
if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.messages = []


def do_login(username, password):
    try:
        r = requests.post(
            f"{API}/login",
            data={"username": username, "password": password},  # form data, not JSON
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return "Cannot reach the API. Is uvicorn running?"
    if r.status_code != 200:
        return "Wrong username or password."
    st.session_state.token = r.json()["access_token"]
    st.session_state.username = username
    st.session_state.messages = []
    return None


def do_logout():
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.messages = []


# ---------- login screen ----------
if not st.session_state.token:
    st.subheader("Login")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        err = do_login(u, p)
        if err:
            st.error(err)
        else:
            st.rerun()
    st.caption("Demo users: alice (employee), harry (hr), frank (finance), root (admin)")
    st.stop()

# ---------- sidebar ----------
with st.sidebar:
    st.write(f"Logged in as **{st.session_state.username}**")
    if st.session_state.role:
        st.write(f"Role: **{st.session_state.role}**")
    if st.button("Log out"):
        do_logout()
        st.rerun()

# ---------- chat history ----------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("sources"):
            with st.expander("Sources"):
                for s in m["sources"]:
                    st.write(f"- {s['source']} (page {s['page']})")

# ---------- new question ----------
query = st.chat_input("Ask a question about company documents")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(
                    f"{API}/chat",
                    json={"query": query},
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    timeout=60,
                )
            except requests.exceptions.RequestException as e:
                r = None
                reply = f"Request failed: {e}"
                sources = []

        pii = []   # default, must be set before the if-chain
        blocked = False

        if r is not None and r.status_code == 401:
            do_logout()
            st.warning("Session expired. Please log in again.")
            st.rerun()
        elif r is not None and r.status_code == 200:
            data = r.json()                      # parse first
            st.session_state.role = data["role"]
            reply = data["answer"]
            sources = data["sources"]
            pii = data.get("pii_found", [])      # then read from it
            blocked = data.get("blocked", False)
        elif r is not None:
            reply = f"Server error ({r.status_code})."
            sources = []

        st.write(reply)
        if blocked:
            st.warning("This request was blocked by the security guardrails.")
        if pii:
            st.info(f"Sensitive data detected and masked before processing: {', '.join(pii)}")
        if sources:
            with st.expander("Sources"):
                for s in sources:
                    st.write(f"- {s['source']} (page {s['page']})")

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "sources": sources}
    )