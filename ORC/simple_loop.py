import asyncio
from typing import Dict, Any, Optional
from enum import Enum

from orchestrator import Orchestrator
from agent_spawner import AgentSpawner


class ActionType(Enum):
    CONTINUE = "continue"
    NEEDS_APPROVAL = "needs_approval"
    COMPLETE = "complete"


class SimpleORCLoop:
    """Simple execution loop - do first, ask only when necessary"""

    def __init__(self, knowledge_graph_url: str = "http://localhost:8000/api/knowledge"):
        self.orchestrator = Orchestrator(knowledge_graph_url)
        self.spawner = AgentSpawner(knowledge_graph_url)
        self.context = {}
        self.pending_action = None

    async def run(self, initial_prompt: str) -> None:
        """Main execution loop"""

        # Parse initial prompt into context
        self.context = self._parse_prompt(initial_prompt)

        while True:
            # Execute current phase
            result = await self._execute_current_phase()

            # Update context with discoveries
            self.context.update(result.get("discoveries", {}))

            # Determine next action
            next_action = self._determine_next_action(result)

            if next_action == ActionType.COMPLETE:
                print("✓ Operation complete")
                break

            elif next_action == ActionType.NEEDS_APPROVAL:
                # Only ask when about to do something significant
                approval = await self._get_approval(result)
                if not approval:
                    print("Operation cancelled")
                    break

            # Otherwise just continue automatically
            # The loop continues with updated context

    async def _execute_current_phase(self) -> Dict[str, Any]:
        """Execute agents based on current context"""

        # Determine what agents to run based on context
        if "vulnerabilities" not in self.context:
            # Need recon first
            agents_to_run = ["recon"]
        elif "access_gained" not in self.context:
            # Have vulns, try exploit
            agents_to_run = ["exploit"]
        elif "persistence" not in self.context:
            # Have access, establish persistence
            agents_to_run = ["persistence"]
        else:
            # Final analysis
            agents_to_run = ["analysis"]

        print(f"→ Running: {', '.join(agents_to_run)}")

        results = {}
        for agent in agents_to_run:
            result = await self.spawner.spawn_agent(agent, {}, self.context)
            results[agent] = result

            # Show progress inline
            if result.get("success"):
                print(f"  ✓ {agent}: {self._summarize_result(result)}")
            else:
                print(f"  ✗ {agent}: failed")

        return {
            "agents_run": agents_to_run,
            "results": results,
            "discoveries": self._extract_discoveries(results)
        }

    def _determine_next_action(self, result: Dict[str, Any]) -> ActionType:
        """Determine if we should continue, ask, or complete"""

        # Complete if we've done everything
        if "analysis" in result.get("agents_run", []):
            return ActionType.COMPLETE

        # Ask for approval before destructive/persistent actions
        if "exploit" in result.get("agents_run", []) and result["results"]["exploit"].get("success"):
            if self.context.get("next_phase") == "persistence":
                self.pending_action = "establish_persistence"
                return ActionType.NEEDS_APPROVAL

        # Ask before lateral movement
        if self.context.get("discovered_systems", 0) > 5:
            self.pending_action = "lateral_movement"
            return ActionType.NEEDS_APPROVAL

        # Otherwise just continue
        return ActionType.CONTINUE

    async def _get_approval(self, result: Dict[str, Any]) -> bool:
        """Get user approval for significant action"""

        action_descriptions = {
            "establish_persistence": "Establish persistence on compromised system",
            "lateral_movement": f"Move laterally to {self.context.get('discovered_systems', 0)} discovered systems",
            "data_exfiltration": "Begin data exfiltration"
        }

        description = action_descriptions.get(self.pending_action, self.pending_action)

        print(f"\n? {description}?")
        response = input("  Continue? (y/n): ").strip().lower()

        return response in ['y', 'yes']

    def _parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse initial prompt into context"""
        context = {}

        # Extract target
        words = prompt.split()
        for word in words:
            if '.' in word or any(c.isdigit() for c in word):
                context["target"] = word
                break

        # Detect mode
        if "stealth" in prompt.lower():
            context["stealth"] = True
        if "quick" in prompt.lower():
            context["quick_mode"] = True

        return context

    def _extract_discoveries(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract important discoveries from results"""
        discoveries = {}

        for agent, result in results.items():
            if result.get("context_updates"):
                discoveries.update(result["context_updates"])

        return discoveries

    def _summarize_result(self, result: Dict[str, Any]) -> str:
        """Create one-line summary of result"""
        if "findings" in result:
            findings = result["findings"]
            if isinstance(findings, dict):
                return f"found {len(findings)} items"
            elif isinstance(findings, list):
                return f"found {len(findings)} results"
        return "completed"


async def main():
    """Example usage"""

    print("ORC Simple Loop Demo")
    print("=" * 40)

    loop = SimpleORCLoop()

    # Example prompts
    prompts = [
        "scan 192.168.1.1 quickly",
        "test example.com with stealth",
        "assess security of target.local"
    ]

    print(f"Example: {prompts[0]}")
    print("-" * 40)

    await loop.run(prompts[0])


if __name__ == "__main__":
    asyncio.run(main())