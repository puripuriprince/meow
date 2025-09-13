from __future__ import annotations

import asyncio
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from uuid import uuid4

import httpx

from pentest_schemas import (
    PentestTask,
    AgentResult,
    Finding,
    Evidence,
    HttpExcerpt,
    TaskType,
    Confidence,
    Severity,
    FindingStatus,
)
from agents.base import BasePentestAgent, AgentContext


SQL_ERROR_PATTERNS = [
    r"you have an error in your sql syntax;",
    r"warning: mysql",
    r"unclosed quotation mark after the character string",
    r"quoted string not properly terminated",
    r"oracle error",
    r"sqlite error",
    r"psql: error",
    r"syntax error at or near",
    r"invalid query",
    r"unknown column",
    r"mysql_fetch",
    r"ole db|odbc|jdbc",
]

XSS_PAYLOAD = "<script>alert(1337)</script>"
SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    '" OR "1"="1',
    "') OR ('1'='1",
]
COMMON_PARAMS = ["q", "search", "s", "id", "page"]


def _gen_id() -> str:
    return uuid4().hex


def _set_query_param(url: str, key: str, value: str) -> str:
    parts = list(urlparse(url))
    q = dict(parse_qsl(parts[4], keep_blank_values=True))
    q[key] = value
    parts[4] = urlencode(q, doseq=True)
    return urlunparse(parts)


class ScanAgent(BasePentestAgent):
    """Lightweight vulnerability detection (XSS, SQLi) with optional tool adapters.

    - Probes discovered URLs for basic reflected XSS and SQL errors
    - Optionally leverages `sqlmap` adapter in detection mode
    - Emits Findings and derives EXPLOIT tasks for higher-confidence signals
    """

    def __init__(self, tools: Optional[List] = None):
        super().__init__(name="scan", tools=tools)

    async def _execute(self, task: PentestTask, result: AgentResult, ctx: AgentContext) -> None:
        urls: List[str] = task.urls or []
        timeout = float(task.params.get("timeout", 10))
        concurrency = int(task.params.get("concurrency", 10))
        findings: List[Finding] = []

        sem = asyncio.Semaphore(concurrency)

        async def scan_one(url: str) -> Tuple[int, List[Finding]]:
            reqs = 0
            local_findings: List[Finding] = []
            try:
                async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
                    # XSS probe
                    f_xss, c1 = await self._probe_xss(client, url)
                    reqs += c1
                    if f_xss:
                        local_findings.append(f_xss)

                    # SQLi probe
                    f_sqli, c2 = await self._probe_sqli(client, url)
                    reqs += c2
                    if f_sqli:
                        local_findings.append(f_sqli)
            except Exception:
                pass
            return reqs, local_findings

        tasks = []
        for u in urls:
            async def bounded(u=u):
                async with sem:
                    return await scan_one(u)

            tasks.append(bounded())

        totals = await asyncio.gather(*tasks)
        requests_made = 0
        for reqs, f_list in totals:
            requests_made += reqs
            findings.extend(f_list)

        # sqlmap adapter (optional)
        sqlmap = ctx.tools.get("sqlmap")
        if sqlmap is not None and await sqlmap.available():
            for u in urls[:5]:  # limit for MVP
                res = await sqlmap.run(args=[
                    "-u",
                    u,
                    "--batch",
                    "--level",
                    "1",
                    "--risk",
                    "1",
                    "--smart",
                    "--flush-session",
                ], timeout=float(task.params.get("sqlmap_timeout", 90)))
                result.logs.append(f"[sqlmap] cmd={res.get('cmd')} exit={res.get('exit_code')} timed_out={res.get('timed_out')}")
                if res.get("stdout"):
                    parsed = self._parse_sqlmap_output(u, res["stdout"])
                    if parsed:
                        findings.append(parsed)
                        # derive EXPLOIT task
                        result.derived_tasks.append(
                            PentestTask(
                                id=_gen_id(),
                                type=TaskType.EXPLOIT,
                                target=task.target,
                                urls=[u],
                                hints={"from": "scan", "tool": "sqlmap"},
                                priority=task.priority,
                            )
                        )
                # Increment tool counts
                result.metrics.tool_invocations["sqlmap"] = result.metrics.tool_invocations.get("sqlmap", 0) + 1

        # attach findings
        result.findings.extend(findings)
        result.metrics.requests_made = (result.metrics.requests_made or 0) + requests_made
        result.metrics.signals_found = len(result.findings)

    async def _probe_xss(self, client: httpx.AsyncClient, url: str) -> Tuple[Optional[Finding], int]:
        reqs = 0
        parsed = urlparse(url)
        qparams = dict(parse_qsl(parsed.query, keep_blank_values=True))
        targets = list(qparams.keys()) or COMMON_PARAMS

        for p in targets[:5]:
            test_url = _set_query_param(url, p, XSS_PAYLOAD)
            try:
                resp = await client.get(test_url)
                reqs += 1
                if XSS_PAYLOAD in (resp.text or ""):
                    f = Finding(
                        id=_gen_id(),
                        category="xss",
                        title=f"Reflected XSS indicator in parameter '{p}'",
                        description="Payload appeared unencoded in response",
                        url=url,
                        param=p,
                        confidence=Confidence.MEDIUM,
                        severity=Severity.MEDIUM,
                        status=FindingStatus.SUSPECTED,
                        source_tool="inline_probe",
                        evidence=[
                            Evidence(
                                request=HttpExcerpt(meta={"method": "GET", "url": test_url}),
                                response=HttpExcerpt(meta={"status": resp.status_code}, body_snippet=resp.text[:500]),
                                payload=XSS_PAYLOAD,
                            )
                        ],
                    )
                    return f, reqs
            except Exception:
                continue
        return None, reqs

    async def _probe_sqli(self, client: httpx.AsyncClient, url: str) -> Tuple[Optional[Finding], int]:
        reqs = 0
        parsed = urlparse(url)
        qparams = dict(parse_qsl(parsed.query, keep_blank_values=True))
        param_keys = list(qparams.keys()) or COMMON_PARAMS

        for p in param_keys[:5]:
            for payload in SQLI_PAYLOADS:
                test_url = _set_query_param(url, p, payload)
                try:
                    resp = await client.get(test_url)
                    reqs += 1
                    text = resp.text or ""
                    if self._looks_like_sql_error(text):
                        f = Finding(
                            id=_gen_id(),
                            category="sqli",
                            title=f"SQL error pattern for parameter '{p}'",
                            description="Response contained SQL error-like patterns",
                            url=url,
                            param=p,
                            confidence=Confidence.MEDIUM,
                            severity=Severity.HIGH,
                            status=FindingStatus.SUSPECTED,
                            source_tool="inline_probe",
                            evidence=[
                                Evidence(
                                    request=HttpExcerpt(meta={"method": "GET", "url": test_url}),
                                    response=HttpExcerpt(meta={"status": resp.status_code}, body_snippet=text[:500]),
                                    payload=payload,
                                )
                            ],
                        )
                        return f, reqs
                except Exception:
                    continue
        return None, reqs

    def _looks_like_sql_error(self, body: str) -> bool:
        lower = body.lower()
        for pat in SQL_ERROR_PATTERNS:
            if re.search(pat, lower):
                return True
        return False

    def _parse_sqlmap_output(self, url: str, stdout: str) -> Optional[Finding]:
        text = stdout.lower()
        if "is vulnerable" in text or "parameter" in text and "appears to be injectable" in text:
            return Finding(
                id=_gen_id(),
                category="sqli",
                title="sqlmap detection indicates SQL injection",
                description="sqlmap reported injectable parameter(s)",
                url=url,
                confidence=Confidence.HIGH,
                severity=Severity.HIGH,
                status=FindingStatus.SUSPECTED,
                source_tool="sqlmap",
                evidence=[Evidence(notes=stdout[:1000])],
            )
        return None


__all__ = ["ScanAgent"]

