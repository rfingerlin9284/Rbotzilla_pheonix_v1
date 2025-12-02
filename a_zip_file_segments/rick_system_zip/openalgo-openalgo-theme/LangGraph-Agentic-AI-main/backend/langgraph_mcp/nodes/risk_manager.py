from utils.redis_publisher import redis_publisher
import logging

logger = logging.getLogger(__name__)

async def risk_manager_node(state):
    agent_name = "RiskManager"
    logger.info(f"Entering {agent_name} node.")

    await redis_publisher.publish_event(
        channel="agent_status",
        event_type="agent_status",
        payload={
            "agent_id": agent_name,
            "status": "running",
            "message": f"{agent_name} is assessing risk."
        }
    )

    try:
        # Existing stub logic
        state.reasoning[agent_name] = "Stub: Risk within acceptable range"
        state.next_agent = "MarketSentinel"

        await redis_publisher.publish_event(
            channel="agent_status",
            event_type="agent_status",
            payload={
                "agent_id": agent_name,
                "status": "completed",
                "message": f"{agent_name} completed risk assessment.",
                "next_agent": state.next_agent
            }
        )
        logger.info(f"Exiting {agent_name} node.")
        return {
            "reasoning": state.reasoning,
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
