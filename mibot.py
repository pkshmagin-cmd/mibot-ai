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

# --- [КОНФИГУРАЦИЯ] ---
TOKEN = '8750614833:AAE8lUJ_QDV43QK26Bp_zsAlhOAwNH1DyCQ'
ADMIN_ID = 7213280513
CHANNEL_URL = "https://t.me/froggy_Nkoop"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher()
turbo_data = {}

def log(text):
    print(f"[{time.strftime('%H:%M:%S')}] 🚀 {text}")

# --- [КЛАВИАТУРЫ] ---
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 МОЙ АККАУНТ", callback_data="profile")],
        [InlineKeyboardButton(text="🎨 НЕЙРО-АРТ", callback_data="art_info"),
         InlineKeyboardButton(text="🎮 СОЗДАТЬ ИГРУ", callback_data="game_info")],
        [InlineKeyboardButton(text="⚡️ КУПИТЬ TURBO (5 ⭐️)", callback_data="buy_turbo")],
        [InlineKeyboardButton(text="🎁 ПОДДЕРЖАТЬ КАНАЛ", callback_data="don_menu")]
    ])

# --- [КОМАНДЫ] ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(f"🚀 mibot ULTIMATE запущен!\nИспользуй меню для управления:", reply_markup=main_kb())

@dp.callback_query(F.data == "profile")
async def profile(cb: types.CallbackQuery):
    uid = cb.from_user.id
    is_t = turbo_data.get(uid, False) or uid == ADMIN_ID
    status = "💎 АДМИН" if uid == ADMIN_ID else ("🚀 TURBO" if is_t else "🐢 СТАНДАРТ")
    text = (
        f"📋 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ\n"
        f"──────────────────────\n"
        f"👤 Имя: {cb.from_user.first_name}\n"
        f"📊 Статус: {status}\n"
        f"⚡️ Turbo: {'✅ Активен' if is_t else '❌ Выключен'}\n"
        f"──────────────────────\n"
        f"📢 Канал: {CHANNEL_URL}"
    )
    await cb.message.edit_text(text, reply_markup=main_kb())

# --- [ПЛАТЕЖИ STARS] ---
@dp.callback_query(F.data == "don_menu")
async def don(cb: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ 5", callback_data="don_5"), InlineKeyboardButton(text="⭐️ 50", callback_data="don_50")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="profile")]
    ])
    await cb.message.edit_text("🎁 Выберите сумму доната для канала:", reply_markup=kb)

@dp.callback_query(F.data.startswith("don_") | (F.data == "buy_turbo"))
async def pay(cb: types.CallbackQuery):
    is_t = cb.data == "buy_turbo"
    amt = 5 if is_t else int(cb.data.split("_")[1])
    payload = "turbo" if is_t else "donate"
    await bot.send_invoice(
        cb.message.chat.id, "Telegram Stars", "Оплата услуг mibot", 
        payload, "XTR", [LabeledPrice(label="XTR", amount=amt)]
    )

@dp.pre_checkout_query()
async def pre(q: PreCheckoutQuery):
    await q.answer(ok=True)

@dp.message(F.successful_payment)
async def success(m: types.Message):
    if m.successful_payment.invoice_payload == "turbo":
        turbo_data[m.from_user.id] = True
        await m.answer("⚡️ Режим TURBO активирован!")
    else:
        await m.answer("🎁 Спасибо за поддержку канала!")

# --- [ГЕНЕРАЦИЯ] ---
@dp.message(Command("image"))
async def image(m: types.Message):
    p = m.text.replace("/image", "").strip()
    if not p: return await m.answer("📝 Опиши картинку!")
    await bot.send_chat_action(m.chat.id, "upload_photo")
    url = f"https://image.pollinations.ai/prompt/{p},perfect%20anatomy,5%20fingers?nologo=true"
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            await m.answer_photo(BufferedInputFile(await r.read(), filename="art.png"), caption="🎨 Готово!")
async def main():
    log("ЗАПУСК СИСТЕМЫ...")
    await bot.set_my_commands([
        BotCommand(command="/start", description="Меню"),
        BotCommand(command="/image", description="Арт"),
        BotCommand(command="/profile", description="Профиль")
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
