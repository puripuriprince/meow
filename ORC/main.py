import asyncio
from typing import Dict, Any
import json
from orchestrator import Orchestrator
from agent_spawner import AgentSpawner


class ORCSystem:
    def __init__(self, knowledge_graph_url: str = "http://localhost:8000/api/knowledge", api_key: str = None):
        self.orchestrator = Orchestrator(knowledge_graph_url, api_key)
        self.spawner = AgentSpawner(knowledge_graph_url)

    async def execute_operation(self, target: str, objectives: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete operation against a target"""

        initial_context = {
            "target": target,
            "objectives": objectives,
            "stealth_mode": objectives.get("stealth", True),
            "time_limit": objectives.get("time_limit", 3600),
            "scope": objectives.get("scope", "full"),
            "target_identified": False,
            "access_gained": False,
            "persistence_established": False,
            "objectives_remaining": True
        }

        print(f"[ORC] Initiating operation against {target}")
        print(f"[ORC] Objectives: {json.dumps(objectives, indent=2)}")

        results = await self.orchestrator.run(initial_context)

        print(f"\n[ORC] Operation completed")
        print(f"[ORC] Final phase: {results['final_phase']}")
        print(f"[ORC] Results summary:")

        for agent, agent_results in results['results'].items():
            status = "✓" if agent_results.get("success") else "✗"
            print(f"  {status} {agent}: {agent_results.get('findings', 'No findings')}")

        return results

    async def run_custom_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Run a custom workflow with specific agent sequence"""

        results = {}
        context = workflow.get("initial_context", {})

        for step in workflow.get("steps", []):
            agent_type = step["agent"]
            task = step["task"]

            print(f"\n[ORC] Executing step: {step.get('name', agent_type)}")

            agent_result = await self.spawner.spawn_agent(agent_type, task, context)

            if agent_result.get("success"):
                context.update(agent_result.get("context_updates", {}))
                results[step.get("name", agent_type)] = agent_result
                print(f"[ORC] Step completed successfully")
            else:
                print(f"[ORC] Step failed: {agent_result.get('error')}")
                if step.get("required", True):
                    break

        return {
            "workflow": workflow.get("name", "custom"),
            "results": results,
            "final_context": context
        }

    def cleanup(self):
        """Cleanup resources"""
        self.spawner.cleanup()


async def example_usage():
    """Example usage of the ORC system"""

    orc = ORCSystem(
        knowledge_graph_url="http://localhost:8000/api/knowledge",
        api_key="your_api_key_here"
    )

    # Example 1: Standard operation
    print("=" * 50)
    print("Example 1: Standard Security Assessment")
    print("=" * 50)

    operation_results = await orc.execute_operation(
        target="example.com",
        objectives={
            "type": "security_assessment",
            "stealth": True,
            "scope": "external",
            "time_limit": 1800,
            "goals": ["identify_vulnerabilities", "assess_risk", "generate_report"]
        }
    )

    # Example 2: Custom workflow
    print("\n" + "=" * 50)
    print("Example 2: Custom Workflow")
    print("=" * 50)

    custom_workflow = {
        "name": "Quick Recon",
        "initial_context": {
            "target": "testsite.com",
            "quick_scan": True
        },
        "steps": [
            {
                "name": "Initial Recon",
                "agent": "recon",
                "task": {
                    "objective": "Quick reconnaissance",
                    "constraints": {"timeout": 60}
                },
                "required": True
            },
            {
                "name": "Risk Analysis",
                "agent": "analysis",
                "task": {
                    "objective": "Analyze recon findings",
                    "constraints": {"report_type": "summary"}
                },
                "required": False
            }
        ]
    }

    workflow_results = await orc.run_custom_workflow(custom_workflow)

    print("\n[ORC] Custom workflow completed")
    print(f"[ORC] Final context: {json.dumps(workflow_results['final_context'], indent=2)}")

    orc.cleanup()


if __name__ == "__main__":
    asyncio.run(example_usage())