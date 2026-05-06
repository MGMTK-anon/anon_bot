import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = "8684577150:AAEfo5PjQPX4hWu6soJr6zm2JQA8_kVkRHA"

ADMIN_GROUP_ID = -1005226802673
CHANNEL_ID = -1003838008372

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Отправь своё сообщение")

@dp.message()
async def handle_message(message: types.Message):
    user = message.from_user

    username = f"@{user.username}" if user.username else user.full_name
    text = message.text or "[не текст]"

    await bot.send_message(
        ADMIN_GROUP_ID,
        f"📩 Новое сообщение\n\nОт: {username}\n\n{text}"
    )

    await bot.send_message(
        CHANNEL_ID,
        text
    )

    await message.answer("Отправлено ✅")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
