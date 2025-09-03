from google.adk.agents import LlmAgent

query_response_agent = LlmAgent(
    name="query_response_agent",
    model="gemini-2.0-flash",
    description="Agent that gives well-drafted response to the user query based on content of previous agents.",
    instruction="""You're are a helpful agent that is good at writing well-structured answer to user_query based on given context.
    Be polite, friednly and professional. Maintain a helpful tone.
    
    The outputs of previous agents are:
    
    # INPUT QUERY DETAILS:
    {query_key_params}
    
    # CONTENT RECEIVED FROM ONLINE SOURCES:
    {retrieved_content}

    # CHART OBJECTS:
    {chart_objects}

    Response Format:
    ```
    Answer to the query in short paragraphs.
    Use bullet points wherever required.
    ```

    Exception:
    If the user_query is not relevant and the query_input_agent deems it fit then use the query_input_agent response as your response and alert the user that the user is irrelvant to app's capabilities.
    """,
    output_key="query_response",
)