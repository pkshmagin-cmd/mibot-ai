import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardRemove, LabeledPrice, PreCheckoutQuery
)
import g4f
from g4f.client import Client

# --- КОНФИГУРАЦИЯ ---
logging.basicConfig(level=logging.INFO)

# ВАЖНО: На GitHub токен берется из Secrets!
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7213280513 

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Client()

# --- МЕНЮ ---
def get_main_menu(user_id):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💎 МАГАЗИН ПРИВИЛЕГИЙ"), KeyboardButton(text="🌟 ДОНАТ")],
            [KeyboardButton(text="👤 ПРОФИЛЬ"), KeyboardButton(text="🎁 ПРОМОКОД")]
        ],
        resize_keyboard=True
    )

def get_shop_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧪 Модуль: ГЕНЕРАТОР (PRO)", callback_data="buy_priv")],
        [InlineKeyboardButton(text="💻 Модуль: КОДЕР (ULTRA)", callback_data="buy_priv")]
    ])

# --- ЛОГИКА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🔄 Синхронизация с сервером...", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.5)
    
    user_id = message.from_user.id
    status = "👑 GOD MODE" if user_id == ADMIN_ID else "USER"
    
    await message.answer(
        f"🌌 GEMINI-X CLOUD v8.0\n\nСтатус: {status}\nСервер: GitHub Actions 🌐\n\nСистема готова.",
        reply_markup=get_main_menu(user_id),
        parse_mode="Markdown"
    )

@dp.message(F.text == "💎 МАГАЗИН ПРИВИЛЕГИЙ")
async def open_shop(message: types.Message):
    await message.answer("🏪 МАРКЕТПЛЕЙС", reply_markup=get_shop_kb())

@dp.callback_query(F.data == "buy_priv")
async def handle_privilege(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.answer("✨ Доступ разрешен автоматически.", show_alert=True)
    else:
        await callback.answer("⭐ Требуется оплата Stars.", show_alert=True)

@dp.message(F.text == "🌟 ДОНАТ")
async def send_donation(message: types.Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Поддержка",
        description="Донат Stars",
        payload="donation",
        provider_token="", 
        currency="XTR",
        prices=[LabeledPrice(label="⭐ 50", amount=50)]
    )

@dp.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def success_payment(message: types.Message):
    await message.answer("💎 Спасибо! Система обновлена.")

@dp.message()
async def ai_processor(message: types.Message):
    if message.text in ["💎 МАГАЗИН ПРИВИЛЕГИЙ", "🌟 ДОНАТ", "👤 ПРОФИЛЬ", "🎁 ПРОМОКОД"]:
        return

    await bot.send_chat_action(message.chat.id, "typing")
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o,
            messages=[
                {"role": "system", "content": "Ты — Gemini-X. Отвечай только по существу."},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response)
    except:
        await message.answer("⚠️ Ошибка связи с сервером.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
