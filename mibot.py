import os
import asyncio
import logging
import random
import time
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton, 
    BufferedInputFile
)
import g4f

# --- НАСТРОЙКИ ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") # Берет токен из Settings -> Secrets
ADMIN_ID = 7213280513

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БАЗА ДАННЫХ (В ПАМЯТИ) ---
users = {} 

def get_user_data(uid):
    if uid not in users:
        users[uid] = {'balance': 100, 'lvl': 1, 'last_msg': 0, 'status': 'User'}
    return users[uid]

# --- ЗАЩИТА ОТ ПЕРЕГРУЗКИ ---
def is_spam(user_id):
    now = time.time()
    u = get_user_data(user_id)
    if now - u['last_msg'] < 2.0: 
        return True
    u['last_msg'] = now
    return False

# --- КЛАВИАТУРА ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 МАГАЗИН"), KeyboardButton(text="👤 ПРОФИЛЬ")],
        [KeyboardButton(text="🖼 ГЕНЕРАЦИЯ"), KeyboardButton(text="🌟 ДОНАТ")]
    ],
    resize_keyboard=True
)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start(message: types.Message):
    get_user_data(message.from_user.id)
    await message.answer("🦾 GEMINI-X ONLINE\nЭкономика: Умеренная\nЗащита: Активна", reply_markup=main_kb)

@dp.message(F.text == "👤 ПРОФИЛЬ")
async def profile(message: types.Message):
    u = get_user_data(message.from_user.id)
    await message.answer(f"👤 ПРОФИЛЬ\n💰 Баланс: {u['balance']} б.\n📈 Множитель: x{u['lvl']}\n🎖 Статус: {u['status']}")

@dp.message(F.text == "🌟 ДОНАТ")
async def donate_info(message: types.Message):
    await message.answer(
        "🌟 ПОПОЛНЕНИЕ БАЛЛОВ\n\nКурс: 1 ед. = 50 баллов\nЧтобы получить 600 баллов, введи:\n/donate 12",
        parse_mode="Markdown"
    )

@dp.message(Command("donate"))
async def process_donate(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2: return
        amount = int(args[1])
        if amount <= 0 or amount > 1000: return
        
        u = get_user_data(message.from_user.id)
        reward = amount * 50
        u['balance'] += reward
        await message.answer(f"✅ Зачислено {reward} баллов!")
    except:
        await message.answer("Ошибка. Введи число.")

@dp.message(F.text == "🛒 МАГАЗИН")
async def shop(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔺 Улучшить Множитель (500 б.)", callback_data="up_lvl")]
    ])
    await message.answer("🏬 МАГАЗИН УЛУЧШЕНИЙ", reply_markup=kb)

@dp.callback_query(F.data == "up_lvl")
async def upgrade(callback: types.CallbackQuery):
    u = get_user_data(callback.from_user.id)
    if u['balance'] >= 500:
        u['balance'] -= 500
        u['lvl'] += 1
        await callback.answer(f"✅ Уровень x{u['lvl']}!", show_alert=True)
    else:
        await callback.answer("❌ Недостаточно баллов!", show_alert=True)

@dp.message(F.text == "🖼 ГЕНЕРАЦИЯ")
async def img_help(message: types.Message):
    await message.answer("Напиши запрос так: /img space cat\nЦена: 50 баллов")

@dp.message(Command("img"))
async def gen_img(message: types.Message):
    if is_spam(message.from_user.id): return
    u = get_user_data(message.from_user.id)
    if u['balance'] < 50:
        return await message.answer("❌ Нужно 50 баллов!")
    
    u['balance'] -= 50
    prompt = message.text.replace("/img", "").strip()
    await message.answer("🖼 Рисую... (-50 баллов)")
    
    url = f"https://image.pollinations.ai/prompt/{prompt}?seed={random.randint(1,999)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                await message.reply_photo(BufferedInputFile(await r.read(), filename="art.jpg"))
@dp.message()
async def ai_handler(message: types.Message):
    if is_spam(message.from_user.id): return
    if message.text in ["🛒 МАГАЗИН", "👤 ПРОФИЛЬ", "🖼 ГЕНЕРАЦИЯ", "🌟 ДОНАТ"]: return

    await bot.send_chat_action(message.chat.id, "typing")
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o,
            messages=[{"role": "user", "content": message.text}]
        )
        u = get_user_data(message.from_user.id)
        bonus = random.randint(2, 5) * u['lvl']
        u['balance'] += bonus
        await message.answer(f"{response}\n\n💰 +{bonus} баллов.")
    except:
        await message.answer("📡 Ошибка ядра.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
