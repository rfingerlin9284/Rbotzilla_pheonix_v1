from utils.redis_publisher import redis_publisher
import logging

logger = logging.getLogger(__name__)

async def platform_pilot_node(state):
    agent_name = "PlatformPilot"
    logger.info(f"Entering {agent_name} node.")

    await redis_publisher.publish_event(
        channel="agent_status",
        event_type="agent_status",
        payload={
            "agent_id": agent_name,
            "status": "running",
            "message": f"{agent_name} is dispatching signal."
        }
    )

    try:
        # Existing stub logic
        state.reasoning[agent_name] = "Stub: Signal dispatched"
        state.next_agent = None # This is the end of the current graph flow

        await redis_publisher.publish_event(
            channel="agent_status",
            event_type="agent_status",
            payload={
                "agent_id": agent_name,
                "status": "completed",
                "message": f"{agent_name} dispatched signal.",
                "next_agent": state.next_agent # Will be None
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
