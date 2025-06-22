from typing import Any, Tuple, AsyncIterator
from game_context import params_settings, GameType
from state import state
import numpy as np
from google import genai
from typing import List
from google.genai.chats import AsyncChat
from google.genai.types import GenerateContentConfig, ThinkingConfig, Part
from loguru import logger
from config import EMBEDDING_MODEL

def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False

def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False
    

def is_numerical(value: str) -> bool:
    """Check if a string is numerical (int or float)."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def filter_params(params: dict, game_type: GameType) -> Tuple[dict, dict]:
    """Filter parameters by game type."""
    new_params = {}
    filtered_params = {}
    for key, value in params.items():
        if key in [p.name for p in params_settings if p.apply_to == game_type]:
            new_params[key] = value
        else:
            filtered_params[key] = value
    return new_params, filtered_params


def get_current_game_state(current_state: dict) -> dict:
    """Return the current game state."""
    game_mode = current_state.get('game_type')
    if not game_mode:
        return {"game_mode": None, "params": []}

    current_params = current_state.get('game_params', {})
    
    applicable_params = [p for p in params_settings if p.apply_to == game_mode]
    
    params_list = []
    for param_setting in applicable_params:
        param_name = param_setting.name
        value = current_params.get(param_name, param_setting.default_value)
        source = 'ai' if param_name in current_params else 'default'
        
        params_list.append({
            "name": param_name,
            "description": param_setting.description,
            "value": value,
            "source": source
        })

    return {
        "game_mode": game_mode,
        "params": params_list
    }

def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_query_embeddings(queries: List[str]) -> List[List[float]]:
    """Generate embeddings for query strings using the same logic as generate_embeddings."""
    client = genai.Client()
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=queries  # type: ignore
    )
    assert result.embeddings is not None
    
    query_embeddings = []
    for embedding in result.embeddings:
        if embedding.values:
            query_embeddings.append(embedding.values)
    
    return query_embeddings

async def generate_parts(current_chat: AsyncChat, prompt: str, **kwargs) -> AsyncIterator[Tuple[str, bool]]:
    """
    Yields parts of the model's response based on the original CLI logic.
    Returns a tuple of (text, is_thinking).
    """
    system_prompt_message = ""
    if len(current_chat._comprehensive_history) == 1 and current_chat._comprehensive_history[0].role == "user":
        system_prompt_message = ''.join([part.text for part in current_chat._comprehensive_history[0].parts])

    cfg = GenerateContentConfig(thinking_config=ThinkingConfig(include_thoughts=True), **kwargs)
    
    combined_prompt = f"{system_prompt_message}\\n{prompt}"
    stream = await current_chat.send_message_stream(combined_prompt, config=cfg)

    async for chunk in stream:
        if not (chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts):
            continue

        for part in chunk.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                tool_log = f"\\n\\n🤖 TOOL CALL: {part.function_call.name}({part.function_call.args})\\n"
                logger.info(f"🔧: {part.function_call}")
                yield tool_log, True

            if hasattr(part, 'text') and part.text:
                is_thinking = hasattr(part, 'thought') and part.thought is not None
                if is_thinking:
                    logger.debug(f"🤔: {part.text}")
                yield part.text, is_thinking

async def generate(current_chat: AsyncChat, prompt: str, **kwargs) -> tuple[str, str]:
    final_response = ''
    thoughts_and_tools = ''
    
    logger.info(f"User: {prompt}")
    
    async for part, is_thinking in generate_parts(current_chat, prompt, **kwargs):
        if is_thinking:
            thoughts_and_tools += part
        else:
            final_response += part
            
    return final_response, thoughts_and_tools