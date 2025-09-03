from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional
import json

def irrelevant_user_query_check(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback that handles irrelevant user_query response and skips the agent.

    Args:
        callback_context: Contains state and context information.

    Returns:
        None to continue with normal agent processing.
        types.Content to skip the agent processing.
    """
    state = callback_context.state
    agent_name = callback_context.agent_name

    if "query_key_params" not in state:
        print("Warning: query_key_params not found in ADK state.")
        return None
    
    query_key_params = state["query_key_params"].strip().removeprefix("```json").removesuffix("```").strip()
    try:
        query_key_params = json.loads(query_key_params)
    except Exception as e:
        print("Error: caught during json.loads in callback function of {agent_name}.")
    if "relevance" not in query_key_params:
        print("Warning: relevance not in query_key_params.")
        return None

    if query_key_params["relevance"].lower().strip() == "no":
        print("Info: User Query is outside the App's capabilities.\nSkipping the {agent_name}.")
        state["retrieved_content"] = ""
        return types.Content(
            parts=[types.Part(text=f"Agent {agent_name} skipped by before_agent_callback due to state.")],
            role="model" # Assign model role to the overriding response
        )
    else:
        print(f"Info: [Callback] State condition not met: Proceeding with agent {agent_name}.")
        return None
    

content_retriever_agent = LlmAgent(
    name="content_retriever_agent",
    model="gemini-2.0-flash",
    description="Agent that gather contents from online trusted sources.",
    instruction="""You will have access to trusted online blogs and industry reports.
    Based on the user query, you will first have to generate key tokens that will help you serach relevant content.
    Call the `google_search` tool to access internet blogs.
    """,
    tools=[google_search],
    output_key="retrieved_content",
    before_agent_callback=irrelevant_user_query_check,
)