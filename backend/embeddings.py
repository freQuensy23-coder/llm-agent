from pydantic import BaseModel
from typing import List
from loguru import logger
from google import genai
import time
from config import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE

# This will be populated on startup
all_param_embeddings: List['ParamEmbedding'] = []

class ParamEmbedding(BaseModel):
    param_name: str
    embedding: List[float]

def generate_embeddings(client: genai.Client, params_settings: list, embedding_model: str = EMBEDDING_MODEL, batch_size: int = EMBEDDING_BATCH_SIZE):
    """
    Generates and stores embeddings for all game parameters in batches.
    Should be called once on application startup.
    """
    global all_param_embeddings
    if all_param_embeddings:
        logger.info("Embeddings have already been generated.")
        return

    logger.info(f"Generating embeddings for {len(params_settings)} parameters in batches of {batch_size}...")
    
    descriptions = [p.description for p in params_settings]
    
    try:
        # Process descriptions in batches
        for i in range(0, len(descriptions), batch_size):
            batch_descriptions = descriptions[i:i + batch_size]
            batch_params = params_settings[i:i + batch_size]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(descriptions) + batch_size - 1)//batch_size} ({len(batch_descriptions)} items)")

            result = client.models.embed_content(
                model=embedding_model,
                contents=batch_descriptions,
            )
            time.sleep(0.25)

            assert result.embeddings is not None
            
            for j, param in enumerate(batch_params):
                embedding_values = result.embeddings[j].values
                if embedding_values:
                    all_param_embeddings.append(
                        ParamEmbedding(param_name=param.name, embedding=embedding_values)
                    )
        
        logger.info(f"Successfully generated {len(all_param_embeddings)} embeddings.")

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise e 