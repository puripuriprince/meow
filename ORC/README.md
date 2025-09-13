# ORC - Orchestration Agent System

An intelligent orchestration system using LangGraph that dynamically spawns specialized agents based on context and objectives.

## Architecture

### Core Components

1. **Orchestrator** (`orchestrator.py`)
   - Main orchestration logic using LangGraph StateGraph
   - Manages operation phases (recon, exploit, persistence, lateral movement, exfiltration, cleanup)
   - Context-aware agent selection and task distribution
   - Result aggregation and decision making

2. **Agent Spawner** (`agent_spawner.py`)
   - Dynamic agent spawning system
   - Base agent class for consistent interface
   - Specialized agents (Recon, Exploit, Analysis)
   - Concurrent execution support
   - Context validation and timeout management

3. **Main System** (`main.py`)
   - High-level API for operations
   - Custom workflow support
   - Integration between orchestrator and spawner

## Agent Types

- **RECON**: Network and service discovery
- **EXPLOIT**: Vulnerability exploitation
- **PERSISTENCE**: Maintaining access
- **LATERAL**: Moving through network
- **EXFIL**: Data extraction
- **ANALYSIS**: Security analysis and reporting
- **CLEANUP**: Trace removal

## Usage

```python
from main import ORCSystem

# Initialize the system
orc = ORCSystem(
    knowledge_graph_url="http://localhost:8000/api/knowledge",
    api_key="your_api_key"
)

# Run a standard operation
results = await orc.execute_operation(
    target="example.com",
    objectives={
        "type": "security_assessment",
        "stealth": True,
        "scope": "external",
        "goals": ["identify_vulnerabilities", "assess_risk"]
    }
)

# Run a custom workflow
workflow = {
    "name": "Custom Recon",
    "steps": [
        {
            "agent": "recon",
            "task": {"objective": "Quick scan"},
            "required": True
        },
        {
            "agent": "analysis",
            "task": {"objective": "Risk assessment"},
            "required": False
        }
    ]
}
results = await orc.run_custom_workflow(workflow)
```

## Installation

```bash
pip install -r requirements.txt
```

## Knowledge Graph Integration

The system is designed to integrate with a backend knowledge graph server that provides:
- Common vulnerability patterns
- Exploitation techniques
- Security best practices
- Tool usage guidelines

The knowledge graph URL is configured during initialization and agents can query it for contextual information.

## Workflow Phases

1. **Context Analysis**: Analyze current situation and determine operation phase
2. **Agent Selection**: Choose appropriate agents based on phase and objectives
3. **Task Distribution**: Create and prioritize tasks for selected agents
4. **Agent Execution**: Spawn and execute agents concurrently
5. **Result Aggregation**: Collect and analyze results from all agents
6. **Decision Point**: Determine next action (continue, retry, or complete)

## Extending the System

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement the `execute` method
3. Register the agent in `AgentSpawner`

```python
class CustomAgent(BaseAgent):
    async def execute(self, task, context):
        # Your agent logic here
        return {
            "success": True,
            "findings": {...},
            "context_updates": {...}
        }

# Register the agent
spawner.register_agent(
    "custom",
    CustomAgent,
    AgentConfig(
        name="custom_agent",
        capabilities=["custom_capability"],
        timeout=300
    )
)
```

## Notes

- The system uses async/await for concurrent agent execution
- Each agent has configurable timeout and retry mechanisms
- Context is passed between agents for coordination
- The orchestrator uses LangGraph for state management and workflow control