from typing import Dict, Any, Optional, List, Type
from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json


@dataclass
class AgentConfig:
    name: str
    capabilities: List[str]
    max_concurrency: int = 1
    timeout: int = 300
    retry_attempts: int = 3
    required_context: List[str] = None


class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, knowledge_graph_url: str):
        self.config = config
        self.knowledge_graph_url = knowledge_graph_url
        self.active_tasks = []

    @abstractmethod
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def validate_context(self, context: Dict[str, Any]) -> bool:
        if not self.config.required_context:
            return True
        return all(key in context for key in self.config.required_context)

    async def query_knowledge_graph(self, query: str) -> Dict[str, Any]:
        return {"response": f"Knowledge graph response for: {query}"}


class ReconAgent(BaseAgent):
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        target = context.get("target", "unknown")

        results = {
            "ports": await self._scan_ports(target),
            "services": await self._enumerate_services(target),
            "subdomains": await self._find_subdomains(target),
            "technologies": await self._detect_technologies(target)
        }

        return {
            "success": True,
            "agent": self.config.name,
            "findings": results,
            "context_updates": {
                "recon_completed": True,
                "attack_surface": results
            }
        }

    async def _scan_ports(self, target: str) -> List[int]:
        await asyncio.sleep(0.1)
        return [22, 80, 443, 3306, 8080]

    async def _enumerate_services(self, target: str) -> Dict[str, str]:
        await asyncio.sleep(0.1)
        return {
            "22": "SSH",
            "80": "HTTP",
            "443": "HTTPS",
            "3306": "MySQL",
            "8080": "HTTP-Alt"
        }

    async def _find_subdomains(self, target: str) -> List[str]:
        await asyncio.sleep(0.1)
        return [f"api.{target}", f"admin.{target}", f"dev.{target}"]

    async def _detect_technologies(self, target: str) -> Dict[str, str]:
        await asyncio.sleep(0.1)
        return {
            "webserver": "nginx/1.18.0",
            "framework": "Django",
            "database": "PostgreSQL"
        }


class ExploitAgent(BaseAgent):
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        vulnerabilities = context.get("vulnerabilities", [])

        exploitation_results = []
        for vuln in vulnerabilities[:3]:
            result = await self._attempt_exploit(vuln, context)
            exploitation_results.append(result)

        successful = [r for r in exploitation_results if r.get("success")]

        return {
            "success": len(successful) > 0,
            "agent": self.config.name,
            "findings": {
                "exploited": successful,
                "failed": [r for r in exploitation_results if not r.get("success")]
            },
            "context_updates": {
                "access_gained": len(successful) > 0,
                "access_level": self._determine_access_level(successful)
            }
        }

    async def _attempt_exploit(self, vulnerability: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return {
            "vulnerability": vulnerability,
            "success": True,
            "access_type": "shell",
            "privileges": "user"
        }

    def _determine_access_level(self, successful_exploits: List[Dict]) -> str:
        if any(e.get("privileges") == "root" for e in successful_exploits):
            return "root"
        elif any(e.get("privileges") == "admin" for e in successful_exploits):
            return "admin"
        return "user"


class AnalysisAgent(BaseAgent):
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        all_findings = context.get("findings", {})

        analysis = {
            "risk_score": await self._calculate_risk_score(all_findings),
            "attack_paths": await self._identify_attack_paths(all_findings),
            "recommendations": await self._generate_recommendations(all_findings),
            "iocs": await self._extract_iocs(all_findings)
        }

        return {
            "success": True,
            "agent": self.config.name,
            "findings": analysis,
            "context_updates": {
                "analysis_complete": True,
                "risk_level": self._categorize_risk(analysis["risk_score"])
            }
        }

    async def _calculate_risk_score(self, findings: Dict) -> float:
        await asyncio.sleep(0.1)
        return 7.5

    async def _identify_attack_paths(self, findings: Dict) -> List[Dict]:
        await asyncio.sleep(0.1)
        return [
            {"path": "External -> Web App -> Database", "likelihood": "high"},
            {"path": "Phishing -> Internal Network -> Domain Controller", "likelihood": "medium"}
        ]

    async def _generate_recommendations(self, findings: Dict) -> List[str]:
        await asyncio.sleep(0.1)
        return [
            "Patch identified vulnerabilities immediately",
            "Implement network segmentation",
            "Enable MFA on all administrative accounts",
            "Review and update firewall rules"
        ]

    async def _extract_iocs(self, findings: Dict) -> Dict[str, List]:
        await asyncio.sleep(0.1)
        return {
            "ips": ["192.168.1.100", "10.0.0.50"],
            "domains": ["malicious.example.com"],
            "hashes": ["d41d8cd98f00b204e9800998ecf8427e"]
        }

    def _categorize_risk(self, score: float) -> str:
        if score >= 8:
            return "critical"
        elif score >= 6:
            return "high"
        elif score >= 4:
            return "medium"
        return "low"


class AgentSpawner:
    def __init__(self, knowledge_graph_url: str, max_workers: int = 5):
        self.knowledge_graph_url = knowledge_graph_url
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.agent_registry: Dict[str, Type[BaseAgent]] = {}
        self.active_agents: Dict[str, BaseAgent] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        self.register_agent("recon", ReconAgent, AgentConfig(
            name="recon_agent",
            capabilities=["port_scanning", "service_enumeration", "subdomain_discovery"],
            max_concurrency=3,
            timeout=600
        ))

        self.register_agent("exploit", ExploitAgent, AgentConfig(
            name="exploit_agent",
            capabilities=["vulnerability_exploitation", "privilege_escalation"],
            max_concurrency=1,
            timeout=300,
            required_context=["vulnerabilities"]
        ))

        self.register_agent("analysis", AnalysisAgent, AgentConfig(
            name="analysis_agent",
            capabilities=["risk_assessment", "report_generation", "ioc_extraction"],
            max_concurrency=2,
            timeout=300
        ))

    def register_agent(self, agent_type: str, agent_class: Type[BaseAgent], config: AgentConfig):
        self.agent_registry[agent_type] = (agent_class, config)

    async def spawn_agent(self, agent_type: str, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if agent_type not in self.agent_registry:
            return {
                "success": False,
                "error": f"Unknown agent type: {agent_type}"
            }

        agent_class, config = self.agent_registry[agent_type]

        if agent_type not in self.active_agents:
            self.active_agents[agent_type] = agent_class(config, self.knowledge_graph_url)

        agent = self.active_agents[agent_type]

        if not await agent.validate_context(context):
            return {
                "success": False,
                "error": f"Missing required context for {agent_type}",
                "required": config.required_context
            }

        try:
            result = await asyncio.wait_for(
                agent.execute(task, context),
                timeout=config.timeout
            )
            return result
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Agent {agent_type} timed out after {config.timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent {agent_type} failed: {str(e)}"
            }

    async def spawn_multiple(self, agent_tasks: List[tuple[str, Dict, Dict]]) -> List[Dict[str, Any]]:
        tasks = []
        for agent_type, task, context in agent_tasks:
            tasks.append(self.spawn_agent(agent_type, task, context))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "agent": agent_tasks[i][0]
                })
            else:
                processed_results.append(result)

        return processed_results

    def cleanup(self):
        self.executor.shutdown(wait=True)
        self.active_agents.clear()