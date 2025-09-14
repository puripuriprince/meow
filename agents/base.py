from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
import time

try:
    # LangGraph is used to structure agent internals as a small state machine.
    from langgraph.graph import StateGraph, END
    from langgraph.graph.state import CompiledStateGraph
except Exception:  # pragma: no cover - allow runtime without langgraph installed
    StateGraph = None  # type: ignore
    END = None  # type: ignore
    CompiledStateGraph = None  # type: ignore

from pentest_schemas import (
    PentestTask,
    AgentResult,
    AgentMetrics,
)


@dataclass
class AgentContext:
    """Lightweight runtime context for an agent execution."""

    tools: Dict[str, ToolAdapter] = field(default_factory=dict)


class BasePentestAgent(ABC):
    """Base class for specialized pentest agents.

    Agents consume a `PentestTask` and return a normalized `AgentResult`.
    Subclasses implement `_execute` and may use registered `ToolAdapter`s.
    """

    def __init__(self, name: str, tools: Optional[List[ToolAdapter]] = None):
        self.name = name
        self._tools: Dict[str, ToolAdapter] = {t.name: t for t in (tools or [])}
        # Build a LangGraph-based internal graph if available; fall back to direct _execute
        self._graph: Optional[CompiledStateGraph] = None
        try:
            self._graph = self._build_graph()
        except Exception:
            # If graph construction fails (e.g., langgraph not installed), run() will call _execute.
            self._graph = None

    def register_tool(self, adapter: ToolAdapter) -> None:
        self._tools[adapter.name] = adapter

    def get_tool(self, name: str) -> Optional[ToolAdapter]:
        return self._tools.get(name)

    async def run(self, task: PentestTask) -> AgentResult:
        start = time.perf_counter()
        result = AgentResult(task_id=task.id)
        try:
            ctx = AgentContext(tools=self._tools)
            if self._graph is not None:
                # Use LangGraph state machine
                state = {"task": task, "result": result, "ctx": ctx}
                await self._graph.ainvoke(state)
            else:
                # Fallback to direct execution
                await self._execute(task, result, ctx)
            return result
        finally:
            duration_ms = (time.perf_counter() - start) * 1000.0
            result.metrics = result.metrics or AgentMetrics()
            result.metrics.duration_ms = duration_ms

    def log(self, result: AgentResult, message: str) -> None:
        result.logs.append(f"[{self.name}] {message}")

    @abstractmethod
    async def _execute(
        self,
        task: PentestTask,
        result: AgentResult,
        ctx: AgentContext,
    ) -> None:
        """Implement agent-specific logic and populate `result`."""
        raise NotImplementedError

    def _build_graph(self) -> Optional[CompiledStateGraph]:
        """Optional LangGraph state graph for the agent.

        Default implementation wraps `_execute` in a single-node graph. Subclasses
        can override to define richer multi-step graphs. If LangGraph is unavailable,
        returns None so `run()` falls back to `_execute`.
        """
        if StateGraph is None:
            return None

        async def _run_node(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            result: AgentResult = state["result"]
            ctx: AgentContext = state["ctx"]
            await self._execute(task, result, ctx)
            return state

        g = StateGraph(dict)
        g.add_node("run", _run_node)
        g.set_entry_point("run")
        return g.compile()


__all__ = ["ToolAdapter", "AgentContext", "BasePentestAgent"]
