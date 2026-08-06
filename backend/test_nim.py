import asyncio
from app.services.llm import get_nim_client

async def test():
    nim = get_nim_client()
    try:
        res = await nim.chat_json([{'role': 'user', 'content': 'output { "hello": "world" }'}])
        print('SUCCESS:', res)
    except Exception as e:
        print('ERROR TYPE:', type(e))
        print('ERROR MSG:', str(e))
        import traceback
        traceback.print_exc()

asyncio.run(test())
