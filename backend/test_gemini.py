import asyncio
from app.services.llm import get_gemini_client
import sys
import logging

logging.basicConfig(level=logging.INFO)

async def test():
    try:
        gemini = get_gemini_client()
        res = await gemini.chat_json([{'role': 'user', 'content': 'output strict JSON { "hello": "world" }'}])
        print('SUCCESS:', res)
    except Exception as e:
        print('ERROR TYPE:', type(e))
        print('ERROR MSG:', str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

asyncio.run(test())
