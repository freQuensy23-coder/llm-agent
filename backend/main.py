# backend/main.py
"""
FastAPI wrapper around your Gemini chat loop.
• One global AsyncChat instance → exactly one concurrent user.
• POST /chat  { "message": str }  →  { "response": str }
"""
import os
from typing import Union, Callable
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai.chats import AsyncChat
from google.genai.types import Content, Part, Tool, FunctionDeclaration
from loguru import logger
import traceback

from tools import choose_game_type_tool, set_param_tool, search_param_tool
from state import state
from game_context import params_settings
from utils import get_current_game_state, generate
from embeddings import generate_embeddings
from config import CHAT_MODEL, CORS_ORIGINS

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize embeddings on startup
generate_embeddings(client, params_settings)

# Construct path relative to this file
system_prompt_path = Path(__file__).parent / "system_prompt.md"

# → history starts with your system prompt
chat: AsyncChat = client.aio.chats.create(
    model=CHAT_MODEL,
    history=[Content(
        role="user",
        parts=[Part(text=open(system_prompt_path).read())]
    )]
)

# ──────────────────────────────────────────────── #
#  FastAPI     (uvicorn main:app --reload)
# ──────────────────────────────────────────────── #
app = FastAPI(title="Gemini-Game-Config Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Msg(BaseModel):
    message: str

class ChatResp(BaseModel):
    response: str
    thoughts: str

@app.get("/state")
async def get_state_endpoint():
    return get_current_game_state(state)

@app.post("/chat", response_model=ChatResp)
async def chat_endpoint(msg: Msg):
    try:
        tools_to_use: list[Union[Callable, Tool]] = [
            choose_game_type_tool,
            search_param_tool
        ]
        game_type = state.get('game_type')
        if game_type:
            available_params = [p for p in params_settings if p.apply_to == game_type]
            
            param_descriptions = "\\n".join([
                f"- {p.name}: {p.description} (min: {p.min_value}, max: {p.max_value})"
                for p in available_params
            ])
            
            set_param_tool.__doc__ = f"""Set any game parameter value. param_value must be numerical (int or float).
Available parameters for game type '{game_type}':
{param_descriptions}
"""
            tools_to_use.append(set_param_tool)

        answer, thoughts = await generate(chat, msg.message, tools=tools_to_use)
        return ChatResp(response=answer, thoughts=thoughts)
    except Exception as e:
        logger.error(f"Error during chat generation: {e}\\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))