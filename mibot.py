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
    ReplyKeyboardRemove, LabeledPrice, PreCheckoutQuery, BufferedInputFile
)
import g4f
from g4f.client import Client

# --- НАСТРОЙКИ (БЕЗОПАСНОСТЬ) ---
logging.basicConfig(level=logging.INFO)
# На GitHub токен берется из Секретов!
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7213280513 

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Client()

# --- КЛАВИАТУРЫ (АНТИ-404) ---
def get_main_menu(user_id):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💎 МАГАЗИН"), KeyboardButton(text="🎨 НАРИСОВАТЬ")],
            [KeyboardButton(text="🌟 ДОНАТ"), KeyboardButton(text="🎁 ПРОМОКОД")]
        ],
        resize_keyboard=True
    )

def get_shop_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧬 Модуль Ultra (Free)", callback_data="buy_ok")],
        [InlineKeyboardButton(text="💻 Режим Кодера (Free)", callback_data="buy_ok")]
    ])

# --- БАЗА ПРОМОКОДОВ (ВСТРОЕНО) ---
PROMO_CODES = {
    "GEMINI2026": "💎 Статус VIP и 500 Stars начислены!",
    "POVAR": "👨‍🍳 Секретный бонус от Повара: Безлимитный ИИ на 24 часа!",
    "START": "🎁 Приветственный бонус: +50 запросов к Ultra-ядру.",
    "GITHUB": "🌐 Бонус за поддержку облачного сервера активен!",
    "ADMIN_POWER": "👑 Активирован режим Создателя (все модули открыты).",
    "PISTON": "🚀 Поршни заведены! Скорость ответов и генерации увеличена.",
    "FREE_MOD": "🧪 Модуль Генератор PRO активирован бесплатно!"
}

# --- КОМАНДЫ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Очистка старых кнопок и кэша
    await message.answer("🔄 Перезагрузка ядра. Восстановление связи...", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.5)
    
    user_id = message.from_user.id
    status = "👑 GOD MODE" if user_id == ADMIN_ID else "USER"
    
    await message.answer(
        f"🌌 GEMINI-X CORE v9.0\n\nСтатус: {status}\nСвязь: ВОССТАНОВЛЕНА ✅\nМагазин: No-404 Active 🛡️\n\nСистема готова. Что прикажешь?",
        reply_markup=get_main_menu(user_id),
        parse_mode="Markdown"
    )

@dp.message(F.text == "💎 МАГАЗИН")
async def open_shop(message: types.Message):
    await message.answer("🏪 ВНУТРЕННИЙ МАРКЕТ", reply_markup=get_shop_kb())

@dp.callback_query(F.data == "buy_ok")
async def shop_callback(callback: types.CallbackQuery):
    await callback.answer("✅ Активировано!", show_alert=True)

@dp.message(F.text == "🌟 ДОНАТ")
async def send_donation(message: types.Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Поддержка",
        description="Донат в Stars",
        payload="donation",
        provider_token=""
        currency="XTR",
        
prices=[LabeledPrice(label="⭐ 50", amount=50)]
    )

@dp.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

# --- ГЕНЕРАТОР КАРТИНОК (БРОНИРОВАННЫЙ) ---

@dp.message(F.text == "🎨 НАРИСОВАТЬ")
async def ask_for_art(message: types.Message):
    await message.answer("🖼️ ОПИШИТЕ КАРТИНКУ:\n(Например: cat in space cyberpunk style)")
    return

async def fetch_image(session, url):
    try:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                return await response.read()
    except:
        return None
    return None

async def generate_image_safe(prompt):
    seed = random.randint(0, 99999)
    # Запасные аэродромы для генерации (Pollinations, HuggingFace, etc.)
urls = [
        f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true&seed={seed}",
        f"https://api.prodiart.com/prompt/{prompt}?seed={seed}",
        f"https://hf.space/embed/mhdang/SDXL-Lightning/+/api/predict/{prompt}"
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in urls:
            logging.info(f"Trying image generator: {url[:30]}...")
            img_data = await fetch_image(session, url)
            if img_data:
                return img_data
    return None

# --- ГЛАВНОЕ ЯДРО: ИИ + ПРОМО + КАРТИНКИ ---

@dp.message()
async def core_processor(message: types.Message):
    # 1. ОБРАБОТКА КОМАНДЫ ГЕНЕРАЦИИ (Если текст длинный и содержит слова-триггеры)
    text_upper = message.text.upper()
    if text_upper == "🎁 ПРОМОКОД":
        await message.answer("🔑 Введите ваш секретный промокод:")
        return

    # 2. ПРОВЕРКА ПРОМОКОДОВ
    if text_upper.strip() in PROMO_CODES:
        bonus = PROMO_CODES[text_upper.strip()]
        await message.answer(f"✅ ПРОМОКОД УСПЕШНО АКТИВИРОВАН!\n\n{bonus}")
        return

    # Игнорируем другие кнопки
    if message.text in ["💎 МАГАЗИН", "🎨 НАРИСОВАТЬ", "🌟 ДОНАТ"]:
        return

    # 3. ЛОГИКА ГЕНЕРАЦИИ КАРТИНОК (По запросу)
    is_drawing_prompt = any(x in text_upper for x in ["НАРИСУЙ", "DRAW", "PAINT", "IMAGE OF", "PICTURE OF", "АРТ"])
    if is_drawing_prompt or len(message.text) > 10 and not is_drawing_prompt:
        # Простая эвристика: если текст длинный и на английском, пробуем рисовать
        if all(ord(c) < 128 for c in message.text.replace(" ", "")) and len(message.text) > 5:
            await bot.send_chat_action(message.chat.id, "upload_photo")
            img_data = await generate_image_safe(message.text)
            if img_data:
                await message.reply_photo(BufferedInputFile(img_data, filename="gemini_art.png"))
                return

    # 4. ЯДРО ИИ (ТОЛЬКО СУТЬ)
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # Основная попытка (GPT-4o)
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o,
            messages=[{"role": "system", "content": "Ты - Gemini-X Ultra. Отвечай только по сути."}, {"role": "user", "content": message.text}]
        )
        if not response:
             raise Exception("Empty response")
        await message.answer(response)
    except:
        # Запасная попытка (Более легкая модель)
        logging.warning("GPT-4o failed. Trying backup model.")
        try:
            response = await g4f.ChatCompletion.create_async(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message.text}]
            )
            await message.answer(response)
        except:
            await message.answer("⚠️ Ядро перегружено. Промокоды и Магазин работают, ИИ ответит через минуту.")

# ЗАПУСК
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
