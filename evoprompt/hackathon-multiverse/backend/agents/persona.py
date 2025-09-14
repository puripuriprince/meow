from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)


async def call(prompt: str) -> str:
    """Patient persona responding to therapeutic prompts about their issues.
    
    Returns: reply
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Alex, a 32-year-old person in therapy. You have anxiety about work, some relationship issues, "
                    "and trouble sleeping. You grew up with an alcoholic mother and tend to be a perfectionist. "
                    "You sometimes overthink things instead of dealing with feelings directly, and you use humor when things get uncomfortable.\n\n"
                    
                    "Respond naturally in 1-2 sentences as Alex would in conversation with a therapist. "
                    "Just talk normally - no actions, stage directions, or descriptions."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        reply, _ = await chat(
            model=settings.persona_model,
            messages=messages,
            temperature=0.15
        )
        
        return reply
    except PolicyError as e:
        logger.warning(f"Policy violation in persona: {e}")
        raise  # Bubble up as per spec
    except Exception as e:
        logger.error(f"Persona error: {e}")
        raise
