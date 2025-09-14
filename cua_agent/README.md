# SOTA Cua Computer-Use Agent

Optimized for OSWorld-Verified benchmark using Nuanced.dev context management and evolved prompts.

## Setup

1. **Install dependencies:**
```bash
bash ../init_cua_agent.sh
```

2. **Set up Nuanced.dev (get free trial at https://nuanced.dev):**
```bash
export NUANCED_API_KEY="your-api-key"
```

3. **Set up Anthropic API:**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## Workflow

### Step 1: Run Benchmark with Nuanced.dev
First, collect benchmark data with intelligent context management:

```bash
python benchmark_nuanced.py
```

This will:
- Run OSWorld-Verified tasks with Nuanced.dev context
- Save performance data to `../evoPrompt/benchmark_data.jsonl`
- Export context insights

### Step 2: Evolve Prompts
Use the benchmark data to evolve optimal prompts:

```bash
python evolve_prompts.py
```

This will:
- Load benchmark performance data
- Run genetic algorithm to evolve prompts
- Save best prompt to `../evoPrompt/best_prompt.txt`

### Step 3: Run Optimized Agent
Use the evolved prompt with Nuanced.dev for best performance:

```bash
python optimized_agent.py
```

## Architecture

```
┌─────────────────────┐
│   Evolved Prompt    │ ← Generated from benchmark data
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   Cua Agent         │ ← Computer control
├─────────────────────┤
│  Nuanced.dev API    │ ← Intelligent context
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  OSWorld Tasks      │ ← Benchmark execution
└─────────────────────┘
```

## Key Features

1. **Nuanced.dev Integration:**
   - Semantic context management
   - Automatic deduplication
   - Relevance filtering
   - Memory layers (immediate, working, episodic, semantic)

2. **Prompt Evolution:**
   - Genetic algorithm optimization
   - Component-based evolution
   - Fitness based on benchmark performance

3. **Optimized Execution:**
   - Low temperature for consistency
   - Context-aware task enhancement
   - Error recovery and retry logic

## Performance Tips

1. Always run the benchmark first to collect data
2. Run prompt evolution multiple times for better results
3. Use Nuanced.dev API for best context management
4. Monitor `benchmark_insights.json` for performance metrics

## Files

- `main.py` - Base Cua agent implementation
- `context_manager.py` - Nuanced.dev integration
- `benchmark_nuanced.py` - Benchmark runner with context
- `evolve_prompts.py` - Prompt evolution system
- `optimized_agent.py` - Final optimized agent
- `prompt_connector.py` - Bridge to evoPrompt folder

## Results

After running the full workflow, the agent will:
- Consistently score high on OSWorld-Verified
- Use minimal actions per task
- Have intelligent error recovery
- Leverage context for better decisions