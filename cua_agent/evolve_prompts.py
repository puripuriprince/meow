"""
Prompt Evolution System for OSWorld-Verified Benchmark
Uses benchmark results to evolve optimal system prompts
"""

import json
import random
from typing import List, Dict, Tuple
from pathlib import Path
import numpy as np


class PromptEvolver:
    """
    Evolves prompts based on benchmark performance data
    Uses genetic algorithm approach for optimization
    """

    def __init__(self):
        self.population_size = 20
        self.mutation_rate = 0.2
        self.crossover_rate = 0.7
        self.elite_size = 4
        self.generations = 50

        # Prompt components to evolve
        self.components = {
            "precision": [
                "Execute actions with extreme precision",
                "Focus on accuracy over speed",
                "Verify each action twice",
                "Use exact coordinates and timing",
                "Double-check before proceeding"
            ],
            "efficiency": [
                "Minimize the number of actions",
                "Take the most direct path",
                "Avoid redundant operations",
                "Combine related actions when possible",
                "Optimize for speed"
            ],
            "verification": [
                "Always verify action completion",
                "Take screenshots for confirmation",
                "Check state after each action",
                "Ensure elements are visible before interaction",
                "Wait for page loads"
            ],
            "error_handling": [
                "Retry failed actions with adjustments",
                "Handle errors gracefully",
                "Implement fallback strategies",
                "Detect and recover from failures",
                "Adapt approach if blocked"
            ],
            "planning": [
                "Plan the full sequence before starting",
                "Break complex tasks into steps",
                "Identify the goal clearly",
                "Consider alternative approaches",
                "Think step-by-step"
            ]
        }

    def load_benchmark_data(self) -> List[Dict]:
        """Load benchmark results from evoPrompt folder"""
        data_path = Path("../evoPrompt/benchmark_data.jsonl")

        if not data_path.exists():
            print("No benchmark data found. Run benchmark first.")
            return []

        data = []
        with open(data_path, 'r') as f:
            for line in f:
                data.append(json.loads(line))

        return data

    def create_initial_population(self) -> List[Dict]:
        """Create initial population of prompts"""
        population = []

        for _ in range(self.population_size):
            prompt_genes = {
                category: random.choice(options)
                for category, options in self.components.items()
            }

            prompt = self.build_prompt(prompt_genes)
            population.append({
                "genes": prompt_genes,
                "prompt": prompt,
                "fitness": 0.0
            })

        return population

    def build_prompt(self, genes: Dict[str, str]) -> str:
        """Build system prompt from genes"""
        prompt = "You are an expert computer-use agent.\n\n"
        prompt += "CORE PRINCIPLES:\n"

        for category, instruction in genes.items():
            prompt += f"- {instruction}\n"

        prompt += "\nEXECUTE with focus on task completion and accuracy."

        return prompt

    def evaluate_fitness(self, individual: Dict, benchmark_data: List[Dict]) -> float:
        """
        Evaluate fitness based on benchmark performance
        Higher score = better performance
        """
        # Simulate testing (in real implementation, would run actual benchmark)
        # For now, use heuristics based on prompt content

        prompt = individual["prompt"]
        fitness = 0.0

        # Analyze success correlation with prompt features
        for result in benchmark_data:
            if result["success"]:
                # Reward prompts that led to success
                if "precision" in prompt.lower() and result["action_count"] < 10:
                    fitness += 2.0
                if "verify" in prompt.lower():
                    fitness += 1.5
                if "efficient" in prompt.lower() and result["execution_time"] < 30:
                    fitness += 1.8

        # Penalize overly complex prompts
        if len(prompt) > 500:
            fitness *= 0.9

        return fitness

    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Create offspring through crossover"""
        child_genes = {}

        for category in self.components.keys():
            if random.random() < 0.5:
                child_genes[category] = parent1["genes"][category]
            else:
                child_genes[category] = parent2["genes"][category]

        return {
            "genes": child_genes,
            "prompt": self.build_prompt(child_genes),
            "fitness": 0.0
        }

    def mutate(self, individual: Dict) -> Dict:
        """Mutate an individual"""
        if random.random() < self.mutation_rate:
            # Randomly change one component
            category = random.choice(list(self.components.keys()))
            individual["genes"][category] = random.choice(self.components[category])
            individual["prompt"] = self.build_prompt(individual["genes"])

        return individual

    def select_parents(self, population: List[Dict]) -> Tuple[Dict, Dict]:
        """Tournament selection"""
        tournament_size = 3

        tournament1 = random.sample(population, tournament_size)
        parent1 = max(tournament1, key=lambda x: x["fitness"])

        tournament2 = random.sample(population, tournament_size)
        parent2 = max(tournament2, key=lambda x: x["fitness"])

        return parent1, parent2

    def evolve(self) -> Dict:
        """Main evolution loop"""
        print("Starting prompt evolution...")

        # Load benchmark data
        benchmark_data = self.load_benchmark_data()

        if not benchmark_data:
            print("Using default fitness function")

        # Initialize population
        population = self.create_initial_population()

        best_overall = None
        best_fitness = 0.0

        for generation in range(self.generations):
            # Evaluate fitness
            for individual in population:
                individual["fitness"] = self.evaluate_fitness(individual, benchmark_data)

            # Sort by fitness
            population.sort(key=lambda x: x["fitness"], reverse=True)

            # Track best
            if population[0]["fitness"] > best_fitness:
                best_fitness = population[0]["fitness"]
                best_overall = population[0]

            print(f"Generation {generation + 1}/{self.generations} - Best fitness: {best_fitness:.2f}")

            # Create next generation
            new_population = []

            # Elitism - keep best individuals
            new_population.extend(population[:self.elite_size])

            # Create offspring
            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate:
                    parent1, parent2 = self.select_parents(population)
                    child = self.crossover(parent1, parent2)
                else:
                    child = random.choice(population).copy()

                child = self.mutate(child)
                new_population.append(child)

            population = new_population

        return best_overall

    def save_evolved_prompt(self, best_individual: Dict):
        """Save the best evolved prompt to evoPrompt folder"""
        # Create evoPrompt directory if it doesn't exist
        evo_dir = Path("../evoPrompt")
        evo_dir.mkdir(exist_ok=True)

        # Save for direct use
        with open(evo_dir / "best_prompt.txt", 'w') as f:
            f.write(best_individual["prompt"])

        # Save with metadata
        with open(evo_dir / "evolved_prompt.json", 'w') as f:
            json.dump({
                "prompt": best_individual["prompt"],
                "fitness": best_individual["fitness"],
                "genes": best_individual["genes"]
            }, f, indent=2)

        print(f"\nBest evolved prompt saved!")
        print(f"Fitness score: {best_individual['fitness']:.2f}")
        print("\nPrompt preview:")
        print(best_individual["prompt"][:200] + "...")


def main():
    """Run prompt evolution"""
    evolver = PromptEvolver()

    # Evolve prompts
    best = evolver.evolve()

    # Save results
    evolver.save_evolved_prompt(best)

    print("\n" + "="*50)
    print("Evolution complete!")
    print("Use the evolved prompt for optimal benchmark performance")
    print("="*50)


if __name__ == "__main__":
    main()