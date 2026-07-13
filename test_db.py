import asyncio
from app.database import engine


async def test():
    async with engine.connect() as conn:
        print("DB ulanishi muvaffaqiyatli!")


asyncio.run(test())