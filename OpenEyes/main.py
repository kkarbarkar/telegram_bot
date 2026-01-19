import asyncio
from aiogram import Bot, Dispatcher, Router

from handlers import start, registration, info, events, admin
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(info.router)
    dp.include_router(events.router)
    dp.include_router(admin.router)
    print("Бот включен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
