"""
Adapter layer to bridge ORC BaseAgent interface with existing BasePentestAgent implementations.
This allows the structured Pydantic-based agents to work with ORC's Dict-based expectations.
"""

from typing import Dict, Any, List, Optional, Type
from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from uuid import uuid4
import sys
import os

# Add parent directory to path to import from agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base import BasePentestAgent, AgentContext
from agents.pentest_schemas import (
    PentestTask,
    Target,
    TaskType,
    AgentResult,
    Finding,
    Severity,
    Confidence,
)
from ORC.agent_spawner import BaseAgent, AgentConfig


class ORCAgentAdapter(BaseAgent):
    """
    Adapter that wraps a BasePentestAgent to work with ORC's BaseAgent interface.
    Converts between Dict-based ORC format and Pydantic-based agent format.
    """
    
    def __init__(
        self, 
        pentest_agent: BasePentestAgent,
        config: AgentConfig,
        knowledge_graph_url: str
    ):
        super().__init__(config, knowledge_graph_url)
        self.pentest_agent = pentest_agent
        
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the wrapped agent by converting ORC format to PentestTask format.
        
        Args:
            task: ORC task dictionary with 'objective', 'constraints', etc.
            context: ORC context dictionary with target info and state
            
        Returns:
            Dict matching ORC's expected format with success, findings, context_updates
        """
        try:
            # Convert ORC task/context to PentestTask
            pentest_task = self._convert_to_pentest_task(task, context)
            
            # Run the actual agent
            agent_result = await self.pentest_agent.run(pentest_task)
            
            # Convert AgentResult back to ORC format
            return self._convert_to_orc_format(agent_result, context)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent execution failed: {str(e)}",
                "agent": self.config.name
            }
    
    def _convert_to_pentest_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> PentestTask:
        """Convert ORC task dictionary to PentestTask."""
        
        # Determine task type from agent name or objective
        task_type_map = {
            "recon": TaskType.RECON,
            "exploit": TaskType.EXPLOIT,
            "analysis": TaskType.ANALYZE,
            "scan": TaskType.SCAN,
        }
        
        # Try to infer task type from config name
        task_type = TaskType.RECON  # default
        for key, t_type in task_type_map.items():
            if key in self.config.name.lower():
                task_type = t_type
                break
        
        # Build Target from context
        target = Target(
            base_url=context.get("target", "http://localhost"),
            allowed_hosts=context.get("allowed_hosts", []),
            default_headers=context.get("headers", {}),
            auth_token=context.get("auth_token"),
            cookies=context.get("cookies", {})
        )
        
        # Extract URLs if present
        urls = []
        if "urls" in context:
            urls = context["urls"] if isinstance(context["urls"], list) else [context["urls"]]
        elif "target" in context and context["target"].startswith("http"):
            urls = [context["target"]]
        
        # Build params from task constraints and context
        params = {}
        if "constraints" in task:
            params.update(task["constraints"])
        if "timeout" in context:
            params["timeout"] = context["timeout"]
        if "stealth_mode" in context:
            params["stealth"] = context["stealth_mode"]
            
        # Build hints from task objective and context
        hints = {
            "objective": task.get("objective", ""),
            "from_orc": True,
            "phase": context.get("_phase", "unknown"),
        }
        
        # Add any findings from context for analysis agent
        if "findings" in context:
            hints["findings"] = self._convert_findings_to_agent_format(context["findings"])
        
        return PentestTask(
            id=str(uuid4()),
            type=task_type,
            target=target,
            urls=urls,
            params=params,
            hints=hints,
            priority=task.get("priority", 0.5),
            notes=task.get("objective", "")
        )
    
    def _convert_to_orc_format(self, result: AgentResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Convert AgentResult to ORC's expected dictionary format."""
        
        # Determine success based on findings or logs
        success = len(result.findings) > 0 or any("success" in log.lower() for log in result.logs)
        
        # Convert structured findings to ORC format
        findings = []
        for finding in result.findings:
            findings.append({
                "id": finding.id,
                "type": finding.category,
                "severity": finding.severity.value,
                "confidence": finding.confidence.value,
                "title": finding.title,
                "description": finding.description,
                "url": finding.url,
                "evidence": [{"notes": e.notes} for e in finding.evidence[:2]]  # Limit evidence
            })
        
        # Build context updates from results
        context_updates = {}
        
        # Update based on agent type
        if "recon" in self.config.name.lower():
            if findings:
                context_updates["recon_completed"] = True
                context_updates["attack_surface"] = {
                    "urls": [f["url"] for f in findings if f.get("url")],
                    "findings_count": len(findings)
                }
        elif "exploit" in self.config.name.lower():
            if any(f["severity"] in ["high", "critical"] for f in findings):
                context_updates["access_gained"] = True
                context_updates["vulnerabilities_confirmed"] = True
        elif "analysis" in self.config.name.lower():
            context_updates["analysis_complete"] = True
            if findings:
                # Calculate risk level from findings
                critical_count = sum(1 for f in findings if f["severity"] == "critical")
                high_count = sum(1 for f in findings if f["severity"] == "high")
                if critical_count > 0:
                    context_updates["risk_level"] = "critical"
                elif high_count > 2:
                    context_updates["risk_level"] = "high"
                else:
                    context_updates["risk_level"] = "medium"
        
        # Add derived tasks as recommendations
        recommendations = []
        for task in result.derived_tasks[:3]:  # Limit recommendations
            recommendations.append(f"Execute {task.type.value} on {task.urls[0] if task.urls else 'target'}")
        
        return {
            "success": success,
            "agent": self.config.name,
            "findings": findings if findings else result.logs[:5],  # Fall back to logs if no findings
            "context_updates": context_updates,
            "recommendations": recommendations,
            "metrics": {
                "duration_ms": result.metrics.duration_ms,
                "requests_made": result.metrics.requests_made,
                "tool_invocations": dict(result.metrics.tool_invocations)
            }
        }
    
    def _convert_findings_to_agent_format(self, orc_findings: Any) -> List[Finding]:
        """Convert ORC findings format to agent Finding objects."""
        findings = []
        
        if isinstance(orc_findings, list):
            for f in orc_findings:
                if isinstance(f, dict):
                    # Convert dict to Finding
                    findings.append(Finding(
                        id=f.get("id", str(uuid4())),
                        category=f.get("type", f.get("category", "unknown")),
                        title=f.get("title", "Finding"),
                        description=f.get("description", ""),
                        url=f.get("url"),
                        severity=Severity(f.get("severity", "info")),
                        confidence=Confidence(f.get("confidence", "low"))
                    ))
                elif isinstance(f, str):
                    # Simple string finding
                    findings.append(Finding(
                        id=str(uuid4()),
                        category="info",
                        title=f,
                        description=f,
                        severity=Severity.INFO,
                        confidence=Confidence.LOW
                    ))
        
        return findings


class AgentRegistrar:
    """
    Helper class to register existing agents with ORC's AgentSpawner.
    """
    
    @staticmethod
    def register_pentest_agents(spawner, knowledge_graph_url: str):
        """
        Register all existing pentest agents with the ORC spawner.
        
        Args:
            spawner: ORC AgentSpawner instance
            knowledge_graph_url: URL for knowledge graph
        """
        
        # Import agent implementations
        from agents.recon import ReconAgent
        from agents.exploit import ExploitAgent
        from agents.analysis import AnalysisAgent
        
        # Import tool adapters
        from tools.adapters.nmap import NmapAdapter
        from tools.adapters.ffuf import FfufAdapter
        from tools.adapters.sqlmap import SqlmapAdapter
        
        # Create tool instances
        tools = {
            "nmap": NmapAdapter(),
            "ffuf": FfufAdapter(),
            "sqlmap": SqlmapAdapter(),
        }
        
        # Register ReconAgent
        recon_config = AgentConfig(
            name="recon_agent",
            capabilities=["port_scanning", "service_enumeration", "subdomain_discovery"],
            max_concurrency=3,
            timeout=600
        )
        recon_agent = ReconAgent(tools=[tools.get("ffuf"), tools.get("nmap")])
        recon_adapter = ORCAgentAdapter(recon_agent, recon_config, knowledge_graph_url)
        spawner.agent_registry["recon"] = (type(recon_adapter), recon_config)
        spawner.active_agents["recon"] = recon_adapter
        
        # Register ExploitAgent  
        exploit_config = AgentConfig(
            name="exploit_agent",
            capabilities=["vulnerability_exploitation", "sqli_confirmation"],
            max_concurrency=1,
            timeout=300,
            required_context=["vulnerabilities", "urls"]
        )
        exploit_agent = ExploitAgent(tools=[tools.get("sqlmap")])
        exploit_adapter = ORCAgentAdapter(exploit_agent, exploit_config, knowledge_graph_url)
        spawner.agent_registry["exploit"] = (type(exploit_adapter), exploit_config)
        spawner.active_agents["exploit"] = exploit_adapter
        
        # Register AnalysisAgent
        analysis_config = AgentConfig(
            name="analysis_agent",
            capabilities=["risk_assessment", "report_generation", "finding_aggregation"],
            max_concurrency=2,
            timeout=300
        )
        analysis_agent = AnalysisAgent()
        analysis_adapter = ORCAgentAdapter(analysis_agent, analysis_config, knowledge_graph_url)
        spawner.agent_registry["analysis"] = (type(analysis_adapter), analysis_config)
        spawner.active_agents["analysis"] = analysis_adapter
        
        return spawner


def integrate_agents_with_orc():
    """
    Main integration function to set up ORC with existing agents.
    
    Returns:
        Configured ORCSystem ready to use with existing agents
    """
    from ORC.main import ORCSystem
    from ORC.agent_spawner import AgentSpawner
    
    # Create ORC system
    knowledge_graph_url = "http://localhost:8000/api/knowledge"
    orc = ORCSystem(knowledge_graph_url)
    
    # Replace spawner with one that has our agents registered
    orc.spawner = AgentSpawner(knowledge_graph_url)
    AgentRegistrar.register_pentest_agents(orc.spawner, knowledge_graph_url)
    
    return orc
