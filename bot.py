import asyncio
import time
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

TOKEN = "8684577150:AAEfo5PjQPX4hWu6soJr6zm2JQA8_kVkRHA"

ADMIN_GROUP_ID = -1003783517039
CHANNEL_ID = -1003838008372

CHANNEL_USERNAME = "@mgmtk_anon"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# антиспам
user_last_message = {}

# минимум символов для текста
MIN_TEXT_LENGTH = 10

# кулдаун антиспама
SPAM_COOLDOWN = 10

# regex для ссылок
LINK_REGEX = r"(https?:\/\/|www\.|t\.me\/|telegram\.me\/)"


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
        else f'<a href="tg://user?id={user.id}">Профиль пользователя</a>'
    )

    caption = message.caption or ""
    text = message.text or caption

    # ---------------- ЗАПРЕТ ССЫЛОК ----------------

    if re.search(LINK_REGEX, text.lower()):

        await message.answer(
            "❌ Ссылки запрещены"
        )
        return

    admin_text = (
        f"📩 Новое сообщение\n\n"
        f"От: {username}\n\n"
        f"{text}"
    )

    # ---------------- МИНИМУМ СИМВОЛОВ ----------------
    # только для текста

    if message.text:

        if len(text.strip()) < MIN_TEXT_LENGTH:

            await message.answer(
                f"❌ Минимум {MIN_TEXT_LENGTH} символов"
            )
            return

    # ---------------- ТЕКСТ ----------------

    if message.text:

        await bot.send_message(
            ADMIN_GROUP_ID,
            admin_text,
            parse_mode="HTML"
        )

        await bot.send_message(
            CHANNEL_ID,
            text
        )

    # ---------------- ФОТО ----------------

    elif message.photo:

        photo = message.photo[-1].file_id

        await bot.send_photo(
            ADMIN_GROUP_ID,
            photo,
            caption=admin_text,
            parse_mode="HTML"
        )

        await bot.send_photo(
            CHANNEL_ID,
            photo,
            caption=caption
        )

    # ---------------- ВИДЕО ----------------

    elif message.video:

        await bot.send_video(
            ADMIN_GROUP_ID,
            message.video.file_id,
            caption=admin_text,
            parse_mode="HTML"
        )

        await bot.send_video(
            CHANNEL_ID,
            message.video.file_id,
            caption=caption
        )

    # ---------------- ГИФКА ----------------

    elif message.animation:

        await bot.send_animation(
            ADMIN_GROUP_ID,
            message.animation.file_id,
            caption=f"🎞 Гифка от {username}\n\n{caption}",
            parse_mode="HTML"
        )

        await bot.send_animation(
            CHANNEL_ID,
            message.animation.file_id,
            caption=caption
        )

    # ---------------- ГОЛОСОВОЕ ----------------

    elif message.voice:

        await bot.send_message(
            ADMIN_GROUP_ID,
            f"🎤 ГС от {username}",
            parse_mode="HTML"
        )

        await bot.send_voice(
            ADMIN_GROUP_ID,
            message.voice.file_id
        )

        await bot.send_voice(
            CHANNEL_ID,
            message.voice.file_id
        )

    # ---------------- КРУЖОЧЕК ----------------

    elif message.video_note:

        await bot.send_message(
            ADMIN_GROUP_ID,
            f"📹 Кружочек от {username}",
            parse_mode="HTML"
        )

        await bot.send_video_note(
            ADMIN_GROUP_ID,
            message.video_note.file_id
        )

        await bot.send_video_note(
            CHANNEL_ID,
            message.video_note.file_id
        )

    # ---------------- НЕПОДДЕРЖИВАЕМЫЙ ТИП ----------------

    else:

        await message.answer(
            "❌ Этот тип файла не поддерживается"
        )
        return

    # ---------------- УСПЕХ ----------------

    await message.answer(
        "✅ Сообщение успешно отправлено"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
