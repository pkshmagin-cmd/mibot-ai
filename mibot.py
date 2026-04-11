import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton, 
    LabeledPrice, PreCheckoutQuery
)
import g4f

# --- НАСТРОЙКИ ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7213280513 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Имитация базы данных (в оперативной памяти)
user_balances = {}
user_statuses = {}

# --- МЕНЮ ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 МАГАЗИН БАЛЛОВ"), KeyboardButton(text="👤 ПРОФИЛЬ")],
        [KeyboardButton(text="🌟 ДОНАТ"), KeyboardButton(text="🎁 ПРОМОКОД")]
    ],
    resize_keyboard=True
)

# --- БАЗА ПРОМОКОДОВ (Код: Баллы) ---
PROMO_CODES = {
    "GEMINI2026": 500,
    "POVAR": 1000,
    "START": 100,
    "PISTON": 300
}

# --- ФУНКЦИИ ---

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0
        user_statuses[user_id] = "User"
    
    await message.answer(
        "🦾 ДОБРО ПОЖАЛОВАТЬ В GEMINI-X CORE\n\nСистема баллов активирована. Используй кнопки ниже.",
        reply_markup=main_kb,
        parse_mode="Markdown"
    )

@dp.message(F.text == "👤 ПРОФИЛЬ")
async def profile(message: types.Message):
    user_id = message.from_user.id
    balance = user_balances.get(user_id, 0)
    status = "👑 Создатель" if user_id == ADMIN_ID else user_statuses.get(user_id, "User")
    
    await message.answer(
        f"👤 ТВОЙ ПРОФИЛЬ\n\n"
        f"🆔 ID: {user_id}\n"
        f"💰 Баланс: {balance} баллов\n"
        f"🎖 Статус: {status}",
        parse_mode="Markdown"
    )

@dp.message(F.text == "🛒 МАГАЗИН БАЛЛОВ")
async def point_shop(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 VIP Статус (500 б.)", callback_data="buy_vip")],
        [InlineKeyboardButton(text="🚀 Турбо-режим (200 б.)", callback_data="buy_turbo")]
    ])
    await message.answer("🛒 МАГАЗИН ЗА БАЛЛЫ\nВыбери товар:", reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
async def handle_buy(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = user_balances.get(user_id, 0)
    
    if callback.data == "buy_vip":
        cost = 500
        if balance >= cost or user_id == ADMIN_ID:
            if user_id != ADMIN_ID: user_balances[user_id] -= cost
            user_statuses[user_id] = "VIP"
            await callback.answer("✅ VIP активирован!", show_alert=True)
        else:
            await callback.answer(f"❌ Недостаточно баллов! Нужно {cost}.", show_alert=True)

@dp.message(F.text == "🎁 ПРОМОКОД")
async def ask_promo(message: types.Message):
    await message.answer("🔑 Введи секретный код для пополнения баланса:")

@dp.message()
async def global_handler(message: types.Message):
    user_id = message.from_user.id
    text_upper = message.text.upper().strip()

    # Обработка промокодов
    if text_upper in PROMO_CODES:
        points = PROMO_CODES[text_upper]
        user_balances[user_id] = user_balances.get(user_id, 0) + points
        await message.answer(f"🎉 УСПЕХ!\nНачислено {points} баллов. Проверь профиль!", parse_mode="Markdown")
        return

    # Логика ИИ (если это не кнопка)
    if message.text not in ["🛒 МАГАЗИН БАЛЛОВ", "👤 ПРОФИЛЬ", "🌟 ДОНАТ"]:
        await bot.send_chat_action(message.chat.id, "typing")
        try:
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.gpt_4o,
                messages=[{"role": "user", "content": message.text}]
            )
            await message.answer(response if response else "📡 Ошибка ядра.")
        except:
            await message.answer("⚠️ Ядро перегружено.")
# --- ОПЛАТА STARS (Пополнение баллов за деньги) ---
@dp.message(F.text == "🌟 ДОНАТ")
async def donation(message: types.Message):
    await bot.send_invoice(
        message.chat.id, "Пополнение баланса", "Купить 1000 баллов за Stars", "refill",
        "", "XTR", [LabeledPrice(label="1000 баллов", amount=50)]
    )

@dp.pre_checkout_query()
async def checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def got_payment(message: types.Message):
    user_id = message.from_user.id
    user_balances[user_id] = user_balances.get(user_id, 0) + 1000
    await message.answer("✅ Оплата прошла! 1000 баллов добавлены на баланс.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
