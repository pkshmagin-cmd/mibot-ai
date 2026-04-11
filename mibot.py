import asyncio
import sqlite3
import random
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

# === КОНФИГУРАЦИЯ ===
TOKEN = '8750614833:AAE8lUJ_QDV43QK26Bp_zsAlhOAwNH1DyCQ'

ADMIN_ID = 7213280513  # ВСТАВЬ СВОЙ ID
WEB_APP_URL = "https://твой-логин.github.io/index.html" 

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Инициализация БД
def init_db():
    conn = sqlite3.connect("users_data.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, status TEXT DEFAULT "user")')
    conn.execute('CREATE TABLE IF NOT EXISTS promocodes (code TEXT PRIMARY KEY)')
    conn.commit()
    conn.close()

def get_status(user_id):
    if user_id == ADMIN_ID: return "creator"
    conn = sqlite3.connect("users_data.db")
    res = conn.execute("SELECT status FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return res[0] if res else "user"

# Установка списка команд в интерфейс Telegram
async def setup_bot_commands(bot: Bot):
    main_commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="promo", description="🎟 Активировать код"),
        BotCommand(command="shop", description="💎 Магазин привилегий")
    ]
    await bot.set_my_commands(main_commands)

# --- ОБРАБОТЧИКИ КОМАНД ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users_data.db")
    conn.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    
    kb = [[types.InlineKeyboardButton(text="💎 ОТКРЫТЬ МАГАЗИН", web_app=types.WebAppInfo(url=WEB_APP_URL))]]
    await message.answer(
        f"🌟 AI PROJECT 2026\n\n"
        f"Привет, {message.from_user.first_name}!\n"
        f"💬 Чат со мной — БЕСПЛАТНО.\n"
        f"🎨 Картинки доступны в Premium.\n\n"
        "Используй меню команд для навигации!",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb)
    )

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    kb = [[types.InlineKeyboardButton(text="💎 ПЕРЕЙТИ В МАГАЗИН", web_app=types.WebAppInfo(url=WEB_APP_URL))]]
    await message.answer("Выберите пакет услуг:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.message(Command("addpromo"))
async def add_promo(message: types.Message, command: CommandObject):
    if message.from_user.id != ADMIN_ID: return
    code = command.args.upper() if command.args else "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    conn = sqlite3.connect("users_data.db")
    try:
        conn.execute("INSERT INTO promocodes (code) VALUES (?)", (code,))
        conn.commit()
        await message.answer(f"✅ Промокод создан: {code}")
    except:
        await message.answer("❌ Ошибка (возможно, код уже существует).")
    conn.close()

@dp.message(Command("promo"))
async def use_promo(message: types.Message, command: CommandObject):
    if not command.args:
        return await message.answer("Введите код: /promo КОД")
    
    code = command.args.upper()
    conn = sqlite3.connect("users_data.db")
    res = conn.execute("SELECT code FROM promocodes WHERE code = ?", (code,)).fetchone()
    
    if res:
        conn.execute("UPDATE users SET status = 'premium' WHERE id = ?", (message.from_user.id,))
        conn.execute("DELETE FROM promocodes WHERE code = ?", (code,))
        conn.commit()
        await message.answer("🎉 Успех! Premium статус активирован.")
    else:
        await message.answer("❌ Код недействителен.")
    conn.close()

# --- УМНЫЙ ЧАТ ---
@dp.message()
async def main_chat(message: types.Message):
    if not message.text: return
    status = get_status(message.from_user.id)
    text = message.text.lower()
# Проверка на запрос картинки
    if any(word in text for word in ["нарисуй", "картинка", "сделай фото"]):
        if status in ["creator", "premium"]:
            await message.answer("🎨 Нейросеть начала рисовать... Опишите детали!")
        else:
            await message.answer("❌ Рисование доступно только в Premium.")
        return

    # Ответ ИИ
    if status == "creator":
        # Спец-ответ для тебя
        await message.answer(f"🚀 Слушаю, Создатель! Твой запрос принят без лимитов.\n\n🤖 ИИ: Я обработал запрос {message.text}. Система работает стабильно.")
    else:
        # Обычный ответ (бесплатно)
        await message.answer(f"🤖 ИИ: Ваш вопрос принят! Я готов общаться с вами бесплатно.")

async def main():
    init_db()
    await setup_bot_commands(bot) # Настройка меню команд
    print("--- БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())