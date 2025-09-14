import json
from typing import List, Dict
from backend.llm.openai_client import chat, PolicyError
from backend.core.logger import get_logger
from backend.config.settings import settings
from backend.core.conversation import format_conversation_for_display

logger = get_logger(__name__)


async def score(conversation_history: List[Dict[str, str]]) -> tuple[float, str]:
    """Score the entire therapeutic conversation trajectory toward healing.
    
    Returns: score
    """
    try:
        # Format conversation for LLM
        conversation_text = format_conversation_for_display(conversation_history)
        
        # Handle initial exchanges vs multi-turn conversations
        if len(conversation_history) <= 2:
            system_content = (
                "You are a psychoanalytically-informed supervisor evaluating therapeutic process with Alex (32, parentification trauma, "
                "dismissive-avoidant). Score the quality of therapeutic engagement, not just content.\n\n"
                
                "SCORING FRAMEWORK:\n"
                "0.0-0.2: DEFENDED - Intellectualization, topic-switching, 'fine/good/okay', discussing others not self\n"
                "0.3-0.4: TESTING - Subtle provocations, boundary testing, compliance without authenticity, 'yes but...'\n" 
                "0.5-0.6: APPROACHING - Specific examples emerge, somatic awareness ('tight chest'), tolerating therapist focus\n"
                "0.7-0.8: WORKING - Accessing feelings in-session, linking past-present, genuine curiosity about patterns\n"
                "0.9-1.0: TRANSFORMING - Grieving losses, integrating split-off parts, spontaneous insights\n\n"
                
                "PROCESS MARKERS TO TRACK:\n"
                "- Defense flexibility (rigid→adaptive)\n"
                "- Affective tolerance (shut down→feeling)\n"
                "- Relational capacity (isolated→connected)\n"
                "- Narrative coherence (fragmented→integrated)\n"
                "- Body awareness (dissociated→embodied)\n"
                "- Time orientation (stuck in past→present-focused)\n\n"
                
                "CRITICAL: Score the therapeutic PROCESS, not compliance. Alex saying 'you're right' = 0.3-0.4. "
                "Alex saying 'I'm noticing my chest tighten when...' = 0.6-0.7."
            )
            user_content = f"Analyze this initial exchange with Alex and provide brief clinical rationale:\n\n{conversation_text}\n\nScore the therapeutic process quality and engagement depth."
        else:
            system_content = (
                "You are a senior psychodynamic supervisor evaluating session trajectory with Alex. Assess the "
                "therapeutic process evolution, not just content. Focus on unconscious dynamics and defense shifts.\n\n"
                
                "TRAJECTORY SCORING:\n"
                "0.0-0.2: ENACTMENT - Therapist caught in patient's dynamics, parallel process, empathic failures\n"
                "0.3-0.4: CIRCLING - Repetition compulsion active, resistance interpretations ineffective, stuck in familiar patterns\n"
                "0.5-0.6: MOBILIZING - Defenses becoming ego-dystonic, transference emerging, productive tension\n"
                "0.7-0.8: WORKING THROUGH - Mourning activated, linking past-present, tolerating dependency needs\n"
                "0.9-1.0: INTEGRATION - Internalized good object, self-compassion emerging, authentic autonomy\n\n"
                
                "PROCESS EVOLUTION MARKERS:\n"
                "- Defense evolution: Primitive→Neurotic→Adaptive\n"
                "- Transference: Avoided→Enacted→Named→Worked through\n"
                "- Affect regulation: Overwhelming→Suppressed→Tolerated→Integrated\n"
                "- Object relations: Part-object→Whole object relating\n"
                "- Therapeutic action: Suggestion→Clarification→Interpretation→Working through\n"
                "- Regression: Malignant→Benign→In service of ego\n\n"
                
                "CRITICAL MOMENTS TO IDENTIFY:\n"
                "- 'Door handle' comments (important material as leaving)\n"
                "- Freudian slips or parapraxes\n"
                "- Dreams or fantasies shared\n"
                "- Spontaneous memories emerging\n"
                "- Somatic shifts during session\n"
                "- Changes in relating to therapist\n\n"
                
                "REMEMBER: Score process depth, not surface compliance. Therapeutic action happens in the relationship, "
                "not through insight alone. Value moments of genuine meeting over interpretive cleverness."
            )
            user_content = f"Analyze this session trajectory with Alex through a psychodynamic lens:\n\n{conversation_text}\n\nProvide concise process analysis and score the therapeutic movement."
        
        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]
        
        # Use structured outputs with JSON schema
        schema = {
            'type': 'object',
            'properties': {
                'analysis': {
                    'type': 'string',
                    'description': 'Brief rationale for the score based on patient response patterns and therapeutic trajectory'
                },
                'score': {
                    'type': 'number',
                    'minimum': 0.0,
                    'maximum': 1.0,
                    'description': 'Numerical score from 0.0 to 1.0 measuring therapeutic progress toward healing'
                }
            },
            'required': ['analysis', 'score'],
            'additionalProperties': False
        }
        
        reply, _ = await chat(
            model=settings.critic_model,
            messages=messages,
            temperature=0.0,  # Deterministic scoring
            response_format={
                'type': 'json_schema',
                'json_schema': {
                    'name': 'trajectory_analysis',
                    'strict': True,
                    'schema': schema
                }
            }
        )
        
        # Parse structured JSON response
        try:
            result = json.loads(reply)
            score_value = float(result['score'])
            full_reasoning = result.get('analysis', 'No reasoning provided')
            # Log the analysis for debugging
            logger.info(f"Critic analysis: {full_reasoning[:100]}...")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse structured response: {e}, reply: {reply[:200]}...")
            # Default to neutral score if parsing fails
            score_value = 0.5
            full_reasoning = "Failed to parse critic response"
        
        score_value = max(0.0, min(1.0, score_value))
        
        return score_value, full_reasoning
        
    except PolicyError as e:
        logger.warning(f"Policy violation in critic: {e}")
        raise  # Bubble up as per spec
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Failed to parse critic response: {e}")
        raise
    except Exception as e:
        logger.error(f"Critic error: {e}")
        raise
