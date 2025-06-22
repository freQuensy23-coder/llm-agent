import asyncio
from loguru import logger

from main import generate, chat
from state import state
from tools import choose_game_type_tool, set_param_tool


async def main():
    logger.info("Starting CLI chat session...")
    while True:
        user_input = input('>: ')
        if not user_input:
            continue
        
        try:
            tools_to_use = [choose_game_type_tool, set_param_tool] if state.get('game_type') else [choose_game_type_tool]
            text, thoughts = await generate(chat, user_input, tools=tools_to_use)
            
            print("\n🤖 Assistant:" + "—" * 40)
            print(text)
            print("—" * 50)
            
        except Exception as e:
            logger.error(f"An error occurred: {e}")


if __name__ == '__main__':
    asyncio.run(main())