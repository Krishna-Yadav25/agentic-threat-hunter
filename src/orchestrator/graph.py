import sys
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.hypothesis_agent import run_hypothesis_agent
from agents.investigator_agent import run_investigation


class ThreatHuntState(TypedDict):
    hypothesis: str
    verdict: str


def hypothesis_node(state: ThreatHuntState) -> ThreatHuntState:
    print("\n[Orchestrator] Running Hypothesis Agent...")
    hypothesis = run_hypothesis_agent()
    print(f"[Orchestrator] Hypothesis generated:\n{hypothesis}\n")
    return {"hypothesis": hypothesis, "verdict": ""}


def investigator_node(state: ThreatHuntState) -> ThreatHuntState:
    print("[Orchestrator] Running Investigator Agent...")
    verdict = run_investigation(state["hypothesis"])
    print(f"[Orchestrator] Investigation complete.\n")
    return {"hypothesis": state["hypothesis"], "verdict": verdict}


def build_graph():
    graph = StateGraph(ThreatHuntState)

    graph.add_node("hypothesis", hypothesis_node)
    graph.add_node("investigator", investigator_node)

    graph.set_entry_point("hypothesis")
    graph.add_edge("hypothesis", "investigator")
    graph.add_edge("investigator", END)

    return graph.compile()


def run_pipeline():
    app = build_graph()
    result = app.invoke({"hypothesis": "", "verdict": ""})
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("AGENTIC THREAT HUNTING PIPELINE — STARTING")
    print("=" * 60)

    result = run_pipeline()

    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"\nHypothesis:\n{result['hypothesis']}")
    print(f"\nVerdict:\n{result['verdict']}")