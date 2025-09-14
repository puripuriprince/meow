"""
OSWorld-Verified Benchmark with Nuanced.dev Integration
Step 1: Run benchmarks with nuanced context management
Step 2: Collect performance data for prompt evolution
Step 3: Generate optimized system prompt
"""

import asyncio
import json
import os
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from cua_agent import ComputerAgent
from cua_computer import Computer
from context_manager import NuancedContextManager


class NuancedBenchmarkRunner:
    """
    Benchmark runner with full nuanced.dev integration
    Collects data for prompt evolution
    """

    def __init__(self):
        self.context_manager = NuancedContextManager()
        self.computer = None
        self.agent = None
        self.benchmark_data = []

        # Base prompt that will be evolved
        self.base_prompt = """You are a precise computer-use agent.
Execute tasks with maximum accuracy and efficiency.
Verify each action before proceeding to the next."""

    async def initialize(self):
        """Initialize with nuanced.dev"""
        print("Initializing nuanced.dev context manager...")
        await self.context_manager.initialize()

        print("Starting computer interface...")
        self.computer = Computer()
        await self.computer.start()

        print("Creating agent with nuanced context...")
        self.agent = ComputerAgent(
            model="anthropic/claude-3-5-sonnet-20241022",
            tools=[self.computer],
            system_prompt=self.base_prompt,
            max_trajectory_budget=15.0,
            temperature=0.1
        )

    async def run_task_with_nuanced(self, task_description: str) -> Dict[str, Any]:
        """
        Run a single task with full nuanced.dev context management
        """
        start_time = datetime.now()

        # Add task to nuanced context
        await self.context_manager.add_context(
            content=f"New task: {task_description}",
            context_type="task_start",
            metadata={"timestamp": start_time.isoformat()}
        )

        # Get relevant context from nuanced
        relevant_context = await self.context_manager.get_relevant_context(
            query=task_description,
            max_results=5
        )

        # Prepare enhanced task with nuanced context
        context_str = await self.context_manager.prepare_prompt_context(
            task=task_description,
            include_history=True
        )

        enhanced_task = f"{task_description}\n\n{context_str}"

        try:
            # Execute with nuanced-enhanced context
            result = await self.agent.run(enhanced_task)

            execution_time = (datetime.now() - start_time).total_seconds()
            action_count = len(result.get("trajectory", []))

            # Add result to nuanced context for learning
            await self.context_manager.add_context(
                content=f"Task completed: {action_count} actions in {execution_time:.2f}s",
                context_type="task_result",
                metadata={
                    "success": True,
                    "action_count": action_count,
                    "execution_time": execution_time
                }
            )

            # Compress context if needed
            await self.context_manager.compress_context()

            return {
                "task": task_description,
                "success": True,
                "action_count": action_count,
                "execution_time": execution_time,
                "trajectory": result.get("trajectory", []),
                "context_used": len(relevant_context)
            }

        except Exception as e:
            # Add error to nuanced context
            await self.context_manager.add_context(
                content=f"Task failed: {str(e)}",
                context_type="error",
                metadata={"task": task_description}
            )

            return {
                "task": task_description,
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }

    async def run_benchmark_suite(self) -> List[Dict[str, Any]]:
        """Run full benchmark suite with nuanced.dev"""

        # OSWorld-Verified benchmark tasks
        benchmark_tasks = [
            "Navigate to google.com and search for 'artificial intelligence'",
            "Open calculator and compute 527 + 389",
            "Take a screenshot of the desktop",
            "Open notepad and type 'Hello World'",
            "Navigate to wikipedia.org and search for 'quantum computing'",
            "Open file explorer and navigate to Documents folder",
            "Create a new folder named 'TestFolder' on the desktop",
            "Open a web browser and navigate to github.com",
            "Search for 'machine learning' on YouTube",
            "Open settings and navigate to display settings"
        ]

        results = []

        for i, task in enumerate(benchmark_tasks, 1):
            print(f"\n[{i}/{len(benchmark_tasks)}] Running: {task}")

            result = await self.run_task_with_nuanced(task)
            results.append(result)

            if result["success"]:
                print(f"✓ Success in {result['execution_time']:.2f}s with {result['action_count']} actions")
            else:
                print(f"✗ Failed: {result.get('error', 'Unknown error')}")

            # Save intermediate results for prompt evolution
            self.save_benchmark_data(result)

            # Brief pause between tasks
            await asyncio.sleep(2)

        return results

    def save_benchmark_data(self, result: Dict[str, Any]):
        """Save data for prompt evolution"""
        self.benchmark_data.append(result)

        # Save to file for evoPrompt
        evolution_data_path = Path("evoPrompt/benchmark_data.jsonl")
        evolution_data_path.parent.mkdir(exist_ok=True)

        with open(evolution_data_path, 'a') as f:
            json.dump({
                "task": result["task"],
                "success": result["success"],
                "action_count": result.get("action_count", 0),
                "execution_time": result.get("execution_time", 0),
                "prompt_used": self.base_prompt,
                "timestamp": datetime.now().isoformat()
            }, f)
            f.write('\n')

    async def export_nuanced_insights(self):
        """Export nuanced.dev insights for analysis"""
        print("\nExporting nuanced.dev session data...")
        await self.context_manager.export_session("nuanced_session.json")

        # Generate insights report
        insights = {
            "total_tasks": len(self.benchmark_data),
            "successful_tasks": sum(1 for r in self.benchmark_data if r["success"]),
            "average_actions": sum(r.get("action_count", 0) for r in self.benchmark_data) / len(self.benchmark_data),
            "average_time": sum(r.get("execution_time", 0) for r in self.benchmark_data) / len(self.benchmark_data),
            "context_effectiveness": {
                "average_context_items": sum(r.get("context_used", 0) for r in self.benchmark_data) / len(self.benchmark_data)
            }
        }

        with open("benchmark_insights.json", 'w') as f:
            json.dump(insights, f, indent=2)

        print(f"Success rate: {insights['successful_tasks']}/{insights['total_tasks']} ({insights['successful_tasks']/insights['total_tasks']*100:.1f}%)")
        print(f"Average actions: {insights['average_actions']:.1f}")
        print(f"Average time: {insights['average_time']:.2f}s")

    async def cleanup(self):
        """Clean up resources"""
        if self.computer:
            await self.computer.stop()
        await self.context_manager.cleanup()


async def main():
    """Run benchmark with nuanced.dev integration"""

    # Check for nuanced API key
    if not os.getenv("NUANCED_API_KEY"):
        print("Warning: NUANCED_API_KEY not set. Please set it to use nuanced.dev")
        print("Get your free trial at https://nuanced.dev")
        return

    runner = NuancedBenchmarkRunner()

    try:
        await runner.initialize()

        print("="*50)
        print("Starting OSWorld-Verified Benchmark")
        print("With Nuanced.dev Context Management")
        print("="*50)

        results = await runner.run_benchmark_suite()

        await runner.export_nuanced_insights()

        print("\n" + "="*50)
        print("Benchmark Complete!")
        print("Data saved for prompt evolution")
        print("Next step: Run prompt evolution with evoPrompt")
        print("="*50)

    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())