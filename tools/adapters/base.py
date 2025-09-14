# base adapter interface, like:
# class ToolAdapter:
#     async def available(self) -> bool
#     async def run(self, **kwargs) -> ToolResult
# Where ToolResult is a class that holds:
# 
# stdout (text / JSON),
# 
# stderr,
# 
# exit_code,
# 
# possibly parsed data (if JSON or other parseable format),
# 
# maybe a flag for timeout or failure.
# 
# The other adapters should implement this interface.


# Sketch code below - something I pulled off of the internet which can help
from __future__ import annotations

import asyncio
import os
import shlex
import shutil
import time
from typing import Dict, List, Optional, Any


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
) -> Dict[str, Any]:
    """Run a CLI command asynchronously with timeout and capture output.

    Returns a dict with: exit_code, stdout, stderr, timed_out, duration_ms, args.
    """
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

    return {
        "args": args,
        "exit_code": proc.returncode,
        "stdout": stdout_text,
        "stderr": stderr_text,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
    }


def format_cmd(args: List[str]) -> str:
    """Pretty-print a command for logs (approximate quoting)."""
    # On Windows, shlex.join may not reflect PowerShell quoting; this is best-effort.
    try:
        return shlex.join(args)
    except Exception:
        return " ".join(args)


__all__ = ["which", "run_command", "format_cmd"]

