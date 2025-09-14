"""
Minimal prompt connector for evoPrompt integration
Links cua_agent with external prompt evolution system
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional


class PromptConnector:
    """Simple connector to use prompts from evoPrompt folder"""

    def __init__(self, evo_prompt_path: str = "../evoPrompt"):
        self.evo_prompt_path = Path(evo_prompt_path)
        self.current_prompt = None

    def load_evolved_prompt(self, prompt_file: str = "best_prompt.txt") -> str:
        """Load the best evolved prompt from evoPrompt"""
        prompt_path = self.evo_prompt_path / prompt_file

        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                return f.read()

        # Fallback to default
        return self.get_default_prompt()

    def get_default_prompt(self) -> str:
        """Minimal default prompt for computer use"""
        return """You are a precise computer-use agent. Execute tasks accurately and efficiently.
Focus on task completion with minimal steps. Verify each action before proceeding."""

    def save_for_evolution(self, task: str, success: bool, metrics: Dict):
        """Save task results for prompt evolution"""
        evolution_data_path = self.evo_prompt_path / "evolution_data.jsonl"

        with open(evolution_data_path, 'a') as f:
            json.dump({
                "task": task,
                "success": success,
                "metrics": metrics,
                "prompt_used": self.current_prompt
            }, f)
            f.write('\n')