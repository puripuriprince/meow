from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any
import json


@dataclass
class ToolResult:
    """Result from running a tool adapter."""
    cmd: list[str] | None = None
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False
    duration_ms: Optional[float] = None
    parsed_data: Optional[Any] = None
    
    def parse_json(self) -> Optional[Any]:
        """Try to parse stdout as JSON and cache in parsed_data."""
        if self.parsed_data is None and self.stdout.strip():
            try:
                self.parsed_data = json.loads(self.stdout)
            except json.JSONDecodeError:
                pass
        return self.parsed_data


class ToolAdapter(ABC):
    """Base interface for tool adapters."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name identifier."""
        pass
    
    @abstractmethod
    async def available(self) -> bool:
        """Check if tool is available on the system."""
        pass
    
    @abstractmethod
    async def run(self, cmd: list[str], **kwargs) -> ToolResult:
        """Run the tool with given parameters."""
        pass

import asyncio
import os
import shutil
import time
from typing import Dict, List


def which(cmd: str) -> Optional[str]:
    """Return full path if executable is on PATH, else None."""
    return shutil.which(cmd)


async def run_command(
    args: List[str],
    *,
    timeout: float = 60.0,
    input_bytes: Optional[bytes] = None,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
) -> ToolResult:
    """Run a CLI command asynchronously with timeout and capture output."""
    start = time.perf_counter()
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE if input_bytes is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env={**os.environ, **(env or {})} if env else None,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=input_bytes), timeout=timeout
        )
        timed_out = False
    except asyncio.TimeoutError:
        proc.kill()
        stdout, stderr = await proc.communicate()
        timed_out = True

    duration_ms = (time.perf_counter() - start) * 1000.0
    stdout_text = stdout.decode(errors="replace") if stdout is not None else ""
    stderr_text = stderr.decode(errors="replace") if stderr is not None else ""

    return ToolResult(
        cmd=args,
        stdout=stdout_text,
        stderr=stderr_text,
        exit_code=proc.returncode or 0,
        timed_out=timed_out,
        duration_ms=duration_ms,
    )


__all__ = ["ToolAdapter", "ToolResult", "which", "run_command"]

