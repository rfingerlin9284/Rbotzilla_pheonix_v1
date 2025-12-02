from utils.redis_publisher import redis_publisher
import logging

logger = logging.getLogger(__name__)

async def chart_analyst_node(state):
    agent_name = "ChartAnalyst"
    logger.info(f"Entering {agent_name} node.")
    
    await redis_publisher.publish_event(
        channel="agent_status",
        event_type="agent_status",
        payload={
            "agent_id": agent_name,
            "status": "running",
            "message": f"{agent_name} is starting analysis."
        }
    )

    try:
        # Existing stub logic
        state.reasoning[agent_name] = "Stub: Chart analysis complete"
        state.signal_type = "BUY"
        state.confidence = 0.85
        state.next_agent = "MacroForecaster"
        
        await redis_publisher.publish_event(
            channel="agent_status",
            event_type="agent_status",
            payload={
                "agent_id": agent_name,
                "status": "completed",
                "message": f"{agent_name} completed analysis.",
                "next_agent": state.next_agent
            }
        )
        logger.info(f"Exiting {agent_name} node.")
        return {
            "reasoning": state.reasoning,
            "signal_type": state.signal_type,
            "confidence": state.confidence,
            "next_agent": state.next_agent,
        }
    except Exception as e:
        logger.error(f"Error in {agent_name} node: {e}")
        await redis_publisher.publish_event(
            channel="agent_status",
            event_type="agent_status",
            payload={
                "agent_id": agent_name,
                "status": "failed",
                "message": f"{agent_name} failed with error: {e}"
            }
        )
        raise # Re-raise the exception to propagate it through the LangGraph
