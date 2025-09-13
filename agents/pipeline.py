from __future__ import annotations

import asyncio
from typing import List, Optional
from uuid import uuid4

from pentest_schemas import Target, PentestTask, TaskType
from agents.base import BasePentestAgent
from agents.recon import ReconAgent
from agents.scan import ScanAgent
from agents.exploit import ExploitAgent
from agents.analysis import AnalysisAgent
from agents.adapters.common import SimpleCLIToolAdapter


def _id() -> str:
    return uuid4().hex


def build_ffuf_adapter() -> SimpleCLIToolAdapter:
    return SimpleCLIToolAdapter(name="ffuf", base_cmd=["ffuf"], default_args=["-s"])  # silent


def build_sqlmap_adapter() -> SimpleCLIToolAdapter:
    # Adjust base_cmd if sqlmap is not on PATH (e.g., use python -m sqlmap if needed)
    return SimpleCLIToolAdapter(name="sqlmap", base_cmd=["sqlmap"])  # expects on PATH


async def run_mvp_pipeline(
    base_url: str,
    *,
    wordlist: Optional[str] = None,
    crawl_depth: int = 2,
    max_urls: int = 200,
    concurrency: int = 10,
) -> dict:
    """Run Recon -> Scan -> Exploit -> Analysis pipeline against a base URL.

    Returns a dict with run artifacts for quick inspection.
    """
    target = Target(base_url=base_url, allowed_hosts=[], disallowed_paths=[])

    # Instantiate agents and register adapters
    recon = ReconAgent(tools=[build_ffuf_adapter()])
    scan = ScanAgent(tools=[build_sqlmap_adapter()])
    exploit = ExploitAgent(tools=[build_sqlmap_adapter()])
    analysis = AnalysisAgent()

    # Recon task
    recon_task = PentestTask(
        id=_id(),
        type=TaskType.RECON,
        target=target,
        params={
            "crawl_depth": crawl_depth,
            "max_urls": max_urls,
            "concurrency": concurrency,
            "wordlist": wordlist,
        },
    )
    r_res = await recon.run(recon_task)

    # Gather URLs for scan
    scan_urls: List[str] = []
    for t in r_res.derived_tasks:
        if t.type == TaskType.SCAN:
            scan_urls.extend(t.urls)

    scan_task = PentestTask(
        id=_id(),
        type=TaskType.SCAN,
        target=target,
        urls=scan_urls[:200],
        params={"concurrency": concurrency},
    )
    s_res = await scan.run(scan_task)

    # Collect EXPLOIT tasks
    exploit_urls: List[str] = []
    for t in s_res.derived_tasks:
        if t.type == TaskType.EXPLOIT:
            exploit_urls.extend(t.urls)

    e_res = None
    if exploit_urls:
        e_task = PentestTask(
            id=_id(),
            type=TaskType.EXPLOIT,
            target=target,
            urls=list(dict.fromkeys(exploit_urls))[:20],
        )
        e_res = await exploit.run(e_task)

    # Analysis aggregates all findings
    all_findings = []
    all_findings.extend(s_res.findings)
    if e_res:
        all_findings.extend(e_res.findings)

    a_task = PentestTask(
        id=_id(),
        type=TaskType.ANALYZE,
        target=target,
        hints={"findings": all_findings},
    )
    a_res = await analysis.run(a_task)

    return {
        "recon": r_res,
        "scan": s_res,
        "exploit": e_res,
        "analysis": a_res,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m agents.pipeline <base_url> [wordlist]")
        sys.exit(1)
    base = sys.argv[1]
    wl = sys.argv[2] if len(sys.argv) > 2 else None

    async def _main():
        res = await run_mvp_pipeline(base, wordlist=wl)
        # Print summary lines from analysis logs
        for line in res["analysis"].logs:
            if line.startswith("# Pentest Findings") or line.startswith("-"):
                print(line)

    asyncio.run(_main())

