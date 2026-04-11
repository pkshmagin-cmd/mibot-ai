import os
import asyncio
import logging
import random
import time
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

# --- НАСТРОЙКИ ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7213280513

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БАЗА ДАННЫХ (В ПАМЯТИ) ---
users = {} 
# Структура: {id: {'bal': 100, 'lvl': 1, 'used_promos': [], 'pet': None, 'emoji': '👤'}}

def get_u(uid):
    if uid not in users:
        users[uid] = {'bal': 100, 'lvl': 1, 'promos': [], 'pet': None, 'emoji': '👤', 'last': 0}
    return users[uid]

# --- КЛАВИАТУРА ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏪 МЕГА-МАРКЕТ"), KeyboardButton(text="👤 ИНФО")],
        [KeyboardButton(text="🎨 НЕЙРО-АРТ"), KeyboardButton(text="🎁 ПРОМОКОД")]
    ],
    resize_keyboard=True
)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start(message: types.Message):
    get_u(message.from_user.id)
    await message.answer("🛠 CORE v12.0: СИСТЕМА ОБНОВЛЕНА\n\n- Исправлены баги промокодов\n- Добавлен зоомагазин\n- Ядро стабилизировано", reply_markup=main_kb)

@dp.message(F.text == "👤 ИНФО")
async def profile(message: types.Message):
    u = get_u(message.from_user.id)
    pet_status = f"🐾 Питомец: {u['pet']}" if u['pet'] else "🐾 Питомца нет"
    await message.answer(
        f"{u['emoji']} ВАШ АЙДИ: {message.from_user.id}\n\n"
        f"💰 Баланс: {u['bal']} б.\n"
        f"🚀 Ядро: уровень {u['lvl']}\n"
        f"{pet_status}", parse_mode="Markdown")

@dp.message(F.text == "🏪 МЕГА-МАРКЕТ")
async def shop(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Прокачать Ядро (500 б.)", callback_data="up_core")],
        [InlineKeyboardButton(text="🐱 Купить Кибер-Кота (1500 б.)", callback_data="buy_pet_cat")],
        [InlineKeyboardButton(text="👑 Элитный Эмодзи [💎] (2000 б.)", callback_data="buy_emoji")]
    ])
    await message.answer("🛒 АССОРТИМЕНТ ОБНОВЛЕН\nВыбери улучшение:", reply_markup=kb)

# Логика магазина
@dp.callback_query(F.data == "up_core")
async def up_core(c: types.CallbackQuery):
    u = get_u(c.from_user.id)
    if u['bal'] >= 500:
        u['bal'] -= 500
        u['lvl'] += 1
        await c.answer(f"Ядро разогнано до x{u['lvl']}!", show_alert=True)
    else:
        await c.answer("Не хватает баллов!", show_alert=True)

@dp.callback_query(F.data == "buy_pet_cat")
async def buy_pet(c: types.CallbackQuery):
    u = get_u(c.from_user.id)
    if u['bal'] >= 1500:
        u['bal'] -= 1500
        u['pet'] = "Кибер-Кот 🤖"
        await c.answer("Вы приобрели Кибер-Кота! Он защищает ваше ядро.", show_alert=True)
    else:
        await c.answer("Нужно 1500 баллов!", show_alert=True)

@dp.callback_query(F.data == "buy_emoji")
async def buy_emoji(c: types.CallbackQuery):
    u = get_u(c.from_user.id)
    if u['bal'] >= 2000:
        u['bal'] -= 2000
        u['emoji'] = "💎"
        await c.answer("Теперь у вас элитный статус!", show_alert=True)
    else:
        await c.answer("Нужно 2000 баллов!", show_alert=True)

@dp.message(F.text == "🎁 ПРОМОКОД")
async def promo_ask(message: types.Message):
    await message.answer("Введите код:")

@dp.message(Command("donate"))
async def donate(message: types.Message):
    try:
        val = int(message.text.split()[1])
        u = get_u(message.from_user.id)
        u['bal'] += val * 50
        await message.answer(f"🌟 Зачислено {val * 50} баллов!")
    except:
        await message.answer("Пример: /donate 12 (даст 600 баллов)")

@dp.message()
async def logic(message: types.Message):
    uid = message.from_user.id
    u = get_u(uid)
    
    # Защита от спама (глюков)
    if time.time() - u['last'] < 2: return
    u['last'] = time.time()
# Обработка ОДНОРАЗОВЫХ промокодов
    txt = message.text.upper()
    promos = {"POVAR": 1000, "GEMINI": 500, "PISTON": 300}
    if txt in promos:
        if txt in u['promos']:
            return await message.answer("❌ Вы уже использовали этот код!")
        u['promos'].append(txt)
        u['bal'] += promos[txt]
        return await message.answer(f"✅ Код активирован! +{promos[txt]} баллов.")

    if message.text in ["🏪 МЕГА-МАРКЕТ", "👤 ИНФО", "🎨 НЕЙРО-АРТ", "🎁 ПРОМОКОД"]: return

    # ИИ с улучшенной стабильностью
    import g4f
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # Пытаемся вызвать несколько моделей если одна упадет
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o,
            messages=[{"role": "user", "content": message.text}]
        )
        bonus = random.randint(3, 7) * u['lvl']
        if u['pet']: bonus += 10 # Бонус от питомца
        u['bal'] += bonus
        await message.answer(f"{response}\n\n💰 +{bonus} б.")
    except:
        await message.answer("🔄 Ядро перезагружается... Попробуйте еще раз.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
