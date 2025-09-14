"""
Adapter to configure evoPrompt agents for OSWorld-Verified benchmark optimization
Replaces the Putin peace negotiation demo with computer-use prompt evolution
"""

from typing import List, Dict
import openai
import os
from backend.config import settings


class BenchmarkMutator:
    """Mutator agent for computer-use prompt evolution"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def mutate(self, conversation_history: List[Dict[str, str]]) -> List[str]:
        """
        Generate strategic prompt variations for computer-use tasks
        Input: Full conversation history (previous prompt attempts)
        Output: 3 new prompt variations
        """

        # Build context from conversation history
        context = "\n".join([
            f"Attempt {i+1}: {turn['content']}"
            for i, turn in enumerate(conversation_history)
            if turn['role'] == 'user'
        ])

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are optimizing system prompts for a computer-use agent benchmark (OSWorld-Verified).

The agent needs to:
1. Execute GUI automation tasks (clicking, typing, navigating)
2. Minimize action count while ensuring success
3. Verify actions and handle errors
4. Work with precision and efficiency

Based on the conversation history showing previous prompt attempts, generate 3 strategic variations that:
- Build on successful patterns
- Fix identified weaknesses
- Explore different approaches (precision vs speed, verification vs efficiency)

Output exactly 3 prompts, one per line, no numbering."""
                },
                {
                    "role": "user",
                    "content": f"Previous attempts:\n{context}\n\nGenerate 3 improved prompt variations:"
                }
            ],
            temperature=0.9,
            max_tokens=500
        )

        prompts = response.choices[0].message.content.strip().split('\n')
        return [p.strip() for p in prompts if p.strip()][:3]


class BenchmarkPersona:
    """Simulated benchmark agent that 'responds' with performance metrics"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def respond(self, prompt: str) -> str:
        """
        Simulate how the prompt would perform on benchmark
        Returns a 'response' describing expected performance
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are simulating how a computer-use agent would perform with the given system prompt.

Analyze the prompt and predict performance on OSWorld-Verified benchmark tasks like:
- Web navigation
- Form filling
- GUI interaction
- File operations

Respond with a brief performance assessment mentioning:
- Expected action efficiency (low/medium/high)
- Error handling capability
- Task completion likelihood
- Any potential weaknesses

Keep response under 100 words."""
                },
                {
                    "role": "user",
                    "content": f"System prompt to evaluate:\n{prompt}"
                }
            ],
            temperature=0.3,
            max_tokens=150
        )

        return response.choices[0].message.content.strip()


class BenchmarkCritic:
    """Critic that scores prompts based on expected benchmark performance"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def score(self, conversation_history: List[Dict[str, str]]) -> tuple[float, str]:
        """
        Score the trajectory of prompt evolution
        Returns: (score 0.0-1.0, reasoning)
        """

        # Get latest prompt and performance assessment
        latest_prompt = ""
        latest_assessment = ""

        for turn in reversed(conversation_history):
            if turn['role'] == 'user' and not latest_prompt:
                latest_prompt = turn['content']
            elif turn['role'] == 'assistant' and not latest_assessment:
                latest_assessment = turn['content']
            if latest_prompt and latest_assessment:
                break

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Score this computer-use agent prompt based on expected OSWorld-Verified benchmark performance.

Scoring criteria (0.0 to 1.0):
- 0.8-1.0: Excellent - balances precision, efficiency, verification, error handling
- 0.6-0.8: Good - strong in most areas but missing some aspects
- 0.4-0.6: Average - functional but lacks optimization
- 0.2-0.4: Poor - significant weaknesses
- 0.0-0.2: Very poor - unlikely to succeed

Output format:
SCORE: [0.00-1.00]
REASONING: [one sentence explanation]"""
                },
                {
                    "role": "user",
                    "content": f"Prompt: {latest_prompt}\n\nPerformance assessment: {latest_assessment}"
                }
            ],
            temperature=0.2,
            max_tokens=100
        )

        result = response.choices[0].message.content.strip()

        # Parse score and reasoning
        try:
            lines = result.split('\n')
            score_line = [l for l in lines if 'SCORE:' in l][0]
            score = float(score_line.split(':')[1].strip())

            reasoning_line = [l for l in lines if 'REASONING:' in l][0]
            reasoning = reasoning_line.split(':', 1)[1].strip()

            return score, reasoning
        except:
            return 0.5, "Could not parse score"


def register_benchmark_agents():
    """Register benchmark-optimized agents with evoPrompt"""

    # This would be called to switch evoPrompt from Putin demo to benchmark mode
    print("Switching evoPrompt to OSWorld-Verified benchmark optimization mode...")

    # The actual registration would happen in the worker files
    return {
        "mutator": BenchmarkMutator(),
        "persona": BenchmarkPersona(),
        "critic": BenchmarkCritic()
    }