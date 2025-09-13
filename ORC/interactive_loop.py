import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum
import json
from datetime import datetime

from orchestrator import Orchestrator
from agent_spawner import AgentSpawner
from context_manager import ContextManager, InfoGatheringAgent, ContextSource


class LoopState(Enum):
    GATHERING = "gathering_context"
    PLANNING = "planning_operation"
    EXECUTING = "executing_agents"
    ANALYZING = "analyzing_results"
    AWAITING_INPUT = "awaiting_user_input"
    COMPLETE = "operation_complete"


class InteractiveORCLoop:
    """Main loop managing interaction between user, orchestrator, and agents"""

    def __init__(
        self,
        knowledge_graph_url: str = "http://localhost:8000/api/knowledge",
        api_key: Optional[str] = None
    ):
        self.orchestrator = Orchestrator(knowledge_graph_url, api_key)
        self.spawner = AgentSpawner(knowledge_graph_url)
        self.context_manager = ContextManager()
        self.info_agent = InfoGatheringAgent(self.context_manager)
        self.state = LoopState.AWAITING_INPUT
        self.operation_history = []
        self.pending_action = None
        self.auto_approve_threshold = 0.8  # Auto-approve if confidence > 80%

    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and return response"""

        # Handle special commands
        if user_input.lower() in ['exit', 'quit', 'stop']:
            self.state = LoopState.COMPLETE
            return {"status": "complete", "message": "Operation terminated by user"}

        if user_input.lower() == 'status':
            return self._get_status()

        if user_input.lower() == 'context':
            return {"context": self.context_manager.current_context}

        # Handle yes/no responses to pending actions
        if self.pending_action and user_input.lower() in ['y', 'yes', 'n', 'no']:
            return await self._handle_confirmation(user_input.lower() in ['y', 'yes'])

        # Process based on current state
        if self.state == LoopState.AWAITING_INPUT:
            return await self._handle_initial_input(user_input)
        else:
            return await self._handle_operational_input(user_input)

    async def _handle_initial_input(self, user_input: str) -> Dict[str, Any]:
        """Handle initial user input - make smart assumptions"""

        # Parse input and make intelligent assumptions
        context = await self.info_agent.gather_initial_context(user_input)

        # Make smart defaults for missing context
        assumptions = self._make_intelligent_assumptions(context, user_input)

        # Merge assumptions with context
        for key, value in assumptions.items():
            if key not in self.context_manager.current_context:
                self.context_manager.add_context(
                    key=key,
                    value=value["value"],
                    source=ContextSource.AGENT_DISCOVERY,
                    confidence=value["confidence"],
                    metadata={"assumption": True, "reason": value["reason"]}
                )

        # Create action plan
        action_plan = await self._create_action_plan()

        # Check if we should auto-proceed or ask for confirmation
        if action_plan["confidence"] >= self.auto_approve_threshold:
            # High confidence - just proceed with a brief notification
            return await self._execute_action(action_plan)
        else:
            # Lower confidence - ask for confirmation
            self.pending_action = action_plan
            return {
                "status": "confirm",
                "message": self._format_action_summary(action_plan),
                "prompt": "Proceed? (y/n or provide new instructions):"
            }

    def _make_intelligent_assumptions(self, context: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Make intelligent assumptions based on partial context"""
        assumptions = {}
        input_lower = user_input.lower()

        # Scope assumptions
        if "scope" not in context:
            if any(word in input_lower for word in ["internal", "lan", "192.168", "10.", "172."]):
                assumptions["scope"] = {
                    "value": "internal",
                    "confidence": 0.9,
                    "reason": "Detected internal network indicators"
                }
            else:
                assumptions["scope"] = {
                    "value": "external",
                    "confidence": 0.85,
                    "reason": "No internal indicators found, assuming external"
                }

        # Stealth assumptions
        if "stealth_mode" not in context:
            if any(word in input_lower for word in ["loud", "aggressive", "fast", "quick"]):
                assumptions["stealth_mode"] = {
                    "value": False,
                    "confidence": 0.9,
                    "reason": "Detected speed/aggression preference"
                }
            else:
                assumptions["stealth_mode"] = {
                    "value": True,
                    "confidence": 0.85,
                    "reason": "Default to stealthy approach"
                }

        # Time limit assumptions
        if "time_limit" not in context:
            if "quick" in input_lower or "fast" in input_lower:
                assumptions["time_limit"] = {
                    "value": 600,  # 10 minutes
                    "confidence": 0.8,
                    "reason": "User wants quick results"
                }
            elif "thorough" in input_lower or "complete" in input_lower:
                assumptions["time_limit"] = {
                    "value": 7200,  # 2 hours
                    "confidence": 0.8,
                    "reason": "User wants thorough analysis"
                }
            else:
                assumptions["time_limit"] = {
                    "value": 1800,  # 30 minutes default
                    "confidence": 0.7,
                    "reason": "Standard operation duration"
                }

        # Objective assumptions
        if "objectives" not in context:
            if any(word in input_lower for word in ["vuln", "security", "pentest", "assess"]):
                assumptions["objectives"] = {
                    "value": ["vulnerability_assessment", "risk_analysis"],
                    "confidence": 0.85,
                    "reason": "Security assessment indicators detected"
                }
            elif any(word in input_lower for word in ["recon", "enumerate", "discover"]):
                assumptions["objectives"] = {
                    "value": ["reconnaissance", "enumeration"],
                    "confidence": 0.9,
                    "reason": "Reconnaissance focus detected"
                }
            else:
                assumptions["objectives"] = {
                    "value": ["general_assessment"],
                    "confidence": 0.6,
                    "reason": "No specific objectives detected"
                }

        return assumptions

    async def _create_action_plan(self) -> Dict[str, Any]:
        """Create an action plan with confidence score"""
        context = self.context_manager.current_context

        # Calculate overall confidence
        total_confidence = 0
        confidence_count = 0

        for key, entries in self.context_manager.context_store.items():
            if entries:
                latest_entry = sorted(entries, key=lambda x: x.timestamp, reverse=True)[0]
                total_confidence += latest_entry.confidence
                confidence_count += 1

        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0.5

        # Determine initial agents based on objectives
        initial_agents = []
        objectives = context.get("objectives", ["general_assessment"])

        if "reconnaissance" in str(objectives) or "general_assessment" in objectives:
            initial_agents.append("recon")
        if "vulnerability" in str(objectives):
            initial_agents.append("exploit")
        if not initial_agents:
            initial_agents = ["recon"]  # Default

        return {
            "action": "start_operation",
            "target": context.get("target", "unknown"),
            "scope": context.get("scope", "external"),
            "stealth": context.get("stealth_mode", True),
            "time_limit": context.get("time_limit", 1800),
            "initial_agents": initial_agents,
            "confidence": avg_confidence,
            "assumptions_made": [
                k for k, v in self.context_manager.context_store.items()
                if any(e.metadata.get("assumption") for e in v)
            ]
        }

    def _format_action_summary(self, action_plan: Dict[str, Any]) -> str:
        """Format action plan into readable summary"""
        summary = f"""
I'll start a {action_plan['scope']} security operation on {action_plan['target']}

Plan:
• Mode: {'Stealthy' if action_plan['stealth'] else 'Aggressive'} approach
• Time limit: {action_plan['time_limit'] // 60} minutes
• Initial phase: {', '.join(action_plan['initial_agents'])}
• Confidence: {action_plan['confidence']*100:.0f}%
"""

        if action_plan['assumptions_made']:
            summary += f"\nAssumptions made: {', '.join(action_plan['assumptions_made'])}"

        return summary

    async def _handle_confirmation(self, confirmed: bool) -> Dict[str, Any]:
        """Handle yes/no confirmation"""
        if not self.pending_action:
            return {"status": "error", "message": "No pending action"}

        if confirmed:
            action = self.pending_action
            self.pending_action = None
            return await self._execute_action(action)
        else:
            self.pending_action = None
            return {
                "status": "cancelled",
                "message": "Action cancelled. Please provide new instructions or corrections."
            }

    async def _execute_action(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action plan"""
        self.state = LoopState.EXECUTING

        # Quick status update
        result = {
            "status": "executing",
            "message": f"Starting operation on {action_plan['target']}...",
            "plan": action_plan
        }

        # Start the first agents
        initial_results = []
        for agent_type in action_plan['initial_agents']:
            agent_result = await self.spawner.spawn_agent(
                agent_type,
                {"objective": f"Initial {agent_type} on {action_plan['target']}"},
                self.context_manager.current_context
            )
            initial_results.append(agent_result)

            # Update context with findings
            if agent_result.get("context_updates"):
                self.context_manager.merge_agent_context(
                    agent_result["context_updates"],
                    agent_type
                )

        result["initial_results"] = initial_results
        result["next_action"] = self._determine_next_automatic_action(initial_results)

        return result

    def _determine_next_automatic_action(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine what to do next automatically"""
        successful = [r for r in results if r.get("success")]

        if len(successful) == len(results):
            # All successful - automatically continue
            return {
                "action": "auto_continue",
                "message": "Initial phase successful, proceeding automatically...",
                "confidence": 0.9
            }
        elif len(successful) > 0:
            # Partial success - ask for guidance
            return {
                "action": "request_guidance",
                "message": "Partial success. Continue with available data or retry failed components?",
                "confidence": 0.6
            }
        else:
            # Complete failure - need user input
            return {
                "action": "request_input",
                "message": "Initial phase failed. Please provide alternative approach or corrections.",
                "confidence": 0.2
            }

    async def _start_operation(self) -> Dict[str, Any]:
        """Start the operation with gathered context"""
        self.state = LoopState.PLANNING

        # Create operation plan
        plan = await self._create_operation_plan()

        self.state = LoopState.EXECUTING

        # Execute first phase
        result = await self._execute_phase(plan["first_phase"])

        return {
            "status": "executing",
            "plan": plan,
            "phase_result": result,
            "next_action": self._determine_next_action(result)
        }

    async def _create_operation_plan(self) -> Dict[str, Any]:
        """Create an operation plan based on context"""
        context = self.context_manager.current_context

        # Determine operation type and phases
        if context.get("scope") == "external":
            phases = ["reconnaissance", "initial_access", "analysis"]
        else:
            phases = ["reconnaissance", "initial_access", "persistence", "lateral_movement", "analysis"]

        plan = {
            "operation_id": f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "target": context.get("target", "unknown"),
            "phases": phases,
            "first_phase": phases[0],
            "estimated_duration": len(phases) * 300,  # 5 min per phase estimate
            "constraints": {
                "stealth": context.get("stealth_mode", True),
                "time_limit": context.get("time_limit", 3600)
            }
        }

        return plan

    async def _execute_phase(self, phase: str) -> Dict[str, Any]:
        """Execute a specific phase of the operation"""

        # Get phase-specific context
        phase_context = self.context_manager.get_context_for_phase(phase)

        # Run orchestrator for this phase
        result = await self.orchestrator.run(phase_context)

        # Update context with results
        if result.get("results"):
            for agent_name, agent_result in result["results"].items():
                if agent_result.get("context_updates"):
                    self.context_manager.merge_agent_context(
                        agent_result["context_updates"],
                        agent_name
                    )

        return result

    async def _handle_operational_input(self, user_input: str) -> Dict[str, Any]:
        """Handle input during operation execution"""

        command = user_input.lower().strip()

        if command == "pause":
            self.state = LoopState.AWAITING_INPUT
            return {"status": "paused", "message": "Operation paused. Type 'resume' to continue."}

        elif command == "resume":
            self.state = LoopState.EXECUTING
            return await self._continue_operation()

        elif command.startswith("adjust"):
            # Allow mid-operation adjustments
            adjustment = command.replace("adjust", "").strip()
            return await self._adjust_operation(adjustment)

        else:
            # Add as additional context
            self.context_manager.add_context(
                "user_guidance",
                user_input,
                ContextSource.USER_INPUT,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            return {"status": "noted", "message": "Guidance noted and added to context"}

    async def _continue_operation(self) -> Dict[str, Any]:
        """Continue operation from current state"""
        # Determine next phase based on context
        current_phase = self.context_manager.current_context.get("_phase", "reconnaissance")
        next_phase = self._get_next_phase(current_phase)

        if next_phase:
            result = await self._execute_phase(next_phase)
            return {
                "status": "executing",
                "phase": next_phase,
                "result": result,
                "next_action": self._determine_next_action(result)
            }
        else:
            self.state = LoopState.COMPLETE
            return self._generate_final_report()

    def _get_next_phase(self, current_phase: str) -> Optional[str]:
        """Determine next phase in operation"""
        phase_sequence = [
            "reconnaissance",
            "initial_access",
            "persistence",
            "lateral_movement",
            "exfiltration",
            "analysis",
            "cleanup"
        ]

        try:
            current_index = phase_sequence.index(current_phase)
            if current_index < len(phase_sequence) - 1:
                return phase_sequence[current_index + 1]
        except ValueError:
            pass

        return None

    def _determine_next_action(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Determine next action based on results"""

        if not result.get("results"):
            return {
                "action": "retry",
                "reason": "No results obtained",
                "suggestion": "Retry with different parameters"
            }

        success_count = sum(
            1 for r in result["results"].values()
            if r.get("success")
        )

        if success_count == 0:
            return {
                "action": "adjust",
                "reason": "All agents failed",
                "suggestion": "Adjust approach or provide additional context"
            }

        elif success_count < len(result["results"]) / 2:
            return {
                "action": "partial_continue",
                "reason": "Partial success",
                "suggestion": "Continue with available results or retry failed agents"
            }

        else:
            return {
                "action": "proceed",
                "reason": "Phase successful",
                "suggestion": "Proceed to next phase"
            }

    async def _adjust_operation(self, adjustment: str) -> Dict[str, Any]:
        """Adjust operation parameters"""

        adjustments = {}

        if "stealth" in adjustment:
            adjustments["stealth_mode"] = True
        if "aggressive" in adjustment:
            adjustments["stealth_mode"] = False
        if "fast" in adjustment:
            adjustments["time_limit"] = 300

        for key, value in adjustments.items():
            self.context_manager.add_context(key, value, ContextSource.USER_INPUT)

        return {
            "status": "adjusted",
            "adjustments": adjustments,
            "message": "Operation parameters adjusted"
        }

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final operation report"""

        report = {
            "status": "complete",
            "operation_summary": {
                "target": self.context_manager.current_context.get("target"),
                "duration": "N/A",  # Would calculate from timestamps
                "phases_completed": self._get_completed_phases(),
                "success_rate": self._calculate_success_rate()
            },
            "findings": self._aggregate_findings(),
            "recommendations": self._generate_recommendations(),
            "context_evolution": self.context_manager.context_history
        }

        return report

    def _get_completed_phases(self) -> List[str]:
        """Get list of completed phases"""
        # This would track actual completed phases
        return ["reconnaissance", "initial_access", "analysis"]

    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        # This would calculate from actual results
        return 0.75

    def _aggregate_findings(self) -> Dict[str, Any]:
        """Aggregate all findings from operation"""
        findings = {}
        for key, value in self.context_manager.current_context.items():
            if not key.startswith("_"):
                findings[key] = value
        return findings

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on operation results"""
        return [
            "Address identified vulnerabilities",
            "Implement additional monitoring",
            "Review access controls"
        ]

    def _get_status(self) -> Dict[str, Any]:
        """Get current operation status"""
        return {
            "state": self.state.value,
            "context": self.context_manager.current_context,
            "phase": self.context_manager.current_context.get("_phase", "N/A"),
            "active_agents": [a for a in self.spawner.active_agents.keys()]
        }


# Terminal UI wrapper
class TerminalInterface:
    """Simple terminal interface for the ORC system"""

    def __init__(self):
        self.loop = InteractiveORCLoop()
        self.running = True

    async def run(self):
        """Run the interactive terminal interface"""

        print("=" * 60)
        print("🎯 ORC - Orchestrated Security Operations System")
        print("=" * 60)
        print("\nType 'help' for commands or describe your operation goal.\n")

        while self.running:
            try:
                # Get user input
                user_input = input("\n[ORC] > ").strip()

                if user_input.lower() == "help":
                    self._show_help()
                    continue

                # Process through the loop
                response = await self.loop.process_user_input(user_input)

                # Display response
                self._display_response(response)

                # Check if complete
                if response.get("status") == "complete":
                    self.running = False

            except KeyboardInterrupt:
                print("\n\n[ORC] Operation interrupted by user")
                self.running = False
            except Exception as e:
                print(f"\n[ERROR] {str(e)}")

        print("\n[ORC] Session terminated. Goodbye!")

    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
  status    - Show current operation status
  context   - Display current context
  pause     - Pause current operation
  resume    - Resume paused operation
  adjust    - Adjust operation parameters
  exit      - Terminate operation

Examples:
  > Scan example.com for vulnerabilities with stealth
  > Internal penetration test on 192.168.1.0/24
  > Quick recon on target.com
        """
        print(help_text)

    def _display_response(self, response: Dict[str, Any]):
        """Display response in a formatted way"""

        status = response.get("status", "unknown")

        if status == "confirm":
            # Show action summary and ask for confirmation
            print(response.get("message", ""))
            print(response.get("prompt", "Proceed? (y/n):"))

        elif status == "executing":
            # Show brief execution status
            print(f"\n→ {response.get('message', 'Executing...')}")

            # Show initial results if available
            if "initial_results" in response:
                for result in response["initial_results"]:
                    agent = result.get("agent", "unknown")
                    success = "✓" if result.get("success") else "✗"
                    findings = result.get("findings", {})

                    # Show compact result
                    if isinstance(findings, dict) and findings:
                        first_key = list(findings.keys())[0]
                        print(f"  {success} {agent}: Found {first_key}")
                    else:
                        print(f"  {success} {agent}: {str(findings)[:60]}")

            # Show next automatic action
            if "next_action" in response:
                next_action = response["next_action"]
                if next_action["action"] == "auto_continue":
                    print(f"\n{next_action['message']}")
                elif next_action["action"] in ["request_guidance", "request_input"]:
                    print(f"\n❓ {next_action['message']}")

        elif status == "cancelled":
            print(f"\n✗ {response.get('message', 'Cancelled')}")

        elif status == "complete":
            print("\n" + "=" * 60)
            print("OPERATION COMPLETE")
            print("=" * 60)
            if "operation_summary" in response:
                summary = response["operation_summary"]
                print(f"Target: {summary.get('target')}")
                print(f"Success Rate: {summary.get('success_rate', 0) * 100:.1f}%")
                print(f"Phases: {', '.join(summary.get('phases_completed', []))}")

        else:
            print(f"\n[{status.upper()}] {response.get('message', json.dumps(response, indent=2))}")


async def main():
    """Main entry point"""
    interface = TerminalInterface()
    await interface.run()


if __name__ == "__main__":
    asyncio.run(main())