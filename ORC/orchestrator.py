from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass
from enum import Enum
import json
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class AgentType(Enum):
    RECON = "recon"
    EXPLOIT = "exploit"
    PERSISTENCE = "persistence"
    LATERAL = "lateral_movement"
    EXFIL = "exfiltration"
    ANALYSIS = "analysis"
    CLEANUP = "cleanup"


@dataclass
class AgentCapability:
    agent_type: AgentType
    specialization: str
    tools: List[str]
    confidence_threshold: float = 0.7


@dataclass
class OrchestratorState:
    messages: List[BaseMessage]
    current_context: Dict[str, Any]
    active_agents: List[AgentType]
    task_queue: List[Dict[str, Any]]
    results: Dict[str, Any]
    phase: str
    metadata: Dict[str, Any]


class Orchestrator:
    def __init__(self, knowledge_graph_url: str, api_key: Optional[str] = None):
        self.knowledge_graph_url = knowledge_graph_url
        self.api_key = api_key
        self.graph = self._build_graph()
        self.agent_registry = self._initialize_agents()

    def _initialize_agents(self) -> Dict[AgentType, AgentCapability]:
        return {
            AgentType.RECON: AgentCapability(
                agent_type=AgentType.RECON,
                specialization="Network and service discovery",
                tools=["nmap", "masscan", "shodan", "dns_enum", "subdomain_finder"]
            ),
            AgentType.EXPLOIT: AgentCapability(
                agent_type=AgentType.EXPLOIT,
                specialization="Vulnerability exploitation",
                tools=["metasploit", "sqlmap", "burp", "nuclei", "custom_exploits"]
            ),
            AgentType.PERSISTENCE: AgentCapability(
                agent_type=AgentType.PERSISTENCE,
                specialization="Maintaining access",
                tools=["backdoor_gen", "service_installer", "registry_mod", "cron_jobs"]
            ),
            AgentType.LATERAL: AgentCapability(
                agent_type=AgentType.LATERAL,
                specialization="Moving through network",
                tools=["mimikatz", "psexec", "wmi", "rdp", "ssh_pivot"]
            ),
            AgentType.EXFIL: AgentCapability(
                agent_type=AgentType.EXFIL,
                specialization="Data extraction",
                tools=["compress", "encrypt", "dns_tunnel", "https_post", "steganography"]
            ),
            AgentType.ANALYSIS: AgentCapability(
                agent_type=AgentType.ANALYSIS,
                specialization="Security analysis and reporting",
                tools=["log_parser", "pcap_analyzer", "malware_sandbox", "ioc_extractor"]
            ),
            AgentType.CLEANUP: AgentCapability(
                agent_type=AgentType.CLEANUP,
                specialization="Trace removal",
                tools=["log_cleaner", "timestamp_mod", "artifact_remover", "process_killer"]
            )
        }

    def _build_graph(self) -> CompiledStateGraph:
        workflow = StateGraph(OrchestratorState)

        workflow.add_node("context_analysis", self._analyze_context)
        workflow.add_node("agent_selection", self._select_agents)
        workflow.add_node("task_distribution", self._distribute_tasks)
        workflow.add_node("agent_execution", self._execute_agents)
        workflow.add_node("result_aggregation", self._aggregate_results)
        workflow.add_node("decision_point", self._make_decision)

        workflow.set_entry_point("context_analysis")

        workflow.add_edge("context_analysis", "agent_selection")
        workflow.add_edge("agent_selection", "task_distribution")
        workflow.add_edge("task_distribution", "agent_execution")
        workflow.add_edge("agent_execution", "result_aggregation")
        workflow.add_edge("result_aggregation", "decision_point")

        workflow.add_conditional_edges(
            "decision_point",
            self._should_continue,
            {
                "continue": "context_analysis",
                "end": END
            }
        )

        return workflow.compile()

    async def _analyze_context(self, state: OrchestratorState) -> OrchestratorState:
        """Analyze current context and determine operation phase"""
        context = state.current_context

        if not context.get("target_identified"):
            state.phase = "reconnaissance"
        elif not context.get("access_gained"):
            state.phase = "initial_access"
        elif not context.get("persistence_established"):
            state.phase = "persistence"
        elif context.get("objectives_remaining"):
            state.phase = "execution"
        else:
            state.phase = "cleanup"

        state.metadata["phase_analysis"] = {
            "current_phase": state.phase,
            "confidence": self._calculate_phase_confidence(state)
        }

        return state

    async def _select_agents(self, state: OrchestratorState) -> OrchestratorState:
        """Select appropriate agents based on phase and context"""
        phase_agents = {
            "reconnaissance": [AgentType.RECON, AgentType.ANALYSIS],
            "initial_access": [AgentType.EXPLOIT, AgentType.ANALYSIS],
            "persistence": [AgentType.PERSISTENCE, AgentType.LATERAL],
            "execution": [AgentType.LATERAL, AgentType.EXFIL],
            "cleanup": [AgentType.CLEANUP, AgentType.ANALYSIS]
        }

        state.active_agents = phase_agents.get(state.phase, [AgentType.ANALYSIS])

        for agent_type in state.active_agents:
            capability = self.agent_registry[agent_type]
            state.metadata[f"agent_{agent_type.value}"] = {
                "tools": capability.tools,
                "specialization": capability.specialization
            }

        return state

    async def _distribute_tasks(self, state: OrchestratorState) -> OrchestratorState:
        """Create and distribute tasks to selected agents"""
        tasks = []

        for agent_type in state.active_agents:
            task = {
                "agent": agent_type.value,
                "objective": self._generate_objective(agent_type, state),
                "constraints": self._get_constraints(state),
                "priority": self._calculate_priority(agent_type, state)
            }
            tasks.append(task)

        state.task_queue = sorted(tasks, key=lambda x: x["priority"], reverse=True)
        return state

    async def _execute_agents(self, state: OrchestratorState) -> OrchestratorState:
        """Coordinate agent execution"""
        results = {}

        for task in state.task_queue:
            agent_type = AgentType(task["agent"])

            agent_result = await self._spawn_agent(
                agent_type=agent_type,
                task=task,
                context=state.current_context
            )

            results[agent_type.value] = agent_result

            state.current_context.update(agent_result.get("context_updates", {}))

        state.results.update(results)
        return state

    async def _aggregate_results(self, state: OrchestratorState) -> OrchestratorState:
        """Aggregate and analyze results from all agents"""
        aggregated = {
            "success_count": 0,
            "failure_count": 0,
            "findings": [],
            "next_steps": []
        }

        for agent, result in state.results.items():
            if result.get("success"):
                aggregated["success_count"] += 1
                aggregated["findings"].extend(result.get("findings", []))
            else:
                aggregated["failure_count"] += 1

            aggregated["next_steps"].extend(result.get("recommendations", []))

        state.metadata["aggregation"] = aggregated
        return state

    async def _make_decision(self, state: OrchestratorState) -> OrchestratorState:
        """Decide next action based on results"""
        if state.metadata["aggregation"]["failure_count"] > len(state.active_agents) / 2:
            state.metadata["decision"] = "retry_with_different_approach"
        elif state.phase == "cleanup":
            state.metadata["decision"] = "complete"
        else:
            state.metadata["decision"] = "proceed_to_next_phase"

        return state

    def _should_continue(self, state: OrchestratorState) -> Literal["continue", "end"]:
        """Determine if orchestration should continue"""
        if state.metadata.get("decision") == "complete":
            return "end"
        if len(state.messages) > 100:  # Safety limit
            return "end"
        return "continue"

    async def _spawn_agent(
        self,
        agent_type: AgentType,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Spawn and execute a specific agent"""

        return {
            "success": True,
            "findings": [f"Mock finding from {agent_type.value}"],
            "context_updates": {
                f"{agent_type.value}_completed": True
            },
            "recommendations": [f"Next step from {agent_type.value}"]
        }

    def _generate_objective(self, agent_type: AgentType, state: OrchestratorState) -> str:
        """Generate specific objective for agent based on context"""
        objectives = {
            AgentType.RECON: "Identify attack surface and gather intelligence",
            AgentType.EXPLOIT: "Gain initial access through identified vulnerabilities",
            AgentType.PERSISTENCE: "Establish persistent access mechanisms",
            AgentType.LATERAL: "Move laterally to high-value targets",
            AgentType.EXFIL: "Extract identified sensitive data",
            AgentType.ANALYSIS: "Analyze findings and generate report",
            AgentType.CLEANUP: "Remove traces and maintain operational security"
        }
        return objectives.get(agent_type, "Perform assigned security task")

    def _get_constraints(self, state: OrchestratorState) -> Dict[str, Any]:
        """Get operational constraints from context"""
        return {
            "stealth_required": state.current_context.get("stealth_mode", True),
            "time_limit": state.current_context.get("time_limit", 3600),
            "avoid_detection": state.current_context.get("ids_present", False)
        }

    def _calculate_priority(self, agent_type: AgentType, state: OrchestratorState) -> int:
        """Calculate task priority based on phase and context"""
        phase_priorities = {
            "reconnaissance": {AgentType.RECON: 10, AgentType.ANALYSIS: 5},
            "initial_access": {AgentType.EXPLOIT: 10, AgentType.ANALYSIS: 3},
            "persistence": {AgentType.PERSISTENCE: 10, AgentType.LATERAL: 7},
            "execution": {AgentType.LATERAL: 8, AgentType.EXFIL: 10},
            "cleanup": {AgentType.CLEANUP: 10, AgentType.ANALYSIS: 8}
        }

        return phase_priorities.get(state.phase, {}).get(agent_type, 5)

    def _calculate_phase_confidence(self, state: OrchestratorState) -> float:
        """Calculate confidence in current phase determination"""
        indicators = 0
        total = 0

        phase_indicators = {
            "reconnaissance": ["target_identified", "services_enumerated"],
            "initial_access": ["vulnerabilities_found", "exploit_available"],
            "persistence": ["access_gained", "privileges_elevated"],
            "execution": ["persistence_established", "targets_identified"],
            "cleanup": ["objectives_completed", "exfil_complete"]
        }

        for indicator in phase_indicators.get(state.phase, []):
            total += 1
            if state.current_context.get(indicator):
                indicators += 1

        return indicators / total if total > 0 else 0.5

    async def run(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the orchestrator with initial context"""
        initial_state = OrchestratorState(
            messages=[HumanMessage(content=json.dumps(initial_context))],
            current_context=initial_context,
            active_agents=[],
            task_queue=[],
            results={},
            phase="initialization",
            metadata={}
        )

        final_state = await self.graph.ainvoke(initial_state)

        return {
            "final_phase": final_state.phase,
            "results": final_state.results,
            "metadata": final_state.metadata
        }