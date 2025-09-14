#!/usr/bin/env python3
"""
enhanced_cua_agent_full.py

Single-file agent harness that:
- Supports modes: dummy | playwright | cua
- Playwright-backed payload testing for quick E2E
- Nuanced CLI integration (nuanced enrich) via subprocess (optional)
- Structured JSON reporting (stdout + file)
- CLI flags: --mode, --run-demo, --target, --use-nuanced, --report-file
- Safety: warns and defaults to safe demo targets only

Date: 2025-09-13
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("enhanced_cua_agent")

# ---------- Constants ----------
SAFE_DEMO_TARGETS = {
    "httpbin_form": "https://httpbin.org/forms/post",
    # If you run Juice Shop locally, use: http://localhost:3000
    # The demo will not target random production websites.
}

DEFAULT_REPORT_FILE = "cua_agent_report.jsonl"

# ---------- Data classes ----------
@dataclass
class PayloadResult:
    payload: str
    found_in_dom: bool
    screenshot: Optional[str]
    timestamp: str
    notes: Optional[str] = None

@dataclass
class TaskReport:
    task_id: str
    target_url: str
    payloads_tested: int
    successful_payloads: int
    results: List[PayloadResult]
    nuanced_context: Optional[Dict[str, Any]] = None
    mode: str = "dummy"
    run_time_seconds: float = 0.0

# ---------- Helpers: Nuanced integration (CLI approach) ----------
def nuanced_enrich(file_path: str, function_name: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Call Nuanced CLI: `nuanced enrich <file> <function>` and parse JSON from stdout.
    Returns parsed JSON or None on failure.
    NOTE: For production, consider using an MCP client/server—not CLI calls.
    """
    cmd = ["nuanced", "enrich", file_path, function_name]
    try:
        logger.info("Attempting Nuanced enrich via CLI: %s", " ".join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            logger.warning("Nuanced CLI exited non-zero: %s", proc.stderr.strip())
            return None
        out = proc.stdout.strip()
        # Nuanced might print JSON or human text; try JSON parse
        try:
            parsed = json.loads(out)
            logger.info("Nuanced enrich: parsed JSON successfully.")
            return parsed
        except Exception as e:
            logger.warning("Nuanced output not JSON-parsable: %s", e)
            return {"raw": out}
    except FileNotFoundError:
        logger.warning("Nuanced CLI not found. Install with npm if you need Nuanced integration.")
        return None
    except Exception as e:
        logger.exception("Nuanced enrich failed: %s", e)
        return None

# ---------- Agents ----------
class BaseAgent:
    def __init__(self, mode: str = "dummy"):
        self.mode = mode

    def test_payloads(self, target_url: str, payloads: List[str], selectors: Dict[str, str]) -> TaskReport:
        """
        Runs payloads against a target URL. Must be implemented by concrete classes.
        selectors: dict with keys like 'input', 'submit' (CSS selectors)
        """
        raise NotImplementedError()

class DummyAgent(BaseAgent):
    def __init__(self):
        super().__init__(mode="dummy")

    def test_payloads(self, target_url: str, payloads: List[str], selectors: Dict[str, str]) -> TaskReport:
        logger.info("Running DummyAgent: simulating payload tests.")
        start = time.time()
        results = []
        successes = 0
        for i, p in enumerate(payloads):
            # deterministic pseudo "success" for demonstration: every 3rd payload "found"
            found = ((i + 1) % 3 == 0)
            screenshot = None
            if found:
                screenshot = f"dummy_screenshot_{i+1}.png"
            results.append(
                PayloadResult(
                    payload=p,
                    found_in_dom=found,
                    screenshot=screenshot,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    notes="simulated" if not found else "simulated found"
                )
            )
            if found:
                successes += 1
        run_time = time.time() - start
        return TaskReport(
            task_id=f"dummy-{int(time.time())}",
            target_url=target_url,
            payloads_tested=len(payloads),
            successful_payloads=successes,
            results=results,
            mode="dummy",
            run_time_seconds=run_time,
        )

# Playwright agent: fast real automation to test DOM/inputs
class PlaywrightAgent(BaseAgent):
    def __init__(self, headless: bool = True):
        super().__init__(mode="playwright")
        self.headless = headless
        # We'll import playwright lazily so user doesn't need it unless mode is used
        self._pw = None

    def _ensure_playwright(self):
        if self._pw is None:
            try:
                from playwright.sync_api import sync_playwright
            except Exception as e:
                logger.exception("Playwright import failed. Did you run `pip install playwright` and `python -m playwright install`?")
                raise
            self._pw = sync_playwright()

    def test_payloads(self, target_url: str, payloads: List[str], selectors: Dict[str, str]) -> TaskReport:
        logger.info("Running PlaywrightAgent against %s", target_url)
        self._ensure_playwright()
        start = time.time()
        results: List[PayloadResult] = []
        successes = 0
        with self._pw as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            # navigate
            logger.info("Navigating to target: %s", target_url)
            page.goto(target_url, wait_until="networkidle")
            for i, payload in enumerate(payloads):
                try:
                    # attempt to fill input
                    if "input" in selectors:
                        logger.debug("Filling %s with payload", selectors["input"])
                        page.fill(selectors["input"], payload)
                    # submit if submit selector provided
                    if "submit" in selectors and selectors["submit"]:
                        try:
                            page.click(selectors["submit"])
                        except Exception:
                            # try pressing Enter
                            page.keyboard.press("Enter")
                    # wait briefly for DOM update
                    page.wait_for_timeout(600)  # ms
                    body = page.content()
                    found = payload in body
                    screenshot_path = None
                    if found:
                        screenshot_path = f"playwright_screenshot_{int(time.time())}_{i+1}.png"
                        page.screenshot(path=screenshot_path, full_page=True)
                    results.append(
                        PayloadResult(
                            payload=payload,
                            found_in_dom=found,
                            screenshot=screenshot_path,
                            timestamp=datetime.utcnow().isoformat() + "Z",
                            notes=None
                        )
                    )
                    if found:
                        successes += 1
                except Exception as e:
                    logger.exception("Payload test failed for payload #%s: %s", i + 1, e)
                    results.append(
                        PayloadResult(
                            payload=payload,
                            found_in_dom=False,
                            screenshot=None,
                            timestamp=datetime.utcnow().isoformat() + "Z",
                            notes=str(e)
                        )
                    )
            browser.close()
        run_time = time.time() - start
        return TaskReport(
            task_id=f"playwright-{int(time.time())}",
            target_url=target_url,
            payloads_tested=len(payloads),
            successful_payloads=successes,
            results=results,
            mode="playwright",
            run_time_seconds=run_time,
        )

# CuaAgent stub: implement using real Cua SDK later
class CuaAgent(BaseAgent):
    def __init__(self):
        super().__init__(mode="cua")
        # Attempt to import the real Cua SDK here; for now we have a placeholder.
        self.available = False
        try:
            # Example: from cua_sdk import Computer (this is illustrative)
            # from cua import CuaClient
            # self.client = CuaClient()
            # self.available = True
            pass
        except Exception:
            self.available = False

    def test_payloads(self, target_url: str, payloads: List[str], selectors: Dict[str, str]) -> TaskReport:
        if not self.available:
            logger.error("Cua SDK not available in this environment. Replace this stub with the real Cua client code.")
            raise RuntimeError("Cua SDK not available")
        # Replace with real Cua control flow using the SDK:
        # - create container/computer
        # - open browser
        # - type payloads using computer.type/click
        # - capture screenshots and DOM via browser devtools or accessibility APIs
        raise NotImplementedError("CuaAgent should be implemented with real Cua SDK calls")

# ---------- Orchestrator ----------
class SimpleOrchestrator:
    def __init__(self, agent: BaseAgent, use_nuanced: bool = False, nuanced_targets: Optional[List[Tuple[str, str]]] = None):
        self.agent = agent
        self.use_nuanced = use_nuanced
        # nuanced_targets: list of tuples (file_path, function_name) to enrich
        self.nuanced_targets = nuanced_targets or []

    def run_task(self, target_url: str, payloads: List[str], selectors: Dict[str, str]) -> TaskReport:
        logger.info("Orchestrator: starting task for %s", target_url)
        nuanced_context = None
        if self.use_nuanced and self.nuanced_targets:
            # for simplicity, enrich the first target if available
            file_path, func = self.nuanced_targets[0]
            nuanced_context = nuanced_enrich(file_path, func)
            if nuanced_context:
                logger.info("Attached Nuanced context (truncated): %s", str(list(nuanced_context.keys())[:5]))
        # run agent test
        report = self.agent.test_payloads(target_url, payloads, selectors)
        report.nuanced_context = nuanced_context
        return report

# ---------- Utilities ----------
def default_payloads() -> List[str]:
    # A short, safe list of test payloads. DO NOT use for malicious scanning.
    return [
        "<test_payload_1>",
        "<test_payload_2>",
        "<script>alert('x')</script>",
        "' OR '1'='1",
        "<img src=x onerror=alert(1)>"
    ]

def safe_demo_target(name: str) -> str:
    if name in SAFE_DEMO_TARGETS:
        return SAFE_DEMO_TARGETS[name]
    else:
        raise ValueError("Unsafe demo target selected. Allowed targets: " + ", ".join(SAFE_DEMO_TARGETS.keys()))

def write_report(report: TaskReport, filename: str = DEFAULT_REPORT_FILE):
    # Append JSON lines for each run (good for later metrics pipeline)
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "a", encoding="utf-8") as f:
        json_line = json.dumps(asdict(report), default=str)
        f.write(json_line + "\n")
    logger.info("Wrote report to %s", filename)

# ---------- CLI and main ----------
def build_agent(mode: str, headless: bool = True) -> BaseAgent:
    if mode == "dummy":
        return DummyAgent()
    elif mode == "playwright":
        return PlaywrightAgent(headless=headless)
    elif mode == "cua":
        return CuaAgent()
    else:
        raise ValueError(f"Unknown mode: {mode}")

def parse_args():
    p = argparse.ArgumentParser(description="Enhanced CUA Agent harness (dummy, playwright, cua) with Nuanced support.")
    p.add_argument("--mode", type=str, choices=["dummy", "playwright", "cua"], default="dummy", help="Which backend to use.")
    p.add_argument("--run-demo", action="store_true", help="Run the safe demo against httpbin form.")
    p.add_argument("--target", type=str, default=None, help="Target URL (don't point to other people's sites).")
    p.add_argument("--use-nuanced", action="store_true", help="Attempt to call Nuanced CLI to enrich context for the task.")
    p.add_argument("--nuanced-file", type=str, default=None, help="File to pass to nuanced enrich (for --use-nuanced).")
    p.add_argument("--nuanced-func", type=str, default=None, help="Function name to pass to nuanced enrich (for --use-nuanced).")
    p.add_argument("--report-file", type=str, default=DEFAULT_REPORT_FILE, help="File to append JSONL reports to.")
    p.add_argument("--headless", action="store_true", help="Run browsers headless (Playwright mode).")
    p.add_argument("--no-headless", dest="headless", action="store_false", help="Run browsers visible (Playwright mode).")
    p.set_defaults(headless=True)
    return p.parse_args()

def main():
    args = parse_args()
    logger.info("Starting enhanced CUA agent harness (mode=%s)", args.mode)

    if args.run_demo:
        # do safe demo
        target = safe_demo_target("httpbin_form")
        logger.info("DEMO MODE: using safe demo target: %s", target)
    else:
        if not args.target:
            logger.error("No target provided. Use --run-demo for a safe demo or --target <url> if you have permission to test.")
            sys.exit(1)
        target = args.target
        # user responsibility warning
        logger.warning("You provided target %s. Only run tests against targets you have permission to test!", target)

    # prepare payloads and selectors (for demo using httpbin forms)
    payloads = default_payloads()
    # For httpbin form: input name is 'custname' etc - safer to use simple CSS input selector
    selectors = {"input": "input[name='custname']", "submit": "button[type='submit']"}
    # If httpbin selectors fail, the agent will still try to fill/maybe submit

    # Build agent
    agent = build_agent(args.mode, headless=args.headless)

    # Optional Nuanced targets configuration
    nuanced_targets = None
    if args.use_nuanced:
        if not args.nuanced_file or not args.nuanced_func:
            logger.warning("Nuanced requested but file/function not specified. Skipping nuanced enrich.")
        else:
            nuanced_targets = [(args.nuanced_file, args.nuanced_func)]

    orchestrator = SimpleOrchestrator(agent=agent, use_nuanced=args.use_nuanced, nuanced_targets=nuanced_targets)

    # Run task
    start_time = time.time()
    try:
        report = orchestrator.run_task(target, payloads, selectors)
    except NotImplementedError as e:
        logger.error("Agent functionality not implemented: %s", e)
        sys.exit(2)
    except Exception as e:
        logger.exception("Task run failed: %s", e)
        sys.exit(3)
    end_time = time.time()
    report.run_time_seconds = end_time - start_time

    # Output summary
    logger.info("Task complete. Target: %s | Mode: %s | payloads: %d | successes: %d | time: %.2fs",
                report.target_url, report.mode, report.payloads_tested, report.successful_payloads, report.run_time_seconds)

    # Print succinct JSON to stdout
    print(json.dumps(asdict(report), indent=2, default=str))

    # Append to report file
    write_report(report, filename=args.report_file)

if __name__ == "__main__":
    main()
