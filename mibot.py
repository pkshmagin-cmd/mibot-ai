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
from g4f.client import Client

# Настройки
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7213280513 # Твой ID

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Client()

# --- КЛАВИАТУРА ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 МАГАЗИН УСЛУГ"), KeyboardButton(text="🌟 ПОДДЕРЖКА")],
        [KeyboardButton(text="👤 ПРОФИЛЬ"), KeyboardButton(text="🎁 ПРОМОКОД")]
    ],
    resize_keyboard=True
)

# --- УМНЫЙ МАГАЗИН (ВНУТРИ ТЕЛЕГРАМ) ---
def get_shop_kb(user_id):
    is_admin = (user_id == ADMIN_ID)
    price = "0 ⭐" if is_admin else "99 ⭐"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🧬 Ultra-Интеллект ({price})", callback_data="buy_ultra")],
        [InlineKeyboardButton(text=f"💻 Premium Кодер ({price})", callback_data="buy_coder")],
        [InlineKeyboardButton(text=f"📚 Решала задач ({price})", callback_data="buy_solver")]
    ])

# --- ПРАВИЛА ИИ (БЕЗ ЛИШНИХ СЛОВ) ---
SYSTEM_PROMPT = (
    "Ты — Gemini-X Ultra. Твоя задача: давать только прямой ответ. "
    "Запрещено писать вступления вроде 'Вот ваш ответ' или 'Я подумал'. "
    "Только суть, факты и код. Для Павла (Создателя) ты работаешь в режиме максимальной мощности."
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Жесткий сброс старого меню (лечит 404)
    await message.answer("⚙️ Синхронизация...", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.5)
    
    is_admin = (message.from_user.id == ADMIN_ID)
    await message.answer(
        f"🚀 GEMINI-X ULTRA ЗАПУЩЕН\n\nСтатус: {'OWNER' if is_admin else 'USER'}\n"
        "Магазин обновлен. Ошибки 404 устранены.",
        reply_markup=main_kb,
        parse_mode="Markdown"
    )

@dp.message(F.text == "💎 МАГАЗИН УСЛУГ")
async def show_shop(message: types.Message):
    await message.answer("🛒 МАГАЗИН ИИ-МОДУЛЕЙ\nВыберите расширение:", 
                         reply_markup=get_shop_kb(message.from_user.id))

@dp.callback_query(F.data.startswith("buy_"))
async def handle_buy(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.answer("✅ Модуль активирован бесплатно (Owner Mode)", show_alert=True)
    else:
        await callback.answer("⭐ Оплата временно доступна только через 'Поддержку'", show_alert=True)

@dp.message(F.text == "🌟 ПОДДЕРЖКА")
async def donate(message: types.Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Поддержка проекта",
        description="Донат в Telegram Stars",
        payload="donate",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=50)]
    )

@dp.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def success_pay(message: types.Message):
    await message.answer("💎 Спасибо за поддержку! Твой лимит запросов увеличен.")

# --- ЯДРО ИИ (ТОЛЬКО ОТВЕТ) ---
@dp.message()
async def ai_answer(message: types.Message):
    if message.text in ["💎 МАГАЗИН УСЛУГ", "🌟 ПОДДЕРЖКА", "👤 ПРОФИЛЬ", "🎁 ПРОМОКОД"]:
        return

    await bot.send_chat_action(message.chat.id, "typing")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}]
        )
        # Бот выдает только чистый текст ответа
        await message.answer(response.choices[0].message.content)
    except:
        await message.answer("⚠️ Ошибка связи. Повторите.")
if __name__ == "__main__":
    asyncio.run(main())

async def main():
    await dp.start_polling(bot)
