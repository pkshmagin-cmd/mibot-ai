import asyncio
import aiohttp
import random
import os
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    BufferedInputFile, BotCommand, InlineKeyboardButton, 
    InlineKeyboardMarkup, FSInputFile, LabeledPrice, PreCheckoutQuery
)

# --- [НАСТРОЙКИ] ---
TOKEN = '8750614833:AAE8lUJ_QDV43QK26Bp_zsAlhOAwNH1DyCQ'
ADMIN_ID = 7213280513
CHANNEL_URL = "https://t.me/froggy_Nkoop"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher()
turbo_data = {} # База Turbo-статусов

def log(text):
    print(f"[{time.strftime('%H:%M:%S')}] 🚀 {text}")

# --- [КЛАВИАТУРЫ] ---
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 МОЙ ЛИЧНЫЙ АККАУНТ", callback_data="profile")],
        [InlineKeyboardButton(text="🎨 НЕЙРО-АРТ", callback_data="art_info"),
         InlineKeyboardButton(text="🎮 СОЗДАТЬ ИГРУ", callback_data="game_info")],
        [InlineKeyboardButton(text="⚡️ КУПИТЬ TURBO (5 ⭐️)", callback_data="buy_turbo")],
        [InlineKeyboardButton(text="📢 НАШ КАНАЛ", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="🎁 ПОДДЕРЖАТЬ КАНАЛ", callback_data="donate_menu")]
    ])

def donate_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ 5", callback_data="don_5"),
         InlineKeyboardButton(text="⭐️ 10", callback_data="don_10")],
        [InlineKeyboardButton(text="⭐️ 25", callback_data="don_25"),
         InlineKeyboardButton(text="⭐️ 50", callback_data="don_50")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="profile")]
    ])

# --- [ЛОГИКА АККАУНТА] ---
@dp.callback_query(F.data == "profile")
async def show_profile(cb: types.CallbackQuery):
    uid = cb.from_user.id
    is_turbo = turbo_data.get(uid, False) or uid == ADMIN_ID
    status = "💎 ВЛАДЕЛЕЦ" if uid == ADMIN_ID else ("🚀 TURBO" if is_turbo else "🐢 СТАНДАРТ")

    text = (
        f"📋 ВАШ ПРОФИЛЬ mibot\n"
        f"──────────────────────\n"
        f"👤 Имя: {cb.from_user.first_name}\n"
        f"🆔 ID: {uid}\n"
        f"📊 Статус: {status}\n"
        f"──────────────────────\n"
        f"🛠 АКТИВНЫЕ РЕЖИМЫ:\n"
        f"✅ Google-Search (5с)\n"
        f"✅ Anatomy-Fix (5 Fingers)\n"
        f"{'✅ Turbo-Boost' if is_turbo else '❌ Turbo-Boost (Выкл)'}\n"
        f"──────────────────────\n"
        f"📢 *Поддержи канал кнопкой ниже!*"
    )
    await cb.message.edit_text(text, reply_markup=main_menu())
    await cb.answer()

# --- [ИНТЕЛЛЕКТ И ИГРЫ] ---
async def fetch_ai(prompt):
    url = "https://text.pollinations.ai/"
    payload = {
        "messages": [{"role": "system", "content": "Ты mibot. Отвечай быстро и четко."}, 
                     {"role": "user", "content": prompt}],
        "model": "openai", "search": True
    }
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=payload) as r:
            return await r.text()

@dp.message(Command("game"))
async def make_game(m: types.Message):
    name = m.text.replace("/game", "").strip()
    if not name: return await m.answer("📝 Напиши: /game название")
    
    msg = await m.answer("⚙️ Проектирую код игры...")
    code = await fetch_ai(f"Write HTML5 code for game: {name}. Single file.")
    path = f"game_{m.from_user.id}.html"
    with open(path, "w", encoding="utf-8") as f: f.write(code)
    
    await m.answer_document(FSInputFile(path), caption=f"🎮 Игра {name} готова!")
    os.remove(path)
    await msg.delete()

# --- [НЕЙРО-АРТ С ФИКСОМ РУК] ---
@dp.message(Command("image"))
async def make_image(m: types.Message):
    p = m.text.replace("/image", "").strip()
    if not p: return await m.answer("📝 Напиши: /image описание")
await bot.send_chat_action(m.chat.id, "upload_photo")
    fix = "perfect anatomy, five fingers, masterpiece, high quality"
    url = f"https://image.pollinations.ai/prompt/{p},{fix}?nologo=true&seed={random.randint(1,999)}&model=flux"
    
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            photo = BufferedInputFile(await r.read(), filename="art.png")
            await m.answer_photo(photo, caption="🎨 Анатомия проверена. 5 пальцев.")

# --- [ДОНАТЫ И ПЛАТЕЖИ] ---
@dp.callback_query(F.data == "donate_menu")
async def show_don(cb: types.CallbackQuery):
    await cb.message.edit_text("🎁 Выберите сумму пожертвования для канала:", reply_markup=donate_menu())
    await cb.answer()

@dp.callback_query(F.data.startswith("don_"))
@dp.callback_query(F.data == "buy_turbo")
async def pay_stars(cb: types.CallbackQuery):
    is_turbo = cb.data == "buy_turbo"
    amount = 5 if is_turbo else int(cb.data.split("_")[1])
    label = "Активация Turbo" if is_turbo else "Поддержка канала"
    
    await bot.send_invoice(
        cb.message.chat.id, title=label, description="Оплата в Telegram Stars",
        payload="turbo" if is_turbo else "donate", currency="XTR",
        prices=[LabeledPrice(label=label, amount=amount)]
    )
    await cb.answer()

@dp.pre_checkout_query()
async def pre_check(q: PreCheckoutQuery):
    await q.answer(ok=True)

@dp.message(F.successful_payment)
async def success_pay(m: types.Message):
    if m.successful_payment.invoice_payload == "turbo":
        turbo_data[m.from_user.id] = True
        await m.answer("⚡️ Turbo-режим включен! Приоритет активирован.")
    else:
        await m.answer("🎁 Спасибо! Твой донат пошел на развитие канала.")

# --- [СТАРТ] ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(f"🚀 mibot готов к работе!\nПользуйся кнопками меню:", reply_markup=main_menu())

async def main():
    await bot.set_my_commands([
        BotCommand(command="/start", description="🚀 Меню"),
        BotCommand(command="/profile", description="👤 Аккаунт"),
        BotCommand(command="/image", description="🎨 Арт"),
        BotCommand(command="/game", description="🎮 Игра")
    ])
    log("СИСТЕМА ОНЛАЙН")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
