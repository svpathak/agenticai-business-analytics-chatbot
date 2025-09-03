from google.adk.agents import SequentialAgent
from .sub_agents.query_input_agent import query_input_agent
from .sub_agents.content_retriever_agent import content_retriever_agent
from .sub_agents.data_chart_agent import data_chart_agent
from .sub_agents.query_response_agent import query_response_agent

root_agent = SequentialAgent(
    name="master_agent",
    description="Master Pipeline that orchestrates the sequences of sub agents.",
    sub_agents=[query_input_agent, content_retriever_agent, data_chart_agent, query_response_agent],
)