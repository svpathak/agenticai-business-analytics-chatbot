import streamlit as st
from streamlit_echarts import st_echarts
import json
from services.adk_service import initialize_adk, run_adk_sync
from config.settings import MESSAGE_HISTORY_KEY, get_api_key

def run_streamlit_app():
    """
    Sets up and runs the Streamlit web application for the ADK chat assistant.
    """
    st.set_page_config(page_title="Business Analytics ChatBot",
                       page_icon="📈",
                       layout="wide") # Configures the browser tab title and page layout.
    st.title("📈 Business Analytics ChatBot Assistant (Powered by ADK, Gemini & Streamlit)") # Main title of the app.

    st.markdown("This application uses the Google Agent Development Kit (ADK) to provide a chat interface.") # Descriptive text.
    st.divider() # A visual separator.
    api_key = get_api_key() # Retrieve the API key from settings.
    if not api_key:
        st.error("⚠️ Action Required: Google API Key Not Found or Invalid! Please set GOOGLE_API_KEY in your .env file. ⚠️")
        st.stop() # Stop the application if the API key is missing, prompting the user for action.
    # Initialize ADK runner and session ID (cached to run only once).
    adk_runner, current_session_id = initialize_adk()

    # # Sidebar for session management
    # with st.sidebar:
    #     st.header("Session Management")
    #     st.success(f"Active session: {current_session_id}")
    #     if st.button("➕ New Session"):
    #         for key in list(st.session_state.keys()):
    #             del st.session_state[key]
    #         adk_runner, current_session_id = initialize_adk()
    #         st.rerun()
    
    st.subheader("Chat with the Assistant") # Subheading for the chat section.

    # Initialize chat message history in Streamlit's session state if it doesn't exist.
    if MESSAGE_HISTORY_KEY not in st.session_state:
        st.session_state[MESSAGE_HISTORY_KEY] = []
    # Display existing chat messages from the session state.
    for message in st.session_state[MESSAGE_HISTORY_KEY]:
        with st.chat_message(message["role"]): # Use Streamlit's chat message container for styling.
            st.markdown(message["content"])
            if message["chart_option"]:
                st_echarts(options=message["chart_option"])


    # Handle new user input.
    if prompt := st.chat_input("Ask for a business/company/market related question ..."):
        # Append user's message to history and display it.
        st.session_state[MESSAGE_HISTORY_KEY].append({"role": "user", "content": prompt, "chart_option": None})
        with st.chat_message("user"):
            st.markdown(prompt)
        # Process the user's message with the ADK agent and display the response.
        with st.chat_message("assistant"):
            message_placeholder = st.empty() # Create an empty placeholder to update with the assistant's response.
            with st.spinner("Assistant is thinking..."): # Show a spinner while the agent processes the request.
                agent_response_text, agent_response_chart_option = run_adk_sync(adk_runner, current_session_id, prompt) # Call the synchronous ADK runner.
                message_placeholder.markdown(agent_response_text) # Update the placeholder with the final response.
                if agent_response_chart_option:
                    agent_response_chart_option = agent_response_chart_option.strip().removeprefix("```json").removesuffix("```").strip()
                    try:
                        agent_response_chart_option = json.loads(agent_response_chart_option)
                        st_echarts(options=agent_response_chart_option, height="300px")
                    except Exception as e:
                        print(f"Error in json.loads or st_echarts: {e}")
                        agent_response_chart_option = None
            
        # Append assistant's response to history.
        st.session_state[MESSAGE_HISTORY_KEY].append({"role": "assistant", "content": agent_response_text, "chart_option":agent_response_chart_option})