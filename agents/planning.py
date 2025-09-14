
from __future__ import annotations

import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from uuid import uuid4

from pentest_schemas import (
    PentestTask,
    AgentResult,
    Finding,
    Evidence,
    Confidence,
    Severity,
    FindingStatus,
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


def _gen_id() -> str:
    return uuid4().hex


class ReverseAgent(BasePentestAgent):
    """Strategic Planning and Context Analysis Agent.
    
    Acts as a project-specific "control panel" similar to CLAUDE.md, providing:
    - Context-aware analysis of current pentest state
    - Strategic planning for next steps
    - Project structure understanding 
    - Workflow coordination and recommendations
    - Documentation of discovered patterns and conventions
    
    This agent serves as the "brain" that understands the bigger picture
    and guides the overall testing strategy based on accumulated findings.
    """

    def __init__(self, tools: Optional[List] = None):
        super().__init__(name="reverse", tools=tools)
        self.project_context: Dict[str, Any] = {}
        self.discovered_patterns: Set[str] = set()
        self.workflow_history: List[Dict[str, Any]] = []

    async def _execute(self, task: PentestTask, result: AgentResult, ctx: AgentContext) -> None:
        """Execute strategic planning and context analysis."""
        
        # Analyze current project state
        current_findings = task.hints.get("accumulated_findings", [])
        previous_tasks = task.hints.get("completed_tasks", [])
        available_context = task.hints.get("context", {})
        
        self.log(result, f"Analyzing project state with {len(current_findings)} findings and {len(previous_tasks)} completed tasks")
        
        # Build comprehensive project context
        project_analysis = await self._analyze_project_context(
            current_findings, previous_tasks, available_context, task.target
        )
        
        # Generate strategic recommendations
        strategy_plan = await self._create_strategic_plan(project_analysis, task)
        
        # Document discovered patterns
        patterns = await self._identify_patterns(current_findings, previous_tasks)
        
        # Create workflow recommendations
        next_steps = await self._recommend_next_steps(project_analysis, strategy_plan)
        
        # Generate findings about project structure and recommendations
        planning_finding = Finding(
            id=_gen_id(),
            category="strategic_planning",
            title="Project Analysis and Strategic Planning",
            description="Comprehensive analysis of current pentest state with strategic recommendations",
            confidence=Confidence.HIGH,
            severity=Severity.INFO,
            status=FindingStatus.CONFIRMED,
            source_tool="reverse_agent",
            evidence=[
                Evidence(notes=f"Project Analysis:\n{json.dumps(project_analysis, indent=2)}"),
                Evidence(notes=f"Strategic Plan:\n{json.dumps(strategy_plan, indent=2)}"),
                Evidence(notes=f"Next Steps:\n{json.dumps(next_steps, indent=2)}")
            ]
        )
        
        result.findings.append(planning_finding)
        
        # If we identify specific next actions, create derived tasks
        for next_step in next_steps.get("immediate_actions", []):
            if next_step.get("create_task", False):
                derived_task = PentestTask(
                    id=_gen_id(),
                    type=TaskType(next_step["task_type"]),
                    target=task.target,
                    urls=next_step.get("urls", []),
                    params=next_step.get("params", {}),
                    hints={
                        "from": "reverse_planning",
                        "context": project_analysis,
                        "priority_reason": next_step.get("reasoning")
                    },
                    priority=next_step.get("priority", 0.5),
                    notes=f"Strategic task: {next_step.get('description')}"
                )
                result.derived_tasks.append(derived_task)
        
        self.log(result, f"Generated strategic plan with {len(next_steps.get('immediate_actions', []))} immediate actions")

    async def _analyze_project_context(
        self, 
        findings: List[Dict], 
        tasks: List[Dict], 
        context: Dict[str, Any], 
        target
    ) -> Dict[str, Any]:
        """Analyze the overall project context like CLAUDE.md would understand a codebase."""
        
        analysis = {
            "target_profile": {
                "base_url": target.base_url,
                "allowed_hosts": target.allowed_hosts,
                "discovered_technologies": [],
                "security_posture": "unknown"
            },
            "testing_progress": {
                "phases_completed": [],
                "current_phase": "unknown",
                "coverage_areas": [],
                "gaps_identified": []
            },
            "attack_surface": {
                "discovered_endpoints": [],
                "potential_entry_points": [],
                "high_value_targets": []
            },
            "constraints_and_context": {
                "time_limits": context.get("time_limits"),
                "scope_restrictions": context.get("scope", "full"),
                "stealth_requirements": context.get("stealth_mode", True),
                "compliance_considerations": []
            }
        }
        
        # Analyze findings to understand what we've discovered
        for finding in findings:
            if isinstance(finding, dict):
                category = finding.get("category", "unknown")
                
                if category in ["tech_detection", "fingerprint"]:
                    tech_info = finding.get("description", "")
                    analysis["target_profile"]["discovered_technologies"].append(tech_info)
                
                elif category in ["sqli", "xss", "xxe"]:
                    analysis["attack_surface"]["potential_entry_points"].append({
                        "type": category,
                        "url": finding.get("url"),
                        "severity": finding.get("severity", "unknown")
                    })
        
        # Analyze completed tasks to understand testing progress
        task_types_seen = set()
        for task in tasks:
            if isinstance(task, dict):
                task_type = task.get("type")
                if task_type:
                    task_types_seen.add(task_type)
        
        # Map task types to phases
        if "recon" in task_types_seen:
            analysis["testing_progress"]["phases_completed"].append("reconnaissance")
        if "scan" in task_types_seen:
            analysis["testing_progress"]["phases_completed"].append("vulnerability_scanning")
        if "exploit" in task_types_seen:
            analysis["testing_progress"]["phases_completed"].append("exploitation_attempts")
        
        # Determine current phase based on what's been done
        if not analysis["testing_progress"]["phases_completed"]:
            analysis["testing_progress"]["current_phase"] = "initial_reconnaissance"
        elif "exploitation_attempts" in analysis["testing_progress"]["phases_completed"]:
            analysis["testing_progress"]["current_phase"] = "post_exploitation"
        elif "vulnerability_scanning" in analysis["testing_progress"]["phases_completed"]:
            analysis["testing_progress"]["current_phase"] = "exploitation"
        else:
            analysis["testing_progress"]["current_phase"] = "vulnerability_assessment"
        
        return analysis

    async def _create_strategic_plan(self, analysis: Dict[str, Any], task: PentestTask) -> Dict[str, Any]:
        """Create a strategic plan based on current analysis."""
        
        current_phase = analysis["testing_progress"]["current_phase"]
        completed_phases = analysis["testing_progress"]["phases_completed"]
        
        plan = {
            "overall_strategy": "",
            "priority_areas": [],
            "resource_allocation": {},
            "risk_considerations": [],
            "success_criteria": []
        }
        
        # Determine strategy based on current phase
        if current_phase == "initial_reconnaissance":
            plan["overall_strategy"] = "Comprehensive discovery and mapping of attack surface"
            plan["priority_areas"] = [
                "Technology stack identification",
                "Endpoint discovery and mapping",
                "Service enumeration",
                "Initial vulnerability scanning"
            ]
            plan["resource_allocation"] = {
                "recon": 0.4,
                "scan": 0.3,
                "analysis": 0.3
            }
        
        elif current_phase == "vulnerability_assessment":
            plan["overall_strategy"] = "Deep vulnerability analysis and exploitation planning"
            plan["priority_areas"] = [
                "Detailed vulnerability scanning",
                "Exploitation feasibility analysis", 
                "Attack path identification",
                "Risk prioritization"
            ]
            plan["resource_allocation"] = {
                "scan": 0.3,
                "exploit": 0.4,
                "analysis": 0.3
            }
        
        elif current_phase == "exploitation":
            plan["overall_strategy"] = "Controlled exploitation and access verification"
            plan["priority_areas"] = [
                "Proof-of-concept exploitation",
                "Access validation",
                "Privilege escalation opportunities",
                "Impact assessment"
            ]
            plan["resource_allocation"] = {
                "exploit": 0.5,
                "analysis": 0.3,
                "documentation": 0.2
            }
        
        elif current_phase == "post_exploitation":
            plan["overall_strategy"] = "Comprehensive impact analysis and documentation"
            plan["priority_areas"] = [
                "Impact analysis",
                "Data access verification",
                "Lateral movement possibilities",
                "Final reporting"
            ]
            plan["resource_allocation"] = {
                "analysis": 0.6,
                "documentation": 0.4
            }
        
        # Add risk considerations based on context
        if analysis["constraints_and_context"]["stealth_requirements"]:
            plan["risk_considerations"].append("Maintain stealth - avoid detection systems")
        
        # Add success criteria
        plan["success_criteria"] = [
            "Complete attack surface mapping",
            "Identify all critical vulnerabilities",
            "Demonstrate exploitability where possible",
            "Provide actionable remediation guidance"
        ]
        
        return plan

    async def _identify_patterns(self, findings: List[Dict], tasks: List[Dict]) -> Dict[str, Any]:
        """Identify patterns in the testing approach and results."""
        
        patterns = {
            "common_vulnerabilities": {},
            "effective_techniques": [],
            "recurring_issues": [],
            "technology_patterns": []
        }
        
        # Analyze vulnerability patterns
        vuln_counts = {}
        for finding in findings:
            if isinstance(finding, dict):
                category = finding.get("category")
                if category:
                    vuln_counts[category] = vuln_counts.get(category, 0) + 1
        
        patterns["common_vulnerabilities"] = vuln_counts
        
        # Identify effective techniques based on successful tasks
        for task in tasks:
            if isinstance(task, dict) and task.get("success", False):
                technique = task.get("type")
                if technique and technique not in patterns["effective_techniques"]:
                    patterns["effective_techniques"].append(technique)
        
        return patterns

    async def _recommend_next_steps(self, analysis: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific next step recommendations."""
        
        recommendations = {
            "immediate_actions": [],
            "medium_term_goals": [],
            "documentation_needs": [],
            "follow_up_required": []
        }
        
        current_phase = analysis["testing_progress"]["current_phase"]
        
        if current_phase == "initial_reconnaissance":
            recommendations["immediate_actions"].extend([
                {
                    "action": "deep_recon",
                    "description": "Perform comprehensive reconnaissance",
                    "task_type": "recon",
                    "priority": 0.9,
                    "create_task": True,
                    "params": {"crawl_depth": 3, "max_urls": 500},
                    "reasoning": "Need complete attack surface mapping"
                },
                {
                    "action": "technology_fingerprinting",
                    "description": "Identify technology stack and versions",
                    "priority": 0.8,
                    "create_task": False,
                    "reasoning": "Understanding tech stack guides vulnerability focus"
                }
            ])
        
        elif current_phase == "vulnerability_assessment":
            potential_vulns = analysis["attack_surface"]["potential_entry_points"]
            if potential_vulns:
                for vuln in potential_vulns[:3]:  # Top 3 potential vulnerabilities
                    recommendations["immediate_actions"].append({
                        "action": "exploit_attempt",
                        "description": f"Attempt exploitation of {vuln['type']} at {vuln.get('url', 'unknown')}",
                        "task_type": "exploit",
                        "priority": 0.8 if vuln.get("severity") in ["high", "critical"] else 0.6,
                        "create_task": True,
                        "urls": [vuln.get("url")] if vuln.get("url") else [],
                        "reasoning": f"High-value target: {vuln['type']} vulnerability"
                    })
        
        elif current_phase in ["exploitation", "post_exploitation"]:
            recommendations["immediate_actions"].append({
                "action": "comprehensive_analysis",
                "description": "Analyze all findings and create final report",
                "task_type": "analyze",
                "priority": 0.9,
                "create_task": True,
                "reasoning": "Time to synthesize findings into actionable insights"
            })
        
        # Always recommend documentation
        recommendations["documentation_needs"].append("Update project context with new findings")
        recommendations["documentation_needs"].append("Document attack paths and potential impact")
        
        return recommendations

    def _build_graph(self) -> Optional[CompiledStateGraph]:
        """Build LangGraph workflow for strategic planning."""
        if StateGraph is None:
            return None

        g = StateGraph(dict)

        async def analyze_context(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            current_findings = task.hints.get("accumulated_findings", [])
            previous_tasks = task.hints.get("completed_tasks", [])
            available_context = task.hints.get("context", {})
            
            project_analysis = await self._analyze_project_context(
                current_findings, previous_tasks, available_context, task.target
            )
            state["project_analysis"] = project_analysis
            return state

        async def create_strategy(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            project_analysis = state["project_analysis"]
            strategy_plan = await self._create_strategic_plan(project_analysis, task)
            state["strategy_plan"] = strategy_plan
            return state

        async def identify_patterns(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            current_findings = task.hints.get("accumulated_findings", [])
            previous_tasks = task.hints.get("completed_tasks", [])
            patterns = await self._identify_patterns(current_findings, previous_tasks)
            state["patterns"] = patterns
            return state

        async def recommend_actions(state: Dict[str, Any]) -> Dict[str, Any]:
            project_analysis = state["project_analysis"]
            strategy_plan = state["strategy_plan"]
            next_steps = await self._recommend_next_steps(project_analysis, strategy_plan)
            state["next_steps"] = next_steps
            return state

        async def generate_outputs(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            result: AgentResult = state["result"]
            
            project_analysis = state["project_analysis"]
            strategy_plan = state["strategy_plan"]
            next_steps = state["next_steps"]
            
            # Generate findings
            planning_finding = Finding(
                id=_gen_id(),
                category="strategic_planning",
                title="Project Analysis and Strategic Planning",
                description="Comprehensive analysis of current pentest state with strategic recommendations",
                confidence=Confidence.HIGH,
                severity=Severity.INFO,
                status=FindingStatus.CONFIRMED,
                source_tool="reverse_agent",
                evidence=[
                    Evidence(notes=f"Project Analysis:\n{json.dumps(project_analysis, indent=2)}"),
                    Evidence(notes=f"Strategic Plan:\n{json.dumps(strategy_plan, indent=2)}"),
                    Evidence(notes=f"Next Steps:\n{json.dumps(next_steps, indent=2)}")
                ]
            )
            
            result.findings.append(planning_finding)
            
            # Generate derived tasks
            for next_step in next_steps.get("immediate_actions", []):
                if next_step.get("create_task", False):
                    derived_task = PentestTask(
                        id=_gen_id(),
                        type=TaskType(next_step["task_type"]),
                        target=task.target,
                        urls=next_step.get("urls", []),
                        params=next_step.get("params", {}),
                        hints={
                            "from": "reverse_planning",
                            "context": project_analysis,
                            "priority_reason": next_step.get("reasoning")
                        },
                        priority=next_step.get("priority", 0.5),
                        notes=f"Strategic task: {next_step.get('description')}"
                    )
                    result.derived_tasks.append(derived_task)
            
            self.log(result, f"Generated strategic plan with {len(next_steps.get('immediate_actions', []))} immediate actions")
            return state

        g.add_node("analyze_context", analyze_context)
        g.add_node("create_strategy", create_strategy) 
        g.add_node("identify_patterns", identify_patterns)
        g.add_node("recommend_actions", recommend_actions)
        g.add_node("generate_outputs", generate_outputs)
        
        g.set_entry_point("analyze_context")
        g.add_edge("analyze_context", "create_strategy")
        g.add_edge("create_strategy", "identify_patterns")
        g.add_edge("identify_patterns", "recommend_actions")
        g.add_edge("recommend_actions", "generate_outputs")
        g.add_edge("generate_outputs", END)
        
        return g.compile()


__all__ = ["ReverseAgent"]
