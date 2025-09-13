from __future__ import annotations

import asyncio
import re
from typing import Dict, List, Set, Tuple, Optional
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import httpx

from pentest_schemas import PentestTask, AgentResult, TaskType
from agents.base import BasePentestAgent, AgentContext

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.state import CompiledStateGraph
except Exception:  # pragma: no cover
    StateGraph = None  # type: ignore
    END = None  # type: ignore
    CompiledStateGraph = None  # type: ignore


HREF_RE = re.compile(r"href=[\"\']([^\"\'#]+)")
SRC_RE = re.compile(r"src=[\"\']([^\"\'#]+)")


def _gen_task_id() -> str:
    return uuid4().hex


def _same_host(url: str, allowed_hosts: List[str]) -> bool:
    host = urlparse(url).netloc.lower()
    return (not allowed_hosts) or (host in {h.lower() for h in allowed_hosts})


class ReconAgent(BasePentestAgent):
    """Reconnaissance/Enumeration agent.

    - Lightweight async crawler (same-host, limited depth)
    - Simple tech fingerprint based on headers
    - Optional directory fuzzing via `ffuf` tool adapter
    - Produces derived SCAN tasks for discovered URLs
    """

    def __init__(self, tools: Optional[List] = None):
        super().__init__(name="recon", tools=tools)

    async def _execute(self, task: PentestTask, result: AgentResult, ctx: AgentContext) -> None:
        base_url = task.target.base_url.rstrip("/")
        allowed_hosts = task.target.allowed_hosts or [urlparse(base_url).netloc]
        crawl_depth = int(task.params.get("crawl_depth", 2))
        max_urls = int(task.params.get("max_urls", 200))
        concurrency = int(task.params.get("concurrency", 10))

        urls, requests_made = await self._crawl(base_url, allowed_hosts, crawl_depth, max_urls, concurrency)
        self.log(result, f"Crawled {len(urls)} URLs (requests={requests_made})")

        headers_info = await self._fingerprint(base_url)
        if headers_info:
            result.logs.append(f"[fingerprint] {headers_info}")

        # Optional ffuf adapter
        ffuf = ctx.tools.get("ffuf")
        if ffuf is not None and await ffuf.available():
            wordlist = task.params.get("wordlist")  # path to a wordlist if provided
            ffuf_args = [
                "-u",
                f"{base_url}/FUZZ",
                "-mc",
                "200,204,301,302,307,401,403",
            ]
            if wordlist:
                ffuf_args += ["-w", wordlist]
            else:
                # tiny built-in list via -w -, feed on stdin
                ffuf_args += ["-w", "-"]
            # Try JSON output to stdout if supported (-of json -o -). If not, we still capture stdout.
            ffuf_args += ["-of", "json", "-o", "-"]

            payload = ("\n".join(["admin", "login", "api", "config", ".git", "backup"]).encode())
            ff = await ffuf.run(args=ffuf_args, timeout=float(task.params.get("ffuf_timeout", 60)), input_bytes=payload if not wordlist else None)
            result.logs.append(f"[ffuf] cmd={ff.get('cmd')} exit={ff.get('exit_code')} timed_out={ff.get('timed_out')}")
            if ff.get("stdout"):
                # Keep a short snippet for logs
                snippet = ff["stdout"][:1000]
                result.logs.append(f"[ffuf:stdout]\n{snippet}")

        # Create derived scan tasks for discovered URLs
        derived: List[PentestTask] = []
        for u in sorted(urls):
            if not _same_host(u, allowed_hosts):
                continue
            derived.append(
                PentestTask(
                    id=_gen_task_id(),
                    type=TaskType.SCAN,
                    target=task.target,
                    urls=[u],
                    priority=task.priority,
                    hints={"from": "recon", "fingerprint": headers_info},
                )
            )

        result.derived_tasks.extend(derived)
        result.metrics.requests_made = requests_made

    def _build_graph(self) -> Optional[CompiledStateGraph]:
        if StateGraph is None:
            return None

        g = StateGraph(dict)

        async def prepare(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            base_url = task.target.base_url.rstrip("/")
            allowed_hosts = task.target.allowed_hosts or [urlparse(base_url).netloc]
            state.update({
                "base_url": base_url,
                "allowed_hosts": allowed_hosts,
                "crawl_depth": int(task.params.get("crawl_depth", 2)),
                "max_urls": int(task.params.get("max_urls", 200)),
                "concurrency": int(task.params.get("concurrency", 10)),
            })
            return state

        async def crawl(state: Dict[str, Any]) -> Dict[str, Any]:
            result: AgentResult = state["result"]
            urls, requests_made = await self._crawl(
                state["base_url"], state["allowed_hosts"], state["crawl_depth"], state["max_urls"], state["concurrency"]
            )
            self.log(result, f"Crawled {len(urls)} URLs (requests={requests_made})")
            state.update({"urls": urls, "requests_made": requests_made})
            return state

        async def fingerprint(state: Dict[str, Any]) -> Dict[str, Any]:
            result: AgentResult = state["result"]
            headers_info = await self._fingerprint(state["base_url"])
            if headers_info:
                result.logs.append(f"[fingerprint] {headers_info}")
            state["headers_info"] = headers_info
            return state

        async def ffuf_step(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            result: AgentResult = state["result"]
            ctx: AgentContext = state["ctx"]
            ffuf = ctx.tools.get("ffuf")
            base_url: str = state["base_url"]
            if ffuf is not None and await ffuf.available():
                wordlist = task.params.get("wordlist")
                ffuf_args = [
                    "-u", f"{base_url}/FUZZ",
                    "-mc", "200,204,301,302,307,401,403",
                    "-of", "json", "-o", "-",
                ]
                if wordlist:
                    ffuf_args += ["-w", wordlist]
                else:
                    ffuf_args += ["-w", "-"]
                payload = ("\n".join(["admin", "login", "api", "config", ".git", "backup"]).encode())
                ff = await ffuf.run(args=ffuf_args, timeout=float(task.params.get("ffuf_timeout", 60)), input_bytes=payload if not wordlist else None)
                result.logs.append(f"[ffuf] cmd={ff.get('cmd')} exit={ff.get('exit_code')} timed_out={ff.get('timed_out')}")
                if ff.get("stdout"):
                    snippet = ff["stdout"][:1000]
                    result.logs.append(f"[ffuf:stdout]\n{snippet}")
            return state

        async def derive(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            result: AgentResult = state["result"]
            allowed_hosts: List[str] = state["allowed_hosts"]
            headers_info: Dict[str, str] = state.get("headers_info", {})
            urls: Set[str] = state.get("urls", set())
            derived: List[PentestTask] = []
            for u in sorted(urls):
                if not _same_host(u, allowed_hosts):
                    continue
                derived.append(
                    PentestTask(
                        id=_gen_task_id(),
                        type=TaskType.SCAN,
                        target=task.target,
                        urls=[u],
                        priority=task.priority,
                        hints={"from": "recon", "fingerprint": headers_info},
                    )
                )
            result.derived_tasks.extend(derived)
            result.metrics.requests_made = state.get("requests_made", 0)
            return state

        g.add_node("prepare", prepare)
        g.add_node("crawl", crawl)
        g.add_node("fingerprint", fingerprint)
        g.add_node("ffuf", ffuf_step)
        g.add_node("derive", derive)
        g.set_entry_point("prepare")
        g.add_edge("prepare", "crawl")
        g.add_edge("crawl", "fingerprint")
        g.add_edge("fingerprint", "ffuf")
        g.add_edge("ffuf", "derive")
        g.add_edge("derive", END)
        return g.compile()

    async def _fingerprint(self, url: str) -> Dict[str, str]:
        info: Dict[str, str] = {}
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                resp = await client.get(url)
                # Simple header-based hints
                for k in ["server", "x-powered-by", "via", "content-type"]:
                    if k in resp.headers:
                        info[k] = resp.headers.get(k, "")
        except Exception:
            pass
        return info

    async def _crawl(
        self,
        base_url: str,
        allowed_hosts: List[str],
        max_depth: int,
        max_urls: int,
        concurrency: int,
    ) -> Tuple[Set[str], int]:
        visited: Set[str] = set()
        queue: asyncio.Queue[Tuple[str, int]] = asyncio.Queue()
        await queue.put((base_url, 0))
        visited.add(base_url)
        in_flight = 0
        requests_made = 0
        sem = asyncio.Semaphore(concurrency)

        async def worker():
            nonlocal requests_made, in_flight
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                while True:
                    try:
                        url, depth = await asyncio.wait_for(queue.get(), timeout=0.1)
                    except asyncio.TimeoutError:
                        return
                    if depth >= max_depth:
                        queue.task_done()
                        continue
                    async with sem:
                        try:
                            in_flight += 1
                            resp = await client.get(url)
                            requests_made += 1
                            text = resp.text or ""
                            for link in self._extract_links(url, text):
                                if len(visited) >= max_urls:
                                    break
                                if link in visited:
                                    continue
                                if not _same_host(link, allowed_hosts):
                                    continue
                                visited.add(link)
                                await queue.put((link, depth + 1))
                        except Exception:
                            pass
                        finally:
                            in_flight -= 1
                            queue.task_done()

        workers = [asyncio.create_task(worker()) for _ in range(max(1, concurrency // 2))]
        await queue.join()
        for w in workers:
            w.cancel()
        return visited, requests_made

    def _extract_links(self, base: str, html: str) -> Set[str]:
        urls: Set[str] = set()
        for m in HREF_RE.finditer(html):
            urls.add(urljoin(base, m.group(1)))
        for m in SRC_RE.finditer(html):
            urls.add(urljoin(base, m.group(1)))
        return urls


__all__ = ["ReconAgent"]
