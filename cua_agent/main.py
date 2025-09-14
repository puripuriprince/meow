"""
SOTA Cua Computer-Use Agent
Optimized for OSWorld-Verified Benchmark
"""

import asyncio
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import yaml
import json
from datetime import datetime

from cua_agent import ComputerAgent
from cua_computer import Computer

from context_manager import AdvancedContextManager
from prompt_optimizer import SystemPromptOptimizer


@dataclass
class AgentConfig:
    """Configuration for the optimized Cua agent"""
    model: str = "anthropic/claude-3-5-sonnet-20241022"
    max_trajectory_budget: float = 10.0
    temperature: float = 0.1
    max_tokens: int = 8192
    context_window_size: int = 200000
    use_memory_compression: bool = True
    use_adaptive_prompting: bool = True
    benchmark_mode: bool = False


class SOTACuaAgent:
    """State-of-the-art Computer-Use Agent with optimizations"""

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.context_manager = AdvancedContextManager(
            window_size=self.config.context_window_size,
            use_compression=self.config.use_memory_compression
        )
        self.prompt_optimizer = SystemPromptOptimizer()
        self.computer = None
        self.agent = None
        self.session_history = []

    async def initialize(self):
        """Initialize computer and agent instances"""
        # Initialize computer interface
        self.computer = Computer()
        await self.computer.start()

        # Get optimized system prompt
        system_prompt = self.prompt_optimizer.get_optimized_prompt(
            task_type="general",
            benchmark_mode=self.config.benchmark_mode
        )

        # Initialize agent with optimized configuration
        self.agent = ComputerAgent(
            model=self.config.model,
            tools=[self.computer],
            max_trajectory_budget=self.config.max_trajectory_budget,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            system_prompt=system_prompt
        )

    async def execute_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a task with advanced context management

        Args:
            task: Task description
            context: Additional context information

        Returns:
            Execution results with performance metrics
        """
        start_time = datetime.now()

        # Prepare context
        enhanced_context = self.context_manager.prepare_context(
            task=task,
            additional_context=context,
            history=self.session_history
        )

        # Adapt prompt based on task complexity
        if self.config.use_adaptive_prompting:
            task = self.prompt_optimizer.adapt_prompt(task, enhanced_context)

        # Execute task
        try:
            result = await self.agent.run(
                task,
                context=enhanced_context
            )

            # Process and store result
            execution_time = (datetime.now() - start_time).total_seconds()

            processed_result = {
                "task": task,
                "result": result,
                "execution_time": execution_time,
                "context_tokens": self.context_manager.get_token_count(),
                "success": True
            }

            # Update session history
            self.session_history.append({
                "task": task,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })

            # Compress context if needed
            if self.config.use_memory_compression:
                self.context_manager.compress_history(self.session_history)

            return processed_result

        except Exception as e:
            return {
                "task": task,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "success": False
            }

    async def benchmark_run(self, tasks: List[str]) -> Dict[str, Any]:
        """Run benchmark tasks for OSWorld-Verified"""
        self.config.benchmark_mode = True
        await self.initialize()

        results = []
        for task in tasks:
            result = await self.execute_task(task)
            results.append(result)

        # Calculate metrics
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        avg_time = sum(r["execution_time"] for r in results) / len(results)

        return {
            "results": results,
            "metrics": {
                "success_rate": success_rate,
                "average_execution_time": avg_time,
                "total_tasks": len(tasks)
            }
        }

    async def cleanup(self):
        """Clean up resources"""
        if self.computer:
            await self.computer.stop()


async def main():
    """Main entry point"""
    # Load configuration
    config = AgentConfig()

    # Initialize agent
    agent = SOTACuaAgent(config)
    await agent.initialize()

    # Example task
    task = "Open a web browser and navigate to example.com"
    result = await agent.execute_task(task)

    print(f"Task completed: {result['success']}")
    print(f"Execution time: {result['execution_time']}s")

    await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())