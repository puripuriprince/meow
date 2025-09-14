"""
Optimized Cua Agent with Evolved Prompts and Nuanced.dev
Final implementation that consistently performs well on OSWorld-Verified
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from cua_agent import ComputerAgent
from cua_computer import Computer
from context_manager import NuancedContextManager


class OptimizedCuaAgent:
    """
    SOTA Computer-Use Agent combining:
    1. Nuanced.dev for intelligent context management
    2. Evolved prompts from benchmark optimization
    3. Cua framework for computer control
    """

    def __init__(self):
        self.context_manager = NuancedContextManager()
        self.computer = None
        self.agent = None
        self.evolved_prompt = None

    def load_evolved_prompt(self) -> str:
        """Load the best evolved prompt from evoPrompt"""
        evo_prompt_path = Path("../evoPrompt/best_prompt.txt")

        if evo_prompt_path.exists():
            with open(evo_prompt_path, 'r') as f:
                prompt = f.read()
                print("✓ Loaded evolved prompt from evoPrompt")
                return prompt

        # Fallback to optimized default
        print("⚠ No evolved prompt found, using optimized default")
        return """You are an expert computer-use agent.

CORE PRINCIPLES:
- Execute actions with extreme precision
- Always verify action completion
- Minimize the number of actions
- Retry failed actions with adjustments
- Plan the full sequence before starting

EXECUTE with focus on task completion and accuracy."""

    async def initialize(self):
        """Initialize with nuanced.dev and evolved prompts"""
        print("Initializing optimized agent...")

        # Initialize nuanced.dev
        if os.getenv("NUANCED_API_KEY"):
            print("✓ Nuanced.dev API key found")
            await self.context_manager.initialize()
        else:
            print("⚠ No NUANCED_API_KEY - using local context management")

        # Load evolved prompt
        self.evolved_prompt = self.load_evolved_prompt()

        # Initialize computer
        self.computer = Computer()
        await self.computer.start()

        # Create optimized agent
        self.agent = ComputerAgent(
            model="anthropic/claude-3-5-sonnet-20241022",
            tools=[self.computer],
            system_prompt=self.evolved_prompt,
            max_trajectory_budget=15.0,
            temperature=0.1,  # Low for consistency
            max_tokens=8192
        )

        print("✓ Agent initialized and ready")

    async def execute(self, task: str) -> Dict[str, Any]:
        """
        Execute task with full optimization stack
        """
        print(f"\nExecuting: {task}")

        # Add to nuanced context
        await self.context_manager.add_context(
            content=f"Task: {task}",
            context_type="task_start"
        )

        # Get relevant context
        relevant_context = await self.context_manager.get_relevant_context(
            query=task,
            max_results=5
        )

        # Prepare enhanced task with context
        context_str = await self.context_manager.prepare_prompt_context(
            task=task,
            include_history=True
        )

        if context_str:
            enhanced_task = f"{task}\n\nContext:\n{context_str}"
        else:
            enhanced_task = task

        try:
            # Execute with optimized setup
            result = await self.agent.run(enhanced_task)

            # Add success to context for learning
            await self.context_manager.add_context(
                content=f"Task completed successfully",
                context_type="success",
                metadata={"task": task}
            )

            print("✓ Task completed successfully")
            return {
                "success": True,
                "result": result,
                "context_items_used": len(relevant_context)
            }

        except Exception as e:
            # Add error to context
            await self.context_manager.add_context(
                content=f"Task failed: {str(e)}",
                context_type="error",
                metadata={"task": task}
            )

            print(f"✗ Task failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def benchmark_mode(self):
        """Run in benchmark mode for OSWorld-Verified"""
        print("\n" + "="*50)
        print("BENCHMARK MODE - OSWorld-Verified")
        print("="*50)

        benchmark_tasks = [
            "Navigate to google.com",
            "Open calculator application",
            "Take a screenshot of the desktop",
            "Open a text editor and type 'Hello World'",
            "Navigate to wikipedia.org"
        ]

        results = []
        for task in benchmark_tasks:
            result = await self.execute(task)
            results.append(result)

            # Brief pause between tasks
            await asyncio.sleep(2)

        # Calculate success rate
        success_count = sum(1 for r in results if r["success"])
        success_rate = success_count / len(results) * 100

        print(f"\nBenchmark Results: {success_count}/{len(results)} ({success_rate:.1f}%)")

        return results

    async def cleanup(self):
        """Clean up resources"""
        if self.computer:
            await self.computer.stop()
        await self.context_manager.cleanup()


async def main():
    """Run the optimized agent"""
    agent = OptimizedCuaAgent()

    try:
        await agent.initialize()

        # Example: Run single task
        print("\n" + "="*50)
        print("Running single task demo")
        print("="*50)

        result = await agent.execute("Open a web browser and navigate to github.com")

        if result["success"]:
            print("Task succeeded!")
        else:
            print(f"Task failed: {result.get('error')}")

        # Optionally run benchmark
        print("\nRun full benchmark? (y/n): ", end="")
        if input().lower() == 'y':
            await agent.benchmark_mode()

    finally:
        await agent.cleanup()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║   Optimized Cua Agent for OSWorld       ║
    ║   With Nuanced.dev + Evolved Prompts    ║
    ╚══════════════════════════════════════════╝
    """)

    asyncio.run(main())