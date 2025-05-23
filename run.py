import aiogram
import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.handlers import router
from database.models import async_main

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))

async def main():
    await async_main()
    dp = Dispatcher()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Бот отключен.')
