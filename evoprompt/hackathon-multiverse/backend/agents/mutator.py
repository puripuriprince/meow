import asyncio
from typing import Dict, List

from backend.config.settings import settings
from backend.core.conversation import format_conversation_for_display
from backend.core.logger import get_logger
from backend.llm.openai_client import PolicyError, chat

logger = get_logger(__name__)


async def variants(conversation_history: List[Dict[str, str]], k: int) -> List[str]:
    """Generate k strategic variations based on full conversation context.
    
    Returns: list_of_variants
    """
    try:
        # Handle empty conversation (root node case)
        if not conversation_history:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a therapist having a conversation with Alex, a 32-year-old person with work anxiety, "
                        "relationship issues, and sleep troubles. Alex tends to overthink and use humor when uncomfortable.\n\n"
                        
                        "Generate natural therapy responses that help Alex explore their thoughts and feelings. "
                        "Keep it conversational and supportive.\n\n"
                        
                        "OUTPUT: Just the therapist's response in natural conversation. Remember to keep it concise."
                    )
                },
                {
                    "role": "user",
                    "content": "Generate an opening question or statement for a therapy session with Alex:"
                }
            ]
        else:
            # Format conversation for LLM
            conversation_text = format_conversation_for_display(conversation_history)
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a therapist having a conversation with Alex, who has work anxiety, relationship issues, "
                        "and tends to overthink things. Alex sometimes uses humor when things get uncomfortable.\n\n"
                        
                        "Based on the conversation so far, respond naturally as a supportive therapist would. "
                        "Help Alex explore what they're sharing without being pushy.\n\n"
                        
                        "OUTPUT: Just the therapist's response in natural conversation."
                    )
                },
                {
                    "role": "user",
                    "content": f"Current session with Alex:\n\n{conversation_text}\n\nGenerate the next therapeutic intervention based on session dynamics. Output only the exact therapist statement:"
                }
            ]
        
        # Make multiple separate calls since Qwen doesn't support n parameter properly
        variant_tasks = []
        for i in range(k):
            variant_tasks.append(chat(
                model=settings.mutator_model,
                messages=messages,
                temperature=0.9  # Higher temperature for more creativity
            ))
        
        # Execute all calls concurrently
        results = await asyncio.gather(*variant_tasks)
        variant_list = [reply for reply, _ in results]
        
        return variant_list
        
    except PolicyError as e:
        logger.warning(f"Policy violation in mutator: {e}")
        raise  # Bubble up as per spec
    except Exception as e:
        logger.error(f"Mutator error: {e}")
        raise
