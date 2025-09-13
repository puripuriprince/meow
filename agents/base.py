from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
import time

from pentest_schemas import (
    PentestTask,
    AgentResult,
    AgentMetrics,
)


class ToolAdapter(Protocol):
    """Interface for tool adapters used by agents.

    Concrete implementations will wrap a CLI or API (e.g., ffuf, ZAP, sqlmap)
    and expose a uniform async `run` method.
    """

    name: str

    async def available(self) -> bool:
        ...

    async def run(self, **kwargs) -> Dict[str, Any]:
        ...


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

    def register_tool(self, adapter: ToolAdapter) -> None:
        self._tools[adapter.name] = adapter

    def get_tool(self, name: str) -> Optional[ToolAdapter]:
        return self._tools.get(name)

    async def run(self, task: PentestTask) -> AgentResult:
        start = time.perf_counter()
        result = AgentResult(task_id=task.id)
        try:
            await self._execute(task, result, AgentContext(tools=self._tools))
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


__all__ = ["ToolAdapter", "AgentContext", "BasePentestAgent"]

