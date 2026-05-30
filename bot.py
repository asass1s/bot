import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 123456789  # <-- замени на свой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = {}          # user_id -> дата первого захода
confirmed = set()   # кто нажал "Я підписався"


# ---------- КНОПКИ ----------

def start_keyboard():
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="📢 Канал 1", url="https://t.me/channel1"))
    kb.add(InlineKeyboardButton(text="📢 Канал 2", url="https://t.me/channel2"))
    kb.add(InlineKeyboardButton(text="📢 Канал 3", url="https://t.me/channel3"))
    kb.add(InlineKeyboardButton(text="📢 Канал 4", url="https://t.me/channel4"))

    kb.add(
        InlineKeyboardButton(
            text="✅ Я підписався",
            callback_data="done"
        )
    )

    kb.adjust(1)
    return kb.as_markup()


def access_keyboard():
    kb = InlineKeyboardBuilder()

    kb.add(
        InlineKeyboardButton(
            text="🔥 Матеріали тут",
            url="https://t.me/ТВОЙ_КАНАЛ"
        )
    )

    kb.adjust(1)
    return kb.as_markup()


# ---------- START ----------

@dp.message(F.text.startswith("/start"))
async def start(message: Message):

    user = message.from_user
    user_id = user.id

    if user_id not in users:
        users[user_id] = datetime.now().strftime("%Y-%m-%d")

        try:
            await bot.send_message(
                ADMIN_ID,
                f"🟢 Новий користувач\n\n"
                f"ID: {user_id}\n"
                f"Ім'я: {user.first_name}\n"
                f"Username: @{user.username if user.username else 'none'}\n\n"
                f"Всього користувачів: {len(users)}"
            )
        except:
            pass

    await message.answer(
        "🔐 Доступ до матеріалів відкривається після підписки на канали нижче:",
        reply_markup=start_keyboard()
    )


# ---------- ЛЮБОЕ СООБЩЕНИЕ ДО ПОДТВЕРЖДЕНИЯ ----------

@dp.message()
async def reminder(message: Message):

    user_id = message.from_user.id

    if user_id in confirmed:
        return

    await message.answer(
        "⚠️ Спочатку завершіть активацію доступу.\n\n"
        "Підпишіться на канали та натисніть кнопку нижче:",
        reply_markup=start_keyboard()
    )


# ---------- ПОДТВЕРЖДЕНИЕ ----------

@dp.callback_query(F.data == "done")
async def done(callback: CallbackQuery):

    user_id = callback.from_user.id

    confirmed.add(user_id)

    await callback.message.answer(
        "✅ Доступ активовано!\n\n"
        "Натисніть кнопку нижче:",
        reply_markup=access_keyboard()
    )

    await callback.answer()


# ---------- СТАТИСТИКА ----------

@dp.message(F.text == "/stats")
async def stats(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    today_count = sum(1 for d in users.values() if d == today)

    await message.answer(
        f"📊 Статистика\n\n"
        f"Всього: {len(users)}\n"
        f"Сьогодні: {today_count}\n"
        f"Підтвердили доступ: {len(confirmed)}"
    )


# ---------- ЗАПУСК ----------

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
