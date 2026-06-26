from langgraph.graph import StateGraph, START, END

from graph.state import DagenGoState
from agents.reasoning_agent import ReasoningAgent

reasoning_agent = ReasoningAgent()
builder = StateGraph(DagenGoState, reasoning_agent, START, END)
builder.add_node("reason",reasoning_agent.invoke)
builder.add_edge(START, "reason")
builder.add_edge("reason", END)
