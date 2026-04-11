import os
import asyncio
import logging
import random
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton, 
    LabeledPrice, PreCheckoutQuery
)
import g4f
from g4f.client import Client

# --- НАСТРОЙКИ ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7213280513 

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Client()

# --- МЕНЮ ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 МАГАЗИН"), KeyboardButton(text="🎁 ПРОМОКОД")],
        [KeyboardButton(text="🌟 ДОНАТ"), KeyboardButton(text="👤 ПРОФИЛЬ")]
    ],
    resize_keyboard=True
)

# --- БАЗА ПРОМОКОДОВ ---
PROMO_CODES = {
    "GEMINI2026": "💎 VIP-статус и доступ к ядру Ultra активированы!",
    "POVAR": "👨‍🍳 Секретный бонус от Повара: Безлимит на 24 часа!",
    "START": "🎁 Приветственный бонус: +100 баллов в системе.",
    "GITHUB": "🌐 Серверная поддержка активирована!",
    "ADMIN_POWER": "👑 Режим Создателя: Все модули открыты.",
    "PISTON": "🚀 Поршни заведены: Скорость ответов MAX.",
    "FREE_MOD": "🧪 Платный модуль 'Генератор' теперь доступен бесплатно."
}

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start(message: types.Message):
    status = "👑 GOD MODE" if message.from_user.id == ADMIN_ID else "USER"
    await message.answer(
        f"🌌 GEMINI-X ULTIMATE v10.0\n\nСтатус: {status}\nЗащита 404: АКТИВНА ✅\n\nСистема готова. Введите промокод или спросите ИИ о чем угодно.",
        reply_markup=main_kb,
        parse_mode="Markdown"
    )

@dp.message(F.text == "💎 МАГАЗИН")
async def shop(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧬 Модуль ULTRA", callback_data="buy_ok")],
        [InlineKeyboardButton(text="💻 Режим Кодера", callback_data="buy_ok")]
    ])
    await message.answer("🏪 БЕЗОПАСНЫЙ МАГАЗИН (No-404)", reply_markup=kb)

@dp.callback_query(F.data == "buy_ok")
async def buy_ok(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.answer("✨ Доступ разрешен (Привилегия владельца)", show_alert=True)
    else:
        await callback.answer("⭐ Нужно больше Stars!", show_alert=True)

@dp.message(F.text == "🌟 ДОНАТ")
async def donation(message: types.Message):
    await bot.send_invoice(
        message.chat.id,
        title="Поддержка проекта",
        description="Пожертвование в Stars",
        payload="don",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="⭐ 50", amount=50)]
    )

@dp.pre_checkout_query()
async def checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message()
async def main_logic(message: types.Message):
    text_upper = message.text.upper().strip()

    # Проверка кнопок меню
    if text_upper == "🎁 ПРОМОКОД":
        await message.answer("🔑 Введите ваш секретный код:")
        return

    # Проверка промокодов
    if text_upper in PROMO_CODES:
        await message.answer(f"✅ УСПЕХ!\n{PROMO_CODES[text_upper]}")
        return

    # Игнорируем нажатия кнопок меню
    if message.text in ["💎 МАГАЗИН", "🌟 ДОНАТ", "👤 ПРОФИЛЬ"]:
        return

    # ИИ (Улучшенное ядро GPT-4o)
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o,
            messages=[
                {"role": "system", "content": "Ты - Gemini-X Ultra. Отвечай кратко, профессионально и по сути."},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response if response else "📡 Ядро не ответило.")
    except Exception:
        await message.answer("⚠️ Ошибка связи. Повторите запрос.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
