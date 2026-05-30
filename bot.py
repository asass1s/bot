import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8401605572  # <-- вставь свой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = {}  # user_id: first_date


# ---------------- KEYBOARDS ----------------

def start_keyboard():
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="📢 Канал 1", url="https://t.me/+o5RAvVlVDCwzYmRk"))
    kb.add(InlineKeyboardButton(text="📢 Канал 2", url="https://t.me/+UNTJxMzGg6E2MTU6"))
    kb.add(InlineKeyboardButton(text="📢 Канал 3", url="https://t.me/+_WAO39LmkNIwM2I6"))
   

    kb.add(InlineKeyboardButton(text="✅ Я підписався", callback_data="done"))

    kb.adjust(1)
    return kb.as_markup()


def access_keyboard():
    kb = InlineKeyboardBuilder()

    kb.add(
        InlineKeyboardButton(
            text="🔥 Матеріали тут",
            url="https://t.me/+o5RAvVlVDCwzYmRk"
        )
    )

    kb.adjust(1)
    return kb.as_markup()


# ---------------- START FLOW ----------------

@dp.message(F.text.startswith("/start"))
async def start(message: Message):
    user = message.from_user
    user_id = user.id

    # фиксируем пользователя
    if user_id not in users:
        users[user_id] = datetime.now().strftime("%Y-%m-%d")

        # уведомление тебе
        await bot.send_message(
            ADMIN_ID,
            f"🟢 Новый пользователь\n"
            f"ID: {user_id}\n"
            f"Имя: {user.first_name}\n"
            f"Username: @{user.username if user.username else 'none'}\n"
            f"Всего пользователей: {len(users)}"
        )

    await message.answer(
        "🔐 Доступ відкривається після підписки на канали:",
        reply_markup=start_keyboard()
    )


# ---------------- CONFIRM ----------------

@dp.callback_query(F.data == "done")
async def done(callback: CallbackQuery):

    await callback.message.answer(
        "✅ Підписку прийнято\n"
        "Ось матеріали:",
        reply_markup=access_keyboard()
    )

    await callback.answer()


# ---------------- STATS ----------------

@dp.message(F.text == "/stats")
async def stats(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    today_count = sum(1 for d in users.values() if d == today)

    await message.answer(
        f"📊 Статистика\n\n"
        f"Всього: {len(users)}\n"
        f"Сьогодні: {today_count}"
    )


# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())