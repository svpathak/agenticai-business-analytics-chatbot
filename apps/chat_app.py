# https://github.com/chongdashu/adk-made-simple/blob/main/apps/speaker_app.py
# https://www.youtube.com/watch?v=jrFFEPWoB1Q

import streamlit as st
from streamlit_echarts import st_echarts
import requests
import json
import uuid
import time

# Set page config
st.set_page_config(
    page_title="Business Analytics ChatBot",
    page_icon="📈",
    layout="centered"
)

# Constants
API_BASE_URL = "http://localhost:8000"
APP_NAME = "master_agent"

# Initialize session state variables
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user-{uuid.uuid4()}"
    
if "session_id" not in st.session_state:
    st.session_state.session_id = None
    
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_key_params" not in st.session_state:
    st.session_state.query_key_params = {}

if "retrieved_content" not in st.session_state:
    st.session_state.retrieved_content = ""

if "chart_objects" not in st.session_state:
    st.session_state.chart_objects = []

if "query_response" not in st.session_state:
    st.session_state.query_response = ""

def create_session():
    """
    Create a new session with the master_agent.
    
    This function:
    1. Generates a unique session ID based on timestamp
    2. Sends a POST request to the ADK API to create a session
    3. Updates the session state variables if successful
    
    Returns:
        bool: True if session was created successfully, False otherwise
    
    API Endpoint:
        POST /apps/{app_name}/users/{user_id}/sessions/{session_id}
    """
    session_id = f"session-{int(time.time())}"
    response = requests.post(
        f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}",
        headers={"Content-Type": "application/json"},
        data=json.dumps({})
    )
    
    if response.status_code == 200:
        st.session_state.session_id = session_id
        st.session_state.messages = []
        st.session_state.query_key_params = {}
        st.session_state.retrieved_content = ""
        st.session_state.chart_objects = []
        st.session_state.query_response = ""
        return True
    else:
        st.error(f"Failed to create session: {response.text}")
        return False
    

def send_message(message):
    """
    Send a message to the master agent and process the response.
    
    This function:
    1. Adds the user message to the chat history
    2. Sends the message to the ADK API
    3. Processes the response to extract text and response information
    4. Updates the chat history with the assistant's response
    
    Args:
        message (str): The user's message to send to the agent
        
    Returns:
        bool: True if message was sent and processed successfully, False otherwise
    
    API Endpoint:
        POST /run
        
    Response Processing:
        - Parses the ADK event structure to extract text responses
        - Looks for text_to_speech function responses to find audio file paths
        - Adds both text and audio information to the chat history
    """
    if not st.session_state.session_id:
        st.error("No active session. Please create a session first.")
        return False
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": message})
    
    # Send message to API
    response = requests.post(
        f"{API_BASE_URL}/run",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "app_name": APP_NAME,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}]
            }
        })
    )
    
    if response.status_code != 200:
        st.error(f"Error: {response.text}")
        return False
    
    # Process the response
    events = response.json()
    
    # Extract assistant's text response
    chart_objects = None
    assistant_message = None
    
    for event in events:
        # Look for the final text response from the model
        if event.get("content", {}).get("role") == "model" and "text" in event.get("content", {}).get("parts", [{}])[0]:
            assistant_message = event["content"]["parts"][0]["text"]

        if hasattr(event,"author") and event["author"] == "data_chart_agent":
            if hasattr(event,"actions") and isinstance(event["actions"], dict):
                if hasattr(event["actions"],"stateDelta") and isinstance(event["actions"]["stateDelta"], dict):
                    if hasattr(event["actions"]["stateDelta"],"chart_objects"):
                        chart_objects = event["actions"]["stateDelta"]["chart_objects"]
                        if not isinstance(chart_objects, list):
                            print("--- Chart Error: Type of chart_objects is NOT list ---")
                            chart_objects = None
    
    # Add assistant response to chat
    if assistant_message:
        st.session_state.messages.append({"role": "assistant", "content": assistant_message, "chart_objects":chart_objects})
    
    return True

# UI Components
st.title("📈 Business Analytics ChatBot")

# Sidebar for session management
with st.sidebar:
    st.header("Session Management")
    
    if st.session_state.session_id:
        st.success(f"Active session: {st.session_state.session_id}")
        if st.button("➕ New Session"):
            create_session()
    else:
        st.warning("No active session")
        if st.button("➕ Create Session"):
            create_session()
    
    st.divider()
    st.caption("This app interacts with the Speaker Agent via the ADK API Server.")
    st.caption("Make sure the ADK API Server is running on port 8000.")

# Chat interface
st.subheader("Conversation")

option = {
        "title": {
            "text": "HDFC Bank Asset Quality (Q1FY26 vs Q1FY25)",
            "subtext": "Values in Percentage"
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "legend": {
            "data": ["Q1FY25", "Q1FY26"]
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": ["Gross NPA", "Net NPA"]
        },
        "yAxis": {
            "type": "value",
            "name": "Percentage (%)",
            "axisLabel": {
                "formatter": "{value}%"
            }
        },
        "series": [
            {
                "name": "Q1FY25",
                "type": "bar",
                "data": [1.33, 0.39],
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{value}%"
                }
            },
            {
                "name": "Q1FY26",
                "type": "bar",
                "data": [1.40, 0.47],
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{value}%"
                }
            }
        ]
}

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])
            # Handle chart_objects if available
            if "chart_objects" in msg and msg["chart_objects"]:
                # Render the chart using st_echarts
                try:
                    st_echarts(options=json.loads(msg["chart_objects"]), height="400px")
                except:
                    print("Failed to render chart_objects")
        
            # if "audio_path" in msg and msg["audio_path"]:
            #     audio_path = msg["audio_path"]
            #     if os.path.exists(audio_path):
            #         st.audio(audio_path)
            #     else:
            #         st.warning(f"Audio file not accessible: {audio_path}")

# Input for new messages
if st.session_state.session_id:  # Only show input if session exists
    user_input = st.chat_input("Type your message...")
    if user_input:
        send_message(user_input)
        st.rerun()  # Rerun to update the UI with new messages
else:
    st.info("👈 Create a session to start chatting")