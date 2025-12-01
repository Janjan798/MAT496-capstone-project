from typing import Dict, Any

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

from .state import GraphState
from .tools import get_team_roster, get_injury_status


# LLM with tools bound
llm = ChatOpenAI(model="gpt-5").bind_tools([
    get_team_roster,
    get_injury_status,
])


def llm_node(state: GraphState) -> Dict[str, Any]:
    """
    Core node: takes messages from state, lets LLM decide
    whether to call tools, and returns the new messages.
    """
    result = llm.invoke(state["messages"])
    return {"messages": [result]}


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
