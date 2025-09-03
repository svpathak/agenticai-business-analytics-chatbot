from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from pydantic import BaseModel, Field
from typing import Optional
import json

class QueryKeyParams(BaseModel):
    query_key_params: dict[str,str] = Field(
        description="Dictionary containing key params from user query."
    )

def irrelevant_user_query(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback that handles irrelevant user_query response.

    Args:
        callback_context: Contains state and context information.

    Returns:
        None to continue with normal agent processing.
        Dict for interrupting the SequentialAgent Pipeline.
    """
    curr_state = callback_context.state
    query_key_params = json.loads(curr_state["query_key_params"].strip().removeprefix("```json").removesuffix("```").strip())

    if "relevance" not in query_key_params.keys():
        print("Warning: relevance NOT in state['query_key_params']")

    relevance = query_key_params.get("relevance", "yes")
    if relevance.lower().strip() == "yes":
        return None
    else:
        print("---User Query is outside the App's capabilities---")
        # return {
        #     "status": "aborted",
        #     "error": "user_query is outside the App's capabilities"
        # }
        return {
            "status": "aborted",
            "error": "user_query is outside the App's capabilities"
        }
    

query_input_agent = LlmAgent(
    name="query_input_agent",
    model="gemini-2.5-flash",
    description="Agent that greets users and receives query from user.",
    instruction="""You are a helpful assistant that understands the user query.
    You will receive the user query related to market research and company/business information.
    You need to create query_key_params dictionary that will store key features from the user_query.
    In case the user query is irrelevant, the "relevance" param will be "no", so that the sequence is broken.'s query and pass on the information to the next agents.

    IMPORTANT: Your response MUST be valid JSON structure. Do NOT write anything else other than the valid json.
    Example:
    #1
    User Query: Please tell me about SBI's performance in India's Credit Card market.
    query_key_params:
    {
        "user_query": "Please tell me about SBI's performance in India's Credit Card market.",
        "relevance": "yes",
        "country": ["India"],
        "market": ["Credit Card"],
        "companies": ["State Bank of India (SBI)"]
    }

    #2
    User Query: What is the live score of India vs England test match?
    query_key_params:
    {
        "user_query": "What is the live score of India vs England test match?",
        "relevance": "no"
    }

    Note: Only "user_query" and "relevance" are mandatory keys, rest of the keys are optional and non-exhaustive.
          You may add many more keys based on user_query as required.
    """,
    output_key="query_key_params",
    # output_schema=QueryKeyParams,
    # after_agent_callback=irrelevant_user_query,
)