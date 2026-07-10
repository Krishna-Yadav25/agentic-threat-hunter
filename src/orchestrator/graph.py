import sys
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.hypothesis_agent import run_hypothesis_agent
from agents.investigator_agent import run_investigation
from agents.reporting_agent import run_reporting_agent


class ThreatHuntState(TypedDict):
    hypothesis: str
    verdict: str
    report_path: str


def hypothesis_node(state: ThreatHuntState) -> ThreatHuntState:
    print("\n[Orchestrator] Running Hypothesis Agent...")
    hypothesis = run_hypothesis_agent()
    print(f"[Orchestrator] Hypothesis generated:\n{hypothesis}\n")
    return {"hypothesis": hypothesis, "verdict": "", "report_path": ""}


def investigator_node(state: ThreatHuntState) -> ThreatHuntState:
    print("[Orchestrator] Running Investigator Agent...")
    verdict = run_investigation(state["hypothesis"])
    print(f"[Orchestrator] Investigation complete.\n")
    return {"hypothesis": state["hypothesis"], "verdict": verdict, "report_path": ""}


def reporting_node(state: ThreatHuntState) -> ThreatHuntState:
    print("[Orchestrator] Running Reporting Agent...")
    report_path = run_reporting_agent(state["hypothesis"], state["verdict"])
    print(f"[Orchestrator] Report saved to: {report_path}\n")
    return {"hypothesis": state["hypothesis"], "verdict": state["verdict"], "report_path": report_path}


def build_graph():
    graph = StateGraph(ThreatHuntState)

    graph.add_node("hypothesis", hypothesis_node)
    graph.add_node("investigator", investigator_node)
    graph.add_node("reporting", reporting_node)

    graph.set_entry_point("hypothesis")
    graph.add_edge("hypothesis", "investigator")
    graph.add_edge("investigator", "reporting")
    graph.add_edge("reporting", END)

    return graph.compile()


def run_pipeline():
    app = build_graph()
    result = app.invoke({"hypothesis": "", "verdict": "", "report_path": ""})
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
    print(f"\nReport saved at: {result['report_path']}")