import json
from typing import Literal, Optional
from pydantic import BaseModel
from pathlib import Path

GAME_TYPES = ('shooter', 'platformer', 'rpg', 'runner', 'puzzle')
GameType = Literal['shooter', 'platformer', 'rpg', 'runner', 'puzzle']

class GameParameter[T](BaseModel):
    name: str
    description: str
    min_value: T
    max_value: T
    reccomended_min_value: T
    reccomended_max_value: T
    default_value: T
    apply_to: GameType


# Construct path relative to this file
params_path = Path(__file__).parent / "params.json"

with open(params_path, 'r') as f:
    params_dicts: list[dict] = json.load(f)

params_settings: list[GameParameter] = [GameParameter(**param_dict) for param_dict in params_dicts]


