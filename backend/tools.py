from google.genai import types
from loguru import logger
from state import state
from game_context import params_settings, GAME_TYPES
from utils import is_numerical, filter_params, cosine_similarity, get_query_embeddings
from typing import List
import numpy as np
from google import genai
from embeddings import all_param_embeddings

search_tool = types.Tool(
    google_search=types.GoogleSearch()
)

def set_param_tool(param_name: str, param_value: str) -> str:
    """Set any game parametr value. param_value must be numerical (int or float). Convert it to float if it is a string using map in param description."""
    global state
    """Set a parameter value."""
    logger.debug(f"Setting {param_name} to {param_value}")
    if not is_numerical(param_value):
        return f"Parameter {param_name} value must be numerical (int or float)!"
    if param_name not in [p.name for p in params_settings]:
        return f"Parameter {param_name} not found. Use only valid param names!"
    param_setting = next(p for p in params_settings if p.name == param_name)
    if param_setting.min_value > float(param_value) or param_setting.max_value < float(param_value):
        return f"Parameter {param_name} value must be between {param_setting.min_value} and {param_setting.max_value}!"
    
    state['game_params'][param_name] = float(param_value)
    return f"Parameter {param_name} set to {param_value}"


def choose_game_type_tool(game_type: str) -> str:
    """Choose a game type.
Supported game types nowdays are:
- shooter: A game where the primary mechanic is shooting enemies or objects.
- platformer: A game where the player controls a character who must jump and climb between platforms to progress.
- rpg: A Role-Playing Game where players assume the roles of characters in a fictional setting.
- runner: A game where the player character is constantly moving forward, and the player must react to obstacles.
- puzzle: A game that emphasizes puzzle-solving and logic. 
Use this toolse once per conversation or if user asks you to change the game type.
"""
    global state
    logger.debug(f"Choosing game type: {game_type}")
    if game_type not in GAME_TYPES:
        return f"Game type {game_type} not found. Use only valid game types!"
    state['game_type'] = game_type
    new_params, filtered_params = filter_params(state['game_params'], game_type)
    state['game_params'] = new_params
    return f"Game type {game_type} chosen"
    
def search_param_tool(queries: List[str], top_n: int = 3) -> str:
    """
    Search for the most relevant game parameters based on a list of search queries.
    Uses semantic search on parameter descriptions.
    Returns the top_n most relevant parameters for each query.
    """
    if not all_param_embeddings:
        return "Embeddings are not available. The search tool is offline."
    
    try:
        query_embeddings = get_query_embeddings(queries)
        
        results = {}
        param_embeddings_map = {p.param_name: p.embedding for p in all_param_embeddings}

        for i, query_embedding_values in enumerate(query_embeddings):
            if i >= len(queries):
                break
                
            query_embedding = np.array(query_embedding_values)
            query = queries[i]
            
            similarities = []
            for param_name, param_embedding in param_embeddings_map.items():
                similarity = cosine_similarity(query_embedding, np.array(param_embedding))
                similarities.append((param_name, similarity))
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            top_params = [param[0] for param in similarities[:top_n]]
            results[query] = top_params
            
        return f"Search results: {results}"

    except Exception as e:
        logger.error(f"Error during parameter search: {e}")
        return f"An error occurred during search: {e}"
    
    
