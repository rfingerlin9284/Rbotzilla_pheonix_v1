import os

# Define folder and file structure
structure = {
    "langgraph_mcp": {
        "__init__.py": "",
        "agent_state.py": """
from pydantic import BaseModel
from typing import Optional, Dict

class AgentState(BaseModel):
    symbol: str
    timeframe: str
    signal_type: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Dict[str, str] = {}
    raw_data: Dict[str, any] = {}
    next_agent: Optional[str] = None
""",
        "graph.py": """
from langgraph.graph import StateGraph, END
from langgraph_mcp.agent_state import AgentState
from langgraph_mcp.nodes.chart_analyst import chart_analyst_node
from langgraph_mcp.nodes.macro_forecaster import macro_forecaster_node
from langgraph_mcp.nodes.risk_manager import risk_manager_node
from langgraph_mcp.nodes.market_sentinel import market_sentinel_node
from langgraph_mcp.nodes.tacticbot import tacticbot_node
from langgraph_mcp.nodes.platform_pilot import platform_pilot_node

builder = StateGraph(AgentState)

builder.add_node("ChartAnalyst", chart_analyst_node)
builder.add_node("MacroForecaster", macro_forecaster_node)
builder.add_node("RiskManager", risk_manager_node)
builder.add_node("MarketSentinel", market_sentinel_node)
builder.add_node("TacticBot", tacticbot_node)
builder.add_node("PlatformPilot", platform_pilot_node)

builder.set_entry_point("ChartAnalyst")
builder.add_edge("ChartAnalyst", "MacroForecaster")
builder.add_edge("MacroForecaster", "RiskManager")
builder.add_edge("RiskManager", "MarketSentinel")
builder.add_edge("MarketSentinel", "TacticBot")
builder.add_edge("TacticBot", "PlatformPilot")
builder.add_edge("PlatformPilot", END)

agent_graph = builder.compile()
""",
        "nodes": {
            "__init__.py": "",
            "chart_analyst.py": """
def chart_analyst_node(state):
    state.reasoning["ChartAnalyst"] = "Stub: Chart analysis complete"
    state.signal_type = "BUY"
    state.confidence = 0.85
    state.next_agent = "MacroForecaster"
    return state
""",
            "macro_forecaster.py": """
def macro_forecaster_node(state):
    state.reasoning["MacroForecaster"] = "Stub: Macro forecast positive"
    state.next_agent = "RiskManager"
    return state
""",
            "risk_manager.py": """
def risk_manager_node(state):
    state.reasoning["RiskManager"] = "Stub: Risk within acceptable range"
    state.next_agent = "MarketSentinel"
    return state
""",
            "market_sentinel.py": """
def market_sentinel_node(state):
    state.reasoning["MarketSentinel"] = "Stub: Market volatility low"
    state.next_agent = "TacticBot"
    return state
""",
            "tacticbot.py": """
def tacticbot_node(state):
    state.reasoning["TacticBot"] = "Stub: Executing BUY"
    state.next_agent = "PlatformPilot"
    return state
""",
            "platform_pilot.py": """
def platform_pilot_node(state):
    state.reasoning["PlatformPilot"] = "Stub: Signal dispatched"
    state.next_agent = None
    return state
"""
        }
    }
}

def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w") as f:
                f.write(content.strip() + "\n")

if __name__ == "__main__":
    base = os.getcwd()
    create_structure(base, structure)
    print("✅ MCP LangGraph folder structure generated.")
