from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
from enum import Enum


class ContextSource(Enum):
    USER_INPUT = "user_input"
    AGENT_DISCOVERY = "agent_discovery"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    PREVIOUS_OPERATION = "previous_operation"
    ENVIRONMENT = "environment"


@dataclass
class ContextEntry:
    key: str
    value: Any
    source: ContextSource
    timestamp: datetime
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """Manages context accumulation and refinement throughout the operation lifecycle"""

    def __init__(self):
        self.context_store: Dict[str, List[ContextEntry]] = {}
        self.current_context: Dict[str, Any] = {}
        self.context_history: List[Dict[str, Any]] = []
        self.confidence_threshold = 0.7

    def add_context(
        self,
        key: str,
        value: Any,
        source: ContextSource,
        confidence: float = 1.0,
        metadata: Dict[str, Any] = None
    ):
        """Add or update context with source tracking"""
        entry = ContextEntry(
            key=key,
            value=value,
            source=source,
            timestamp=datetime.now(),
            confidence=confidence,
            metadata=metadata or {}
        )

        if key not in self.context_store:
            self.context_store[key] = []
        self.context_store[key].append(entry)

        # Update current context with highest confidence value
        self._update_current_context(key)

    def _update_current_context(self, key: str):
        """Update current context with the most reliable value"""
        entries = self.context_store[key]

        # Sort by confidence and timestamp (newer is better for same confidence)
        sorted_entries = sorted(
            entries,
            key=lambda x: (x.confidence, x.timestamp.timestamp()),
            reverse=True
        )

        if sorted_entries and sorted_entries[0].confidence >= self.confidence_threshold:
            self.current_context[key] = sorted_entries[0].value

    def merge_agent_context(self, agent_context: Dict[str, Any], agent_name: str):
        """Merge context from agent discoveries"""
        for key, value in agent_context.items():
            # Agents provide discovered context with varying confidence
            confidence = self._calculate_confidence(key, value, agent_name)
            self.add_context(
                key=key,
                value=value,
                source=ContextSource.AGENT_DISCOVERY,
                confidence=confidence,
                metadata={"agent": agent_name}
            )

    def _calculate_confidence(self, key: str, value: Any, agent_name: str) -> float:
        """Calculate confidence based on agent type and data type"""
        # This can be made more sophisticated based on agent reliability metrics
        agent_confidence = {
            "recon": 0.9,
            "exploit": 0.85,
            "analysis": 0.95,
            "persistence": 0.8
        }
        return agent_confidence.get(agent_name, 0.7)

    def get_context_for_phase(self, phase: str) -> Dict[str, Any]:
        """Get relevant context for a specific operation phase"""
        phase_requirements = {
            "reconnaissance": [
                "target", "scope", "time_limit", "stealth_mode",
                "allowed_techniques", "exclude_patterns"
            ],
            "initial_access": [
                "target", "vulnerabilities", "attack_surface",
                "access_requirements", "stealth_mode"
            ],
            "persistence": [
                "access_level", "target_os", "available_privileges",
                "persistence_methods", "detection_risk"
            ],
            "lateral_movement": [
                "network_map", "discovered_systems", "credentials",
                "target_systems", "movement_paths"
            ],
            "exfiltration": [
                "data_targets", "exfil_channels", "bandwidth_limits",
                "encryption_requirements", "stealth_mode"
            ]
        }

        required_keys = phase_requirements.get(phase, [])
        phase_context = {
            k: v for k, v in self.current_context.items()
            if k in required_keys
        }

        # Add phase-specific metadata
        phase_context["_phase"] = phase
        phase_context["_timestamp"] = datetime.now().isoformat()

        return phase_context

    def suggest_missing_context(self, phase: str) -> List[str]:
        """Identify missing context for a phase"""
        phase_requirements = {
            "reconnaissance": ["target", "scope"],
            "initial_access": ["vulnerabilities", "attack_surface"],
            "persistence": ["access_level", "target_os"],
            "lateral_movement": ["network_map", "discovered_systems"],
            "exfiltration": ["data_targets", "exfil_channels"]
        }

        required = phase_requirements.get(phase, [])
        missing = [k for k in required if k not in self.current_context]

        return missing

    def snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of current context"""
        snapshot = {
            "context": self.current_context.copy(),
            "timestamp": datetime.now().isoformat(),
            "sources": self._get_source_summary()
        }
        self.context_history.append(snapshot)
        return snapshot

    def _get_source_summary(self) -> Dict[str, int]:
        """Summarize context sources"""
        summary = {}
        for entries in self.context_store.values():
            for entry in entries:
                source_name = entry.source.value
                summary[source_name] = summary.get(source_name, 0) + 1
        return summary


class InfoGatheringAgent:
    """Specialized agent for gathering and refining context"""

    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        self.question_templates = self._load_question_templates()

    def _load_question_templates(self) -> Dict[str, List[str]]:
        """Load question templates for different scenarios"""
        return {
            "target_clarification": [
                "Is this an internal or external target?",
                "What is the primary domain/IP?",
                "Are there any subdomains or related systems in scope?",
                "What ports/services should be prioritized?"
            ],
            "scope_definition": [
                "What types of testing are authorized?",
                "Are there any systems that should be excluded?",
                "What is the time window for this operation?",
                "Should we maintain stealth? What level?"
            ],
            "objective_clarification": [
                "What is the primary goal of this operation?",
                "What specific data or access is needed?",
                "Should we establish persistence?",
                "What is the acceptable risk level?"
            ]
        }

    async def gather_initial_context(self, user_input: str) -> Tuple[Dict[str, Any], List[str]]:
        """Parse user input and identify missing context"""

        # Parse natural language input for context clues
        parsed_context = self._parse_user_input(user_input)

        # Add parsed context to manager
        for key, value in parsed_context.items():
            self.context_manager.add_context(
                key=key,
                value=value,
                source=ContextSource.USER_INPUT,
                confidence=0.9
            )

        # Identify what's missing
        missing = self._identify_missing_critical_context()

        # Generate clarifying questions
        questions = self._generate_clarifying_questions(missing)

        return self.context_manager.current_context, questions

    def _parse_user_input(self, input_text: str) -> Dict[str, Any]:
        """Parse natural language input for context"""
        context = {}

        # Simple keyword extraction (can be enhanced with NLP)
        if "stealth" in input_text.lower():
            context["stealth_mode"] = True
        if "quick" in input_text.lower() or "fast" in input_text.lower():
            context["time_limit"] = 600  # 10 minutes
        if "internal" in input_text.lower():
            context["scope"] = "internal"
        elif "external" in input_text.lower():
            context["scope"] = "external"

        # Extract potential targets (IPs, domains)
        import re

        # Domain pattern
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        domains = re.findall(domain_pattern, input_text)
        if domains:
            context["target"] = domains[0]
            context["additional_targets"] = domains[1:] if len(domains) > 1 else []

        # IP pattern
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        ips = re.findall(ip_pattern, input_text)
        if ips and "target" not in context:
            context["target"] = ips[0]

        return context

    def _identify_missing_critical_context(self) -> List[str]:
        """Identify critical missing context"""
        critical_keys = ["target", "scope", "objectives"]
        missing = []

        for key in critical_keys:
            if key not in self.context_manager.current_context:
                missing.append(key)

        return missing

    def _generate_clarifying_questions(self, missing_keys: List[str]) -> List[str]:
        """Generate questions for missing context"""
        questions = []

        for key in missing_keys:
            if key == "target" and "target_clarification" in self.question_templates:
                questions.extend(self.question_templates["target_clarification"][:2])
            elif key == "scope" and "scope_definition" in self.question_templates:
                questions.extend(self.question_templates["scope_definition"][:2])
            elif key == "objectives" and "objective_clarification" in self.question_templates:
                questions.extend(self.question_templates["objective_clarification"][:2])

        return questions[:3]  # Limit to 3 questions at a time

    async def refine_context(self, current_phase: str, agent_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Refine context based on agent feedback"""

        # Check for context gaps reported by agents
        if "missing_context" in agent_feedback:
            for key in agent_feedback["missing_context"]:
                if key not in self.context_manager.current_context:
                    # Try to infer or request this context
                    inferred_value = self._infer_context(key, agent_feedback)
                    if inferred_value:
                        self.context_manager.add_context(
                            key=key,
                            value=inferred_value,
                            source=ContextSource.AGENT_DISCOVERY,
                            confidence=0.7
                        )

        # Update context with discoveries
        if "discoveries" in agent_feedback:
            self.context_manager.merge_agent_context(
                agent_feedback["discoveries"],
                agent_feedback.get("agent", "unknown")
            )

        return self.context_manager.get_context_for_phase(current_phase)

    def _infer_context(self, key: str, feedback: Dict[str, Any]) -> Any:
        """Try to infer missing context from available information"""
        inferences = {
            "target_os": lambda f: f.get("detected_os", "unknown"),
            "network_size": lambda f: len(f.get("discovered_hosts", [])),
            "security_level": lambda f: "high" if f.get("ids_detected") else "medium"
        }

        if key in inferences:
            return inferences[key](feedback)
        return None