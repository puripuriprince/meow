from __future__ import annotations

from typing import Any, Dict, Optional, List

from agents.tool_runner import which, run_command, format_cmd


class SimpleCLIToolAdapter:
    """Minimal CLI tool adapter implementing the ToolAdapter Protocol.

    Usage:
        ffuf = SimpleCLIToolAdapter(
            name="ffuf",
            base_cmd=["ffuf"],
            default_args=["-s"],
        )
        await ffuf.available()
        await ffuf.run(args=["-u", url, "-w", wordlist])
    """

    def __init__(
        self,
        *,
        name: str,
        base_cmd: List[str],
        default_args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        self.name = name
        self._base_cmd = base_cmd
        self._default_args = default_args or []
        self._cwd = cwd
        self._env = env or {}

    async def available(self) -> bool:
        exe = self._base_cmd[0]
        return which(exe) is not None

    async def run(
        self,
        *,
        args: Optional[List[str]] = None,
        timeout: float = 60.0,
        input_bytes: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        cmd = [*self._base_cmd, *self._default_args, *(args or [])]
        result = await run_command(
            cmd, timeout=timeout, input_bytes=input_bytes, cwd=self._cwd, env=self._env
        )
        result["tool"] = self.name
        result["cmd"] = format_cmd(cmd)
        return result


__all__ = ["SimpleCLIToolAdapter"]

