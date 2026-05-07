import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

TOKEN = "8684577150:AAEfo5PjQPX4hWu6soJr6zm2JQA8_kVkRHA"

ADMIN_GROUP_ID = -1003783517039
CHANNEL_ID = -1003838008372

# username канала
CHANNEL_USERNAME = "@mgmtk_anon"

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)

        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except:
        return False


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Отправь своё сообщение ✉️"
    )


@dp.message()
async def handle_message(message: types.Message):

    # проверка подписки
    subscribed = await is_subscribed(message.from_user.id)

    if not subscribed:
        await message.answer(
            f"❌ Чтобы отправлять сообщения, подпишись на канал {CHANNEL_USERNAME}"
        )
        return

    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else user.full_name
    )

    text = message.text or "[не текст]"

    # в группу админов
    await bot.send_message(
        ADMIN_GROUP_ID,
        f"📩 Новое сообщение\n\nОт: {username}\n\n{text}"
    )

    # в канал анонимно
    await bot.send_message(
        CHANNEL_ID,
        text
    )

    await message.answer(
        "✅ Сообщение успешно отправлено"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
