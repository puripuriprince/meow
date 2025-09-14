#!/usr/bin/env python3
"""Push initial seed node to Redis frontier and fit UMAP reducer."""

import sys
import os
# Add parent directory to path so backend module can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.schemas import Node
from backend.core.utils import uuid_str
from backend.db.node_store import save
from backend.db.frontier import push
from backend.core.logger import get_logger
from backend.core.embeddings import fit_reducer, embed, to_xy

logger = get_logger(__name__)


def main():
    """Create and push root node, then fit reducer."""
    # Create root node with embedding
    root_prompt = "I noticed you seem a bit tense as you sit down. What brings you in today?"
    emb = embed(root_prompt)

    root = Node(
        id=uuid_str(),
        prompt=root_prompt,
        depth=0,
        score=1.0,
        emb=emb,
        xy=[0.0, 0.0],  # Will be updated after fitting reducer
    )

    # Save node and push to frontier
    save(root)
    push(root.id, 1.0)

    logger.info(f"Seeded root node {root.id} with prompt: {root.prompt}")
    print(f"Root node created: {root.id}")

    # Fit reducer on initial therapeutic prompts
    seed_prompts = [
        "I noticed you seem a bit tense as you sit down. What brings you in today?",
        "How are you feeling right now, in this moment?",
        "What's been on your mind lately?",
        "I'm curious about what drew you to therapy at this time.",
        "How has your week been since we last spoke?",
        "What would be most helpful for us to explore today?",
        "I notice you seem quiet today. What's that about?",
        "How are you experiencing our relationship right now?",
        "What feelings are coming up for you as we sit here?",
        "I'm wondering what it's like for you to be here with me.",
    ]

    fit_reducer(seed_prompts)
    logger.info("Fitted UMAP reducer on seed prompts")

    # Update root node with proper 2D projection
    xy = list(to_xy(emb))
    root.xy = xy
    save(root)

    print(f"UMAP reducer fitted, root node projected to xy=({xy[0]:.2f}, {xy[1]:.2f})")


if __name__ == "__main__":
    main()
