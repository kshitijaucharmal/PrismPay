import streamlit as st
from google.adk.runners import InMemoryRunner
from agent_backend import get_user_agent

# --- Page Config ---
st.set_page_config(page_title="OneCard Assistant", page_icon="💳")

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "runner" not in st.session_state:
    st.session_state.runner = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "customer_id" not in st.session_state:
    st.session_state.customer_id = None


def login(user_id, password):
    # Mock authentication - In real world, check against DB
    if user_id and password == "1234":  # Simple password for demo
        st.session_state.logged_in = True
        st.session_state.customer_id = user_id

        # Initialize the Agent specifically for this user
        # This binds the tools to the logged-in customer_id
        agent = get_user_agent(customer_id=user_id)
        st.session_state.runner = InMemoryRunner(agent=agent)
        st.rerun()
    else:
        st.error("Invalid Customer ID or Password")


def logout():
    st.session_state.logged_in = False
    st.session_state.customer_id = None
    st.session_state.runner = None
    st.session_state.messages = []
    st.rerun()

# --- UI Layout ---


st.title("💳 OneCard GenAI Assistant")

if not st.session_state.logged_in:
    st.header("Login")
    with st.form("login_form"):
        uid = st.text_input("Customer ID (e.g., CUST101)")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            login(uid, pwd)

    st.info("Demo Tip: Use any Customer ID and password '1234'")

else:
    # --- Sidebar ---
    with st.sidebar:
        st.success(f"Logged in as: **{st.session_state.customer_id}**")
        if st.button("Logout"):
            logout()
        st.divider()
        st.markdown("### Suggested Actions")
        if st.button("Check Bill"):
            # A trick to programmatically trigger a user message
            st.session_state.messages.append(
                {"role": "user", "content": "What is my current bill?"})
            st.rerun()

    # --- Chat Interface ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you with your card?"):
        # 1. Display User Message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Get Response from ADK Runner
        with st.spinner("Thinking..."):
            try:
                # The runner executes the agent we created during login
                result = st.session_state.runner.run(prompt)

                # ADK returns complex objects, we extract the final text
                # Adjust 'final_response' if your ADK version returns differently
                bot_response = result.get(
                    "final_response", "Sorry, I couldn't process that.")

                st.chat_message("assistant").markdown(bot_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": bot_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")
