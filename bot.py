import asyncio
import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

TOKEN = "8684577150:AAEfo5PjQPX4hWu6soJr6zm2JQA8_kVkRHA"

ADMIN_GROUP_ID = -1003783517039
CHANNEL_ID = -1003838008372

CHANNEL_USERNAME = "mgmtk_anon"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# антиспам
user_last_message = {}

# минимум символов
MIN_TEXT_LENGTH = 10

# кулдаун антиспама (сек)
SPAM_COOLDOWN = 10


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
        "✉️ Отправь своё сообщение"
    )


@dp.message()
async def handle_message(message: types.Message):

    user_id = message.from_user.id

    # ---------------- ПОДПИСКА ----------------
    subscribed = await is_subscribed(user_id)

    if not subscribed:
        await message.answer(
            f"❌ Вы должны быть подписаны на канал"
        )
        return

    # ---------------- АНТИСПАМ ----------------
    current_time = time.time()

    if user_id in user_last_message:
        last_time = user_last_message[user_id]

        if current_time - last_time < SPAM_COOLDOWN:
            await message.answer(
                "⏳ Не спамь. Подожди немного."
            )
            return

    user_last_message[user_id] = current_time

    # ---------------- ДАННЫЕ ЮЗЕРА ----------------
    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else user.full_name
    )

    caption = message.caption or ""
    text = message.text or caption

# ---------------- МИНИМУМ 5 СИМВОЛОВ ----------------
# Только для обычного текста

if message.text:
    if len(text.strip()) < MIN_TEXT_LENGTH:
        await message.answer(
            "❌ Минимум 5 символов"
        )
        return

    # ---------------- АДМИН ГРУППА ----------------

    admin_text = (
        f"📩 Новое сообщение\n\n"
        f"От: {username}\n\n"
        f"{text}"
    )

    # Текст
    if message.text:
        await bot.send_message(
            ADMIN_GROUP_ID,
            admin_text
        )

        await bot.send_message(
            CHANNEL_ID,
            text
        )

    # Фото
    elif message.photo:
        photo = message.photo[-1].file_id

        await bot.send_photo(
            ADMIN_GROUP_ID,
            photo,
            caption=admin_text
        )

        await bot.send_photo(
            CHANNEL_ID,
            photo,
            caption=caption
        )

    # Видео
    elif message.video:
        await bot.send_video(
            ADMIN_GROUP_ID,
            message.video.file_id,
            caption=admin_text
        )

        await bot.send_video(
            CHANNEL_ID,
            message.video.file_id,
            caption=caption
        )

    # Голосовое
    elif message.voice:
        await bot.send_voice(
            ADMIN_GROUP_ID,
            message.voice.file_id,
            caption=f"🎤 ГС от {username}"
        )

        await bot.send_voice(
            CHANNEL_ID,
            message.voice.file_id
        )

    # Кружочек
    elif message.video_note:
        await bot.send_message(
            ADMIN_GROUP_ID,
            f"📹 Кружочек от {username}"
        )

        await bot.send_video_note(
            ADMIN_GROUP_ID,
            message.video_note.file_id
        )

        await bot.send_video_note(
            CHANNEL_ID,
            message.video_note.file_id
        )

    # Гифка
elif message.animation:
    await bot.send_animation(
        ADMIN_GROUP_ID,
        message.animation.file_id,
        caption=f"🎞 Гифка от {username}\n\n{caption}"
    )

    await bot.send_animation(
        CHANNEL_ID,
        message.animation.file_id,
        caption=caption
    )

    else:
        await message.answer(
            "❌ Этот тип файла не поддерживается"
        )
        return

    await message.answer(
        "✅ Сообщение успешно отправлено"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
