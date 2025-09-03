from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Dict, Optional
import json
import yfinance as yf


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
        state["chart_objects"] = "```json {}```"
        return types.Content(
            parts=[types.Part(text=f"Agent {agent_name} skipped by before_agent_callback due to state.")],
            role="model" # Assign model role to the overriding response
        )
    else:
        print(f"Info: [Callback] State condition not met: Proceeding with agent {agent_name}.")
        return None
    
def get_data_tables(company_name: str) -> Dict:
    '''
        Tool that returns various data tables for a `company_name` using the famous yfinance api.

        Input:
            company_name (str): Official stock exchange abbreviation of the company.
                                For company listed in India, add ".NS" at the end of teh company_name.
        Output:
            Returns a dictionary of various data tables in json object format of the company_name.
            In case of error, will return a dict with error message.
    '''
    try:
        ticker = yf.Ticker(company_name)
    except:
        return {
            "status": "failure",
            "error_msg": "company_name is invalid."
        }
    info = ticker.info

    return_dict = dict()
    try:
        return_dict["sector"] = info["sector"]
    except Exception as e:
        print(f"Agent - data_chart_agent - Tool - get_data_tables: error in 'sector': {e}")

    try:
        return_dict["marketCap"] = info["marketCap"]
    except Exception as e:
        print(f"Agent - data_chart_agent - Tool - get_data_tables: error in 'marketCap': {e}")

    try:
        return_dict["financials"] = ticker.financials.to_json(orient='records')
    except Exception as e:
        print(f"Agent - data_chart_agent - Tool - get_data_tables: error in 'financials': {e}")

    try:
        return_dict["balance_sheet"] = ticker.balance_sheet.to_json(orient='records')
    except Exception as e:
        print(f"Agent - data_chart_agent - Tool - get_data_tables: error in 'balance_sheet': {e}")

    try:
        return_dict["cashflow"] = ticker.cashflow.to_json(orient='records')
    except Exception as e:
        print(f"Agent - data_chart_agent - Tool - get_data_tables: error in 'cashflow': {e}")

    try:
        return_dict["income_stmt"] = ticker.income_stmt.to_json(orient='records')
    except Exception as e:
        print(f"Agent - data_chart_agent - Tool - get_data_tables: error in 'income_stmt': {e}")


    return_dict["status"] = "success"
    return return_dict


data_chart_agent = LlmAgent(
    name="data_chart_agent",
    model="gemini-2.5-flash",
    description="Agent that extract data relevant to query and renders a json apache echarts object.",
    instruction="""You're a helpful agent that extracts relvant data for charts using `get_data_tables` tool and returns json objects for each chart.
    Based on the data received and the user query, select the most appropriate data field received from the tool.
    Once the most appropriate data is selected then create apache echarts json object of a illustrative chart.
    
    Response Style: echarts json object
    Some sample echarts json objects:
    # Stacked Line Chart
    ```json
    {
        title: {
            text: 'Stacked Line'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['Email', 'Union Ads', 'Video Ads', 'Direct', 'Search Engine']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        toolbox: {
            feature: {
            saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
            name: 'Email',
            type: 'line',
            stack: 'Total',
            data: [120, 132, 101, 134, 90, 230, 210]
            },
            {
            name: 'Union Ads',
            type: 'line',
            stack: 'Total',
            data: [220, 182, 191, 234, 290, 330, 310]
            },
            {
            name: 'Video Ads',
            type: 'line',
            stack: 'Total',
            data: [150, 232, 201, 154, 190, 330, 410]
            },
            {
            name: 'Direct',
            type: 'line',
            stack: 'Total',
            data: [320, 332, 301, 334, 390, 330, 320]
            },
            {
            name: 'Search Engine',
            type: 'line',
            stack: 'Total',
            data: [820, 932, 901, 934, 1290, 1330, 1320]
            }
        ]
    };
    ```

    # Stacked Horizontal Bar Chart
    ```json
    {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
            // Use axis to trigger tooltip
            type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
            }
        },
        legend: {},
        xAxis: {
            type: 'value'
        },
        yAxis: {
            type: 'category',
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        series: [
            {
            name: 'Direct',
            type: 'bar',
            stack: 'total',
            label: {
                show: true
            },
            emphasis: {
                focus: 'series'
            },
            data: [320, 302, 301, 334, 390, 330, 320]
            },
            {
            name: 'Mail Ad',
            type: 'bar',
            stack: 'total',
            label: {
                show: true
            },
            emphasis: {
                focus: 'series'
            },
            data: [120, 132, 101, 134, 90, 230, 210]
            },
            {
            name: 'Affiliate Ad',
            type: 'bar',
            stack: 'total',
            label: {
                show: true
            },
            emphasis: {
                focus: 'series'
            },
            data: [220, 182, 191, 234, 290, 330, 310]
            },
            {
            name: 'Video Ad',
            type: 'bar',
            stack: 'total',
            label: {
                show: true
            },
            emphasis: {
                focus: 'series'
            },
            data: [150, 212, 201, 154, 190, 330, 410]
            },
            {
            name: 'Search Engine',
            type: 'bar',
            stack: 'total',
            label: {
                show: true
            },
            emphasis: {
                focus: 'series'
            },
            data: [820, 832, 901, 934, 1290, 1330, 1320]
            }
        ]
    };
    ```
    """,
    tools=[get_data_tables],
    output_key="chart_objects",
    before_agent_callback=irrelevant_user_query_check,
)
