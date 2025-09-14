#!/bin/bash

# Initialize SOTA Cua Computer-Use Agent
# For OSWorld-Verified benchmark optimization

echo "=== Initializing SOTA Cua Agent Project ==="

# Create project structure
mkdir -p cua_agent/{agents,prompts,context,benchmarks,configs}

# Create Python virtual environment
echo "Setting up Python environment..."
python -m venv cua_agent/venv

# Activate virtual environment (cross-platform)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    source cua_agent/venv/Scripts/activate
else
    source cua_agent/venv/bin/activate
fi

# Install Cua dependencies
echo "Installing Cua framework..."
pip install --upgrade pip
pip install cua-agent[all]
pip install cua-computer[all]

# Install additional dependencies for optimization
echo "Installing optimization dependencies..."
pip install numpy pandas scikit-learn
pip install transformers sentence-transformers  # For context management
pip install asyncio aiohttp
pip install python-dotenv
pip install pyyaml
pip install tqdm rich

# Create requirements file
pip freeze > cua_agent/requirements.txt

echo "Project structure created successfully!"
echo "Next steps:"
echo "1. Configure your API keys in .env file"
echo "2. Run the agent with: python cua_agent/main.py"
echo "3. Benchmark with: python cua_agent/benchmark.py"