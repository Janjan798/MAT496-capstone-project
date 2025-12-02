from typing import Dict, Any

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

from .state import GraphState
from .tools import refresh_injuries, get_team_roster, get_injury_status


# LLM with tools bound
llm = ChatOpenAI(model="gpt-5").bind_tools([
    refresh_injuries,
    get_team_roster,
    get_injury_status,
])


def llm_node(state: GraphState) -> Dict[str, Any]:
    """
    Core node: takes the user_query, lets the LLM decide whether to call tools,
    executes any tool calls, and returns the final natural-language answer.
    """
    import json

    user_query = state.get("user_query", "").strip()
    if not user_query:
        return {"answer": ""}

    messages = [
        SystemMessage(content=(
            "You are an NBA injury assistant. Always use tools to refresh the "
            "injury dataset and to answer questions. Do not guess."
        )),
        HumanMessage(content=user_query),
    ]

    last_tool_output: str | None = None
    # Iterate: LLM -> (optional) tool calls -> tool outputs -> LLM ... until final content
    for round_idx in range(6):
        ai: AIMessage = llm.invoke(messages)

        tool_calls = getattr(ai, "tool_calls", None) or []
        if not tool_calls:
            content = (ai.content or "").strip()
            return {"answer": content}

        messages.append(ai)

        for call in tool_calls:
            name = call.get("name") or call.get("tool")
            args = call.get("args", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {"input": args}

            if name == "refresh_injuries":
                output = refresh_injuries.invoke({})
            elif name == "get_injury_status":
                output = get_injury_status.invoke({
                    "player_name": args.get("player_name") or args.get("name") or ""
                })
            elif name == "get_team_roster":
                output = get_team_roster.invoke({
                    "team_name": args.get("team_name") or args.get("team") or ""
                })
            else:
                output = f"Unknown tool: {name}"

            last_tool_output = str(output)
            messages.append(
                ToolMessage(
                    content=str(output),
                    tool_call_id=call.get("id") or name or "tool",
                )
            )

        # Nudge model to produce a final answer after tools
        messages.append(SystemMessage(content="Use the tool outputs above to answer the user now, concisely."))

    # Fallback: if no final content, surface the last tool output if available
    return {"answer": (last_tool_output or "").strip()}


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("chat", llm_node)
    builder.set_entry_point("chat")
    builder.set_finish_point("chat")

    memory = MemorySaver()
    app = builder.compile(checkpointer=memory)
    return app


# Re-export app
app = build_graph()
