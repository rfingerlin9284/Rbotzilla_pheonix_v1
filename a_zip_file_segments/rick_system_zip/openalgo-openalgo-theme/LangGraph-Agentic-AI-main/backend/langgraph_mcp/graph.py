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
