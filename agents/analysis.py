from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

from pentest_schemas import (
    PentestTask,
    AgentResult,
    Finding,
    Severity,
    TaskType,
)
from agents.base import BasePentestAgent, AgentContext

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.state import CompiledStateGraph
except Exception:  # pragma: no cover
    StateGraph = None  # type: ignore
    END = None  # type: ignore
    CompiledStateGraph = None  # type: ignore


def _key(f: Finding) -> Tuple[str, str, str]:
    return (f.category, f.url or "", f.param or "")


class AnalysisAgent(BasePentestAgent):
    """Aggregate/dedupe findings and produce a minimal report artifact.

    MVP: merges duplicates by (category,url,param), promotes severity heuristically,
    and emits a Markdown report in logs.
    """

    def __init__(self):
        super().__init__(name="analysis")

    async def _execute(self, task: PentestTask, result: AgentResult, ctx: AgentContext) -> None:
        # The orchestrator can pass findings in hints for this MVP
        input_findings: List[Finding] = task.hints.get("findings", [])
        merged = self._dedupe(input_findings)
        scored = self._score(merged)

        result.findings.extend(scored)
        report = self._render_markdown(scored)
        result.logs.append(report)

    def _build_graph(self) -> Optional[CompiledStateGraph]:
        if StateGraph is None:
            return None

        g = StateGraph(dict)

        async def collect(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            state["input_findings"] = task.hints.get("findings", [])
            return state

        async def dedupe(state: Dict[str, Any]) -> Dict[str, Any]:
            merged = self._dedupe(state.get("input_findings", []))
            state["merged"] = merged
            return state

        async def score(state: Dict[str, Any]) -> Dict[str, Any]:
            scored = self._score(state.get("merged", []))
            state["scored"] = scored
            return state

        async def render(state: Dict[str, Any]) -> Dict[str, Any]:
            result: AgentResult = state["result"]
            findings = state.get("scored", [])
            result.findings.extend(findings)
            report = self._render_markdown(findings)
            result.logs.append(report)
            return state

        g.add_node("collect", collect)
        g.add_node("dedupe", dedupe)
        g.add_node("score", score)
        g.add_node("render", render)
        g.set_entry_point("collect")
        g.add_edge("collect", "dedupe")
        g.add_edge("dedupe", "score")
        g.add_edge("score", "render")
        g.add_edge("render", END)
        return g.compile()

    def _dedupe(self, findings: List[Finding]) -> List[Finding]:
        buckets: Dict[Tuple[str, str, str], List[Finding]] = defaultdict(list)
        for f in findings:
            buckets[_key(f)].append(f)

        merged: List[Finding] = []
        for k, group in buckets.items():
            # Keep the highest confidence/severity instance, merge evidence lists
            best = max(
                group,
                key=lambda f: (
                    ["low", "medium", "high"].index(f.confidence.value),
                    ["info", "low", "medium", "high", "critical"].index(f.severity.value),
                ),
            )
            if len(group) > 1:
                ev = []
                for g in group:
                    ev.extend(g.evidence)
                best.evidence = ev[:5]  # cap
            merged.append(best)
        return merged

    def _score(self, findings: List[Finding]) -> List[Finding]:
        # Placeholder scoring; already set by producers, but we can bump critical SQLi confirmations
        for f in findings:
            if f.category == "sqli" and f.status.value == "confirmed":
                f.severity = Severity.CRITICAL
        return findings

    def _render_markdown(self, findings: List[Finding]) -> str:
        lines = ["# Pentest Findings (MVP)"]
        for f in findings:
            lines.append(
                f"- [{f.severity.value.upper()}] {f.category} at {f.url or 'unknown'}"
                + (f" param={f.param}" if f.param else "")
            )
        return "\n".join(lines)


__all__ = ["AnalysisAgent"]
