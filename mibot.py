import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from g4f.client import Client

# Логирование
logging.basicConfig(level=logging.INFO)

# --- НАСТРОЙКИ ---
TOKEN = os.getenv("BOT_TOKEN")
# ВАЖНО: Замени эти цифры на свой ID из @userinfobot, чтобы всё было бесплатно
ADMIN_ID = 7213280513 

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Client()

# --- КЛАВИАТУРА ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚡ СПИСОК ДЕЙСТВИЙ"), KeyboardButton(text="🎁 ПРОМОКОД")],
        [KeyboardButton(text="💎 МОЙ СТАТУС"), KeyboardButton(text="❓ ПОМОЩЬ")]
    ],
    resize_keyboard=True
)

# --- МЕНЮ ДЕЙСТВИЙ (ВМЕСТО МАГАЗИНА С ОШИБКОЙ 404) ---
def get_actions_menu(is_admin):
    status = "БЕСПЛАТНО (Owner)" if is_admin else "50 ⭐"
    status_vip = "БЕСПЛАТНО (Owner)" if is_admin else "150 ⭐"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📝 Решить задачу ({status})", callback_data="buy_task")],
        [InlineKeyboardButton(text=f"💻 Написать код ({status})", callback_data="buy_code")],
        [InlineKeyboardButton(text=f"👑 VIP Поддержка ({status_vip})", callback_data="buy_vip")]
    ])
    return keyboard

# Характер бота (Промпт)
SYSTEM_PROMPT = """
Ты — элитный искусственный интеллект последнего поколения. Твои знания безграничны.
Твои правила:
1. Отвечай максимально умно, глубоко и по существу. Никакой "воды" и глупых фраз.
2. Ты эксперт в математике, программировании и науках.
3. Для Павла (создателя) ты — верный помощник, для остальных — профессиональный ментор.
4. Если тебя просят написать код — пиши его идеально и с комментариями.
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    is_admin = message.from_user.id == ADMIN_ID
    name = "Создатель" if is_admin else message.from_user.first_name
    await message.answer(
        f"🚀 Приветствую, {name}!\n\nЯ — твой обновленный ИИ-терминал. Мои вычислительные мощности настроены на максимум. Теперь я не просто бот, а твой личный гений.",
        reply_markup=main_kb
    )

@dp.message(F.text == "⚡ СПИСОК ДЕЙСТВИЙ")
async def show_actions(message: types.Message):
    is_admin = message.from_user.id == ADMIN_ID
    await message.answer("🛠 Доступные спец-возможности:", reply_markup=get_actions_menu(is_admin))

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.answer("✅ Доступ разрешен! Ты создатель, для тебя всё бесплатно.", show_alert=True)
    else:
        await callback.answer("⭐ Оплата через Telegram Stars временно в режиме отладки.", show_alert=True)

@dp.message(F.text == "💎 МОЙ СТАТУС")
async def show_status(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 Статус: Владелец системы\n🔓 Лимиты: Отсутствуют\n⭐ Баланс: Безлимит")
    else:
        await message.answer("👤 Статус: Пользователь\n🔓 Лимиты: 10 запросов в день\n⭐ Баланс: 0 Stars")

@dp.message(F.text == "🎁 ПРОМОКОД")
async def promo_info(message: types.Message):
    await message.answer("Введи промокод командой: /promo КОД", parse_mode="Markdown")

@dp.message(Command("promo"))
async def use_promo(message: types.Message):
    code = message.text.replace("/promo ", "").strip().upper()
    if code == "ULTRA":
        await message.answer("🔥 АКТИВИРОВАНО! Режим 'Ультра-Интеллект' включен для твоего аккаунта.")
    else:
        await message.answer("❌ Промокод недействителен.")

@dp.message()
async def chat_ai(message: types.Message):
    if message.text in ["⚡ СПИСОК ДЕЙСТВИЙ", "🎁 ПРОМОКОД", "💎 МОЙ СТАТУС", "❓ ПОМОЩЬ"]:
        return
await bot.send_chat_action(message.chat.id, "typing")
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Самая умная модель
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        logging.error(e)
        await message.answer("⚠️ ИИ сейчас перегружен задачами. Попробуй еще раз через минуту!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
