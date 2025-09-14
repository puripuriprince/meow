# Hackathon Multiverse

AI-powered therapeutic conversation optimization system using MCTS and multi-agent orchestration.

## Complete System Startup Guide

### Prerequisites

- Python 3.11+ 
- Redis server installed
- OpenAI API key set in `.env` file

### Virtual Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (do this in each terminal)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step-by-Step Launch Sequence

**Terminal 1: Start Redis Server**

```bash
redis-server
# Should show "Ready to accept connections"
```

**Terminal 2: Start Backend API**

```bash
cd /Users/matthieuhuss/AdventureX-Final/hackathon-multiverse
source .venv/bin/activate
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3: Start Web Visualization**

```bash
cd /Users/matthieuhuss/AdventureX-Final/hackathon-multiverse
source .venv/bin/activate
python3 frontend/server.py
# Visit http://localhost:3000 to see the visualization
```

**Terminal 4: Seed the System & Start Worker**

```bash
cd /Users/matthieuhuss/AdventureX-Final/hackathon-multiverse
source .venv/bin/activate

# Clear any old data and seed the system
redis-cli flushall
python3 scripts/dev_seed.py

# Start the parallel worker
python3 -m backend.worker.parallel_worker
```

**Terminal 5: (Optional) Live Terminal Monitor**

```bash
cd /Users/matthieuhuss/AdventureX-Final/hackathon-multiverse
source .venv/bin/activate
python3 -m visualization.live_monitor
```

### What You'll See

1. **Web Interface (localhost:3000)**: Matrix-style real-time visualization showing:
   - Semantic space exploration with colored nodes (red=resistant, green=breakthrough)
   - Live statistics (total nodes, avg therapeutic progress score, max session depth)
   - Real-time activity log of new therapeutic interventions being tested
   - Clickable "Best Sessions" showing highest-scoring therapeutic dialogues
2. **Worker Terminal**: Therapeutic conversation processing with logs like:

   ```
   🔄 Processing node depth=2 prompt='Therapist: I notice you said that "everything is fine"...'
   📚 Conversation context: 2 turns, last reply: 'Yeah, fine. Just work stuff.'
   🧬 Generated 3 therapeutic variants
   ✅ Child created TRAJECTORY_SCORE=0.650 priority=0.573
   ```

3. **Terminal Monitor**: ASCII dashboard with growth charts and real-time stats

### Quick Docker Alternative

**Start basic stack (without visualization)**

```bash
docker compose up --build
```

**Seed a root node**

```bash
python3 scripts/dev_seed.py
```

## For UI Developers

The backend provides a simple REST + WebSocket API:

1. **GET /graph** - Get all nodes for initial canvas rendering
2. **POST /seed** - Start exploration with a root prompt
3. **POST /focus_zone** - Boost/seed nodes in a polygon area
4. **WebSocket /ws** - Real-time updates as new nodes are created

**Example UI Integration:**

1. `GET /graph` once → draw initial points
2. Open WebSocket and incrementally add nodes
3. `POST /focus_zone` or `/seed` when user interacts

## Demo & Testing

**Quick demo (3 nodes):**

```bash
python scripts/e2e_demo.py
```

**100-node PARALLEL exploration with blazing speed:**

```bash
# Make sure system is running (see Complete System Startup Guide above)
# Then run analysis script:
python scripts/long_run_demo.py
```

**Analyze exploration patterns:**

```bash
python scripts/exploration_analyzer.py
```

**Run integration test:**

```bash
pytest tests/test_roundtrip.py -v
```

The long-run demo is perfect for observing AI exploration patterns over time with detailed agent logs and statistics.

## What You'll Observe

- **Therapeutic Conversation Optimization**: AI system learns effective therapeutic interventions for a complex patient (Alex)
- **Live exploration**: Watch nodes appear in real-time as AI explores different therapeutic approaches
- **Semantic space positioning**: Nodes positioned in 2D space based on OpenAI embeddings
- **Process-aware mutations**: Therapeutic responses that recognize defense mechanisms and transference patterns
- **Trajectory scoring**: Full sessions scored toward therapeutic breakthrough (0.0=defended, 1.0=transforming)
- **Tree structure**: Parent-child relationships showing session depth and therapeutic branching
- **Priority-based expansion**: More effective therapeutic approaches get processed first
- **Parallel processing**: 20 nodes processed simultaneously for 20x speed improvement
- **Real-time metrics**: Velocity tracking shows therapeutic interventions/second generation rate
- **Interactive sessions**: Click any high-scoring session to see the full Therapist↔Patient dialogue

## Key Features

### Goal-Directed Optimization Framework

This system demonstrates a general framework for optimizing therapeutic conversations toward healing:

- **Patient Model**: Complex therapy patient (Alex) with specific psychological profile and defenses
- **Therapist Model**: Evidence-based therapeutic interventions recognizing transference and resistance
- **Supervisor Model**: Clinical assessment scoring therapeutic process quality (o3-powered)
- **Exploration**: MCTS-inspired priority system discovers effective therapeutic approaches

### Real-Time Visualization

- **Matrix-style interface** showing semantic exploration in 2D space
- **Color-coded nodes** by trajectory score (red=defended, orange=mobilizing, green=breakthrough)
- **Live activity feed** with emoji-enhanced logging
- **Best conversations panel** with clickable dialogue viewers
- **WebSocket integration** for real-time updates as conversations evolve

License: MIT
