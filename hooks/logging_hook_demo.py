import logging
import time
from uuid import uuid4

from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentState,
    Runtime,
    before_model,
    wrap_model_call,
    wrap_tool_call,
)

try:
    from llm_engineering.llm_provider import create_model
    from llm_engineering.tools.tool_demo import get_timezone, get_weather
except ModuleNotFoundError:  # pragma: no cover - supports running from repo root
    from llm_provider import create_model
    from tools.tool_demo import get_timezone, get_weather

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("agent")
request_id = uuid4().hex[:8]


@before_model
def log_model_step(state: AgentState, runtime: Runtime) -> dict:
    """Record basic agent progress without logging private prompt text."""
    messages = state["messages"]
    message_types = ",".join(type(message).__name__ for message in messages)
    logger.info(
        "request_id=%s event=before_model message_count=%d message_types=%s",
        request_id,
        len(messages),
        message_types,
    )
    return {}


@wrap_model_call
def log_model_timing(request, handler):
    started = time.perf_counter()
    try:
        response = handler(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "request_id=%s event=model_finished duration_ms=%.1f",
            request_id,
            elapsed_ms,
        )
        return response
    except Exception:
        logger.exception("request_id=%s event=model_failed", request_id)
        raise


@wrap_tool_call
def log_tool_call(request, handler):
    tool_name = request.tool_call["name"]
    argument_names = ",".join((request.tool_call.get("args") or {}).keys())
    started = time.perf_counter()
    logger.info(
        "request_id=%s event=tool_started tool=%s argument_names=%s",
        request_id,
        tool_name,
        argument_names,
    )
    try:
        response = handler(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "request_id=%s event=tool_finished tool=%s duration_ms=%.1f",
            request_id,
            tool_name,
            elapsed_ms,
        )
        return response
    except Exception:
        logger.exception(
            "request_id=%s event=tool_failed tool=%s",
            request_id,
            tool_name,
        )
        raise


agent = create_agent(
    model=create_model(),
    tools=[get_weather, get_timezone],
    middleware=[log_model_step, log_model_timing, log_tool_call],
)

question = input("Ask about weather or timezone: ").strip()
result = agent.invoke({"messages": [{"role": "user", "content": question}]})
logger.info(
    "request_id=%s event=agent_finished message_count=%d",
    request_id,
    len(result["messages"]),
)
print(result["messages"][-1].content)
