"""
Context Management System using nuanced.dev
Optimized for computer-use agents and OSWorld-Verified benchmark
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class ContextConfig:
    """Configuration for nuanced.dev integration"""
    api_key: str = os.getenv("NUANCED_API_KEY", "")
    api_url: str = "https://api.nuanced.dev/v1"
    max_context_length: int = 200000
    compression_threshold: float = 0.8
    relevance_threshold: float = 0.7
    use_semantic_search: bool = True
    use_memory_layers: bool = True


class NuancedContextManager:
    """
    Advanced context management using nuanced.dev
    Features:
    - Intelligent context compression
    - Semantic relevance filtering
    - Multi-layer memory management
    - Automatic deduplication
    """

    def __init__(self, config: Optional[ContextConfig] = None):
        self.config = config or ContextConfig()
        self.session = None
        self.context_id = None
        self.memory_layers = {
            "immediate": [],  # Current task context
            "working": [],    # Recent relevant actions
            "episodic": [],   # Important past events
            "semantic": []    # Knowledge and patterns
        }

    async def initialize(self):
        """Initialize nuanced.dev session"""
        self.session = aiohttp.ClientSession()

        # Create new context session
        async with self.session.post(
            f"{self.config.api_url}/context/create",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            json={
                "max_length": self.config.max_context_length,
                "features": {
                    "semantic_search": self.config.use_semantic_search,
                    "memory_layers": self.config.use_memory_layers,
                    "auto_compression": True,
                    "relevance_filtering": True
                }
            }
        ) as resp:
            data = await resp.json()
            self.context_id = data["context_id"]

    async def add_context(
        self,
        content: str,
        context_type: str = "observation",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add context to nuanced.dev with intelligent processing"""

        if not self.session:
            await self.initialize()

        payload = {
            "context_id": self.context_id,
            "content": content,
            "type": context_type,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }

        # Send to nuanced.dev for processing
        async with self.session.post(
            f"{self.config.api_url}/context/add",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            json=payload
        ) as resp:
            result = await resp.json()

            # Update local memory layers based on nuanced.dev's analysis
            self._update_memory_layers(result)

            return result

    def _update_memory_layers(self, nuanced_result: Dict):
        """Update memory layers based on nuanced.dev's analysis"""
        layer = nuanced_result.get("assigned_layer", "working")
        processed_content = nuanced_result.get("processed_content", {})

        if layer == "immediate":
            self.memory_layers["immediate"].append(processed_content)
            # Keep only last 10 immediate items
            self.memory_layers["immediate"] = self.memory_layers["immediate"][-10:]

        elif layer == "episodic":
            # Important events worth remembering
            self.memory_layers["episodic"].append(processed_content)

        elif layer == "semantic":
            # Patterns and knowledge
            self.memory_layers["semantic"].append(processed_content)

        else:  # working memory
            self.memory_layers["working"].append(processed_content)
            # Keep last 30 working items
            self.memory_layers["working"] = self.memory_layers["working"][-30:]

    async def get_relevant_context(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get relevant context using nuanced.dev's semantic search"""

        async with self.session.post(
            f"{self.config.api_url}/context/search",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            json={
                "context_id": self.context_id,
                "query": query,
                "max_results": max_results,
                "relevance_threshold": self.config.relevance_threshold
            }
        ) as resp:
            results = await resp.json()
            return results.get("relevant_contexts", [])

    async def compress_context(self) -> Dict[str, Any]:
        """Compress context using nuanced.dev's intelligent compression"""

        async with self.session.post(
            f"{self.config.api_url}/context/compress",
            headers={"Authorization": f"Bearer {self.config.api_key}"},
            json={
                "context_id": self.context_id,
                "compression_level": "intelligent",
                "preserve_important": True
            }
        ) as resp:
            return await resp.json()

    async def prepare_prompt_context(
        self,
        task: str,
        include_history: bool = True
    ) -> str:
        """Prepare optimized context for prompt"""

        # Get relevant context from nuanced.dev
        relevant = await self.get_relevant_context(task)

        # Build context string
        context_parts = []

        # Add immediate context
        if self.memory_layers["immediate"]:
            context_parts.append("## Current Context")
            for item in self.memory_layers["immediate"][-3:]:
                context_parts.append(f"- {item}")

        # Add relevant context from search
        if relevant:
            context_parts.append("\n## Relevant Information")
            for ctx in relevant[:5]:
                context_parts.append(f"- {ctx.get('content', '')}")

        # Add important episodic memories
        if self.memory_layers["episodic"]:
            context_parts.append("\n## Important Events")
            for event in self.memory_layers["episodic"][-3:]:
                context_parts.append(f"- {event}")

        return "\n".join(context_parts)

    async def export_session(self, filepath: str):
        """Export session data for analysis"""

        async with self.session.get(
            f"{self.config.api_url}/context/export/{self.context_id}",
            headers={"Authorization": f"Bearer {self.config.api_key}"}
        ) as resp:
            data = await resp.json()

        # Add local memory layers
        data["memory_layers"] = self.memory_layers

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    async def cleanup(self):
        """Clean up session"""
        if self.session:
            await self.session.close()


class HybridContextManager:
    """
    Hybrid approach combining nuanced.dev with local optimizations
    Falls back to local management if nuanced.dev is unavailable
    """

    def __init__(self, use_nuanced: bool = True):
        self.use_nuanced = use_nuanced and os.getenv("NUANCED_API_KEY")

        if self.use_nuanced:
            self.context_manager = NuancedContextManager()
        else:
            # Fallback to local context management
            self.context_manager = LocalContextManager()

    async def initialize(self):
        """Initialize context manager"""
        if hasattr(self.context_manager, 'initialize'):
            await self.context_manager.initialize()

    async def add_context(self, content: str, context_type: str = "observation", **kwargs):
        """Add context with automatic routing"""
        if self.use_nuanced:
            return await self.context_manager.add_context(content, context_type, **kwargs)
        else:
            return self.context_manager.add_context(content, context_type, **kwargs)

    async def get_context_for_task(self, task: str) -> str:
        """Get optimized context for a task"""
        if self.use_nuanced:
            return await self.context_manager.prepare_prompt_context(task)
        else:
            return self.context_manager.prepare_context(task)


class LocalContextManager:
    """Fallback local context manager using ripgrep-like search"""

    def __init__(self):
        self.contexts = []
        self.index = {}

    def add_context(self, content: str, context_type: str, **kwargs):
        """Add context locally with indexing"""
        context_id = hashlib.md5(content.encode()).hexdigest()[:8]

        entry = {
            "id": context_id,
            "content": content,
            "type": context_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": kwargs
        }

        self.contexts.append(entry)

        # Simple indexing for fast search
        words = content.lower().split()
        for word in words:
            if word not in self.index:
                self.index[word] = []
            self.index[word].append(context_id)

        return {"status": "added", "id": context_id}

    def search(self, query: str) -> List[Dict]:
        """Fast local search similar to ripgrep"""
        query_words = query.lower().split()
        matching_ids = set()

        for word in query_words:
            if word in self.index:
                matching_ids.update(self.index[word])

        results = []
        for ctx in self.contexts:
            if ctx["id"] in matching_ids:
                results.append(ctx)

        # Sort by recency
        results.sort(key=lambda x: x["timestamp"], reverse=True)

        return results[:10]

    def prepare_context(self, task: str) -> str:
        """Prepare context for task"""
        relevant = self.search(task)

        context_parts = ["## Relevant Context"]
        for ctx in relevant[:5]:
            context_parts.append(f"- {ctx['content'][:200]}...")

        # Add recent contexts
        context_parts.append("\n## Recent Actions")
        for ctx in self.contexts[-5:]:
            if ctx["type"] == "action":
                context_parts.append(f"- {ctx['content'][:100]}...")

        return "\n".join(context_parts)