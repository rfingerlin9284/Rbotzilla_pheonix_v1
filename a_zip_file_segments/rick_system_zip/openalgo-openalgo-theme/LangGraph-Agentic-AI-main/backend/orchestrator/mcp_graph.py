from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
import asyncio
import logging

from backend.agents.chartanalyst.agent import ChartAnalystAgent
from backend.agents.macroforecaster.main import MacroforecasterAgent
from backend.agents.marketdatafetcher.agent import MarketDataFetcherAgent
from backend.agents.marketsentinel.main import MarketsentinelAgent
from backend.agents.platformpilot.main import PlatformpilotAgent
from backend.agents.riskmanager.agent import RiskManagerAgent
from backend.agents.tacticbot.main import TacticbotAgent
from backend.orchestrator.event_bus import event_bus
from backend.ai_client import AIModelClient

logger = logging.getLogger(__name__)

# Initialize AI client (can be passed to agents if needed)
ai_client = AIModelClient()

# Initialize agents (these will be used within the nodes)
market_data_fetcher_agent = MarketDataFetcherAgent(name="MarketDataFetcher")
chart_analyst_agent = ChartAnalystAgent(api_client=ai_client, name="ChartAnalyst")
macro_forecaster_agent = MacroforecasterAgent(api_client=ai_client, name="MacroForecaster")
risk_manager_agent = RiskManagerAgent(api_client=ai_client, name="RiskManager")
tactic_bot_agent = TacticbotAgent(api_client=ai_client, name="TacticBot")
platform_pilot_agent = PlatformpilotAgent(api_client=ai_client, name="PlatformPilot")

async def initialize_agents_for_graph():
    await market_data_fetcher_agent.initialize(event_bus)
    await chart_analyst_agent.initialize(event_bus)
    await macro_forecaster_agent.initialize(event_bus)
    await risk_manager_agent.initialize(event_bus)
    await tactic_bot_agent.initialize(event_bus)
    await platform_pilot_agent.initialize(event_bus)

# Node functions that call agent's process_message
async def market_data_fetcher_node(state: dict) -> dict:
    logger.info("Running market data fetcher node")
    # Simulate a request for market data
    await market_data_fetcher_agent.process_message(
        "market_data_requests", 
        {"symbol": state["symbol"], "timeframe": state["timeframe"]}
    )
    # For LangGraph, we need to return the updated state. 
    # In a real scenario, the agent would publish to event_bus, and we'd listen.
    # For simplicity here, we'll just add a dummy market_data to the state.
    fetched_data = {
        "symbol": state["symbol"],
        "timeframe": state["timeframe"],
        "price": 1.0850, 
        "volume": 100000,
        "timestamp": "2025-08-12T10:00:00Z"
    }
    return {**state, "market_data": fetched_data}

async def chart_analyst_node(state: dict) -> dict:
    logger.info("Running chart analyst node")
    # Pass the fetched market data to the chart analyst
    await chart_analyst_agent.process_message("market_data", state.get("market_data", {}))
    # Simulate chart analysis result
    chart_analysis_result = f"Chart analysis for {state['symbol']} on {state['timeframe']} using data: {state.get('market_data', 'N/A')}"
    return {**state, "chart_analysis": chart_analysis_result}

async def macro_forecaster_node(state: dict) -> dict:
    logger.info("Running macro forecaster node")
    # Simulate macro forecast based on some input (e.g., market sentiment)
    await macro_forecaster_agent.process_message("market_sentiment_analysis", {"sentiment_data": "some sentiment"})
    macro_outlook_result = f"Macro outlook for {state['symbol']}"
    return {**state, "macro_outlook": macro_outlook_result}

async def risk_manager_node(state: dict) -> dict:
    logger.info("Running risk manager node")
    # Simulate risk assessment based on chart analysis and macro outlook
    await risk_manager_agent.process_message("technical_signals", {"signal": state.get("chart_analysis"), "macro": state.get("macro_outlook")})
    risk_score_result = f"Risk score for {state['symbol']}"
    return {**state, "risk_score": risk_score_result}

async def tactic_bot_node(state: dict) -> dict:
    logger.info("Running tactic bot node")
    # Simulate trading decision based on risk score
    await tactic_bot_agent.process_message("riskmanager_out", {"risk_assessment": state.get("risk_score")})
    decision = f"Execute BUY order on {state['symbol']}" if "EURUSD" in state["symbol"] else "HOLD"
    return {**state, "decision": decision}

# ✅ Main MCP function called by FastAPI
async def run_mcp_pipeline(symbol: str, timeframe: str) -> dict:
    initial_state = {"symbol": symbol, "timeframe": timeframe}

    # Build the graph
    builder = StateGraph(dict)

    # Add nodes
    builder.add_node("market_data_fetcher", RunnableLambda(market_data_fetcher_node))
    builder.add_node("chart_analyst", RunnableLambda(chart_analyst_node))
    builder.add_node("macro_forecaster", RunnableLambda(macro_forecaster_node))
    builder.add_node("risk_manager", RunnableLambda(risk_manager_node))
    builder.add_node("tactic_bot", RunnableLambda(tactic_bot_node))

    # Set node execution order
    builder.set_entry_point("market_data_fetcher")
    builder.add_edge("market_data_fetcher", "chart_analyst")
    builder.add_edge("chart_analyst", "macro_forecaster")
    builder.add_edge("macro_forecaster", "risk_manager")
    builder.add_edge("risk_manager", "tactic_bot")
    builder.set_finish_point("tactic_bot")

    # Compile and run
    graph = builder.compile()
    result = await graph.ainvoke(initial_state)
    return result

# Initialize agents when this module is imported
asyncio.create_task(initialize_agents_for_graph())