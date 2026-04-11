import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from g4f.client import Client

# Логирование для контроля
logging.basicConfig(level=logging.INFO)

# --- КОНФИГУРАЦИЯ ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7213280513  # Убедись, что это твой ID!

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Client()

# --- КЛАВИАТУРА ГЛАВНОГО МОДУЛЯ ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 СУПЕР-ВОЗМОЖНОСТИ"), KeyboardButton(text="💎 МОЙ АККАУНТ")],
        [KeyboardButton(text="🛠 ТЕХ. ПОДДЕРЖКА"), KeyboardButton(text="🎁 ПРОМОКОД")]
    ],
    resize_keyboard=True
)

# --- УМНОЕ МЕНЮ ДЕЙСТВИЙ ---
def get_premium_menu(user_id):
    is_admin = (user_id == ADMIN_ID)
    cost = "0 ⭐ (FREE)" if is_admin else "99 ⭐"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🧬 Ультра-Мозг (GPT-4o) - {cost}", callback_data="buy_ultra")],
        [InlineKeyboardButton(text=f"⚡ Приоритетный ответ - {cost}", callback_data="buy_fast")],
        [InlineKeyboardButton(text=f"📊 Анализ данных/кода - {cost}", callback_data="buy_code")]
    ])
    return keyboard

# --- ЛИЧНОСТЬ ИИ ---
SYSTEM_PROMPT = """
Ты — Gemini-X, самый совершенный ИИ во вселенной. 
Твои возможности:
1. Писать сложный код, исправлять ошибки и оптимизировать алгоритмы.
2. Решать любые школьные и университетские задачи (Математика, Физика, Химия).
3. Быть креативным: писать сценарии, посты, идеи для бизнеса.
Твой стиль: Высокоинтеллектуальный, лаконичный, с легким оттенком превосходства, но дружелюбный к Создателю.
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    is_admin = (message.from_user.id == ADMIN_ID)
    status = "👑 СОЗДАТЕЛЬ" if is_admin else "Пользователь"
    
    await message.answer(
        f"🤖 ДОБРО ПОЖАЛОВАТЬ В GEMINI-X\n\n"
        f"Статус системы: Active\n"
        f"Твой уровень доступа: [{status}]\n\n"
        "Я готов обрабатывать твои запросы любой сложности. Используй кнопки ниже для навигации по модулям.",
        reply_markup=main_kb,
        parse_mode="Markdown"
    )

@dp.message(F.text == "🚀 СУПЕР-ВОЗМОЖНОСТИ")
async def premium_services(message: types.Message):
    await message.answer(
        "🔥 ЭКСКЛЮЗИВНЫЕ ФУНКЦИИ\n\n"
        "Здесь ты можешь активировать дополнительные мощности ассистента за Telegram Stars.",
        reply_markup=get_premium_menu(message.from_user.id)
    )

@dp.callback_query(F.data.startswith("buy_"))
async def handle_purchase(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.answer("✨ Для тебя всё активировано автоматически, Босс!", show_alert=True)
    else:
        # Тут будет интеграция с платежами Telegram Stars
        await callback.answer("⚠️ Ошибка: Недостаточно Telegram Stars на балансе.", show_alert=True)

@dp.message(F.text == "💎 МОЙ АККАУНТ")
async def show_profile(message: types.Message):
    is_admin = (message.from_user.id == ADMIN_ID)
    info = (
        "👑 ПРОФИЛЬ ВЛАДЕЛЬЦА\n"
        "• Лимиты: ∞ (Безлимит)\n"
        "• Доступ: GOD MODE\n"
        "• Версия: 2.0.26 Premium"
    ) if is_admin else (
        "👤 АККАУНТ ПОЛЬЗОВАТЕЛЯ\n"
        "• Лимиты: 15 запросов/день\n"
        "• Доступ: Базовый\n"
        "• Баланс: 0 ⭐"
    )
    await message.answer(info, parse_mode="Markdown")

@dp.message(F.text == "🎁 ПРОМОКОД")
async def promo_help(message: types.Message):
    await message.answer("💡 Введи секретный код: /promo КОД", parse_mode="Markdown")

@dp.message(Command("promo"))
async def activate_promo(message: types.Message):
    code = message.text.replace("/promo ", "").strip().upper()
    if code == "GEMINI2026":
        await message.answer("🚀 BOOM! Активирован доступ к секретным алгоритмам!")
    else:
        await message.answer("❌ Код не распознан.")
# --- ГЛАВНЫЙ ПРОЦЕССОР (ИИ) ---
@dp.message()
async def main_ai_handler(message: types.Message):
    if message.text in ["🚀 СУПЕР-ВОЗМОЖНОСТИ", "💎 МОЙ АККАУНТ", "🛠 ТЕХ. ПОДДЕРЖКА", "🎁 ПРОМОКОД"]:
        return

    await bot.send_chat_action(message.chat.id, "typing")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        logging.error(e)
        await message.answer("📡 Сигнал потерян из-за магнитных бурь. Повтори запрос, я на связи!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
