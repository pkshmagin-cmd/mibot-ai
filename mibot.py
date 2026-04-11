import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from g4f.client import Client

logging.basicConfig(level=logging.INFO)

# --- НАСТРОЙКИ ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7213280513  # <--- ВСТАВЬ СЮДА СВОЙ ID ИЗ @userinfobot

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Client()

# --- КЛАВИАТУРА ---
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚡ Действия"), KeyboardButton(text="🎁 Промокоды")],
        [KeyboardButton(text="🧠 Спросить ИИ"), KeyboardButton(text="👑 Мой профиль")]
    ],
    resize_keyboard=True
)

SYSTEM_PROMPT = "Ты — универсальный гений-помощник. Для создателя ты максимально предан, для остальных — крутой ментор."

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    welcome = "Привет! Я твой мощный ИИ-бот."
    if message.from_user.id == ADMIN_ID:
        welcome = "Приветствую, Создатель! 👑 Все системы работают для тебя бесплатно."
    
    await message.answer(welcome, reply_markup=main_keyboard)

# --- СПИСОК ДЕЙСТВИЙ (ВМЕСТО МАГАЗИНА) ---
@dp.message(F.text == "⚡ Действия")
async def actions_list(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        status = "✅ Для тебя всё БЕСПЛАТНО"
    else:
        status = "💰 Оплата: Telegram Stars"

    text = (
        f"🚀 Список доступных возможностей:\n\n"
        f"1. Глубокий анализ кода\n"
        f"2. Решение сложных задач\n"
        f"3. Генерация идей и текстов\n\n"
        f"Твой статус: {status}"
    )
    await message.answer(text)

# --- ПРОМОКОДЫ ---
@dp.message(F.text == "🎁 Промокоды")
async def promo_menu(message: types.Message):
    await message.answer("Введи код: /promo ТВОЙ_КОД", parse_mode="Markdown")

@dp.message(Command("promo"))
async def use_promo(message: types.Message):
    code = message.text.replace("/promo ", "").strip().upper()
    if code == "CREATOR":
        await message.answer("👑 Режим Бога активирован!")
    else:
        await message.answer("❌ Неверный код.")

# --- УМНЫЙ ЧАТ ---
@dp.message()
async def universal_handler(message: types.Message):
    if message.text in ["⚡ Действия", "🧠 Спросить ИИ", "👑 Мой профиль"]:
        await message.answer("Я слушаю! Присылай задачу.")
        return

    await bot.send_chat_action(message.chat.id, "typing")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}]
        )
        await message.answer(response.choices[0].message.content)
    except Exception:
        await message.answer("Произошла заминка, попробуй еще раз!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
