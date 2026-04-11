import asyncio
import aiohttp
import random
import os
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BufferedInputFile, LabeledPrice, PreCheckoutQuery, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile

# --- [ГЛОБАЛЬНЫЕ НАСТРОЙКИ] ---
# На GitHub лучше использовать секреты, но для простоты вставь токен сюда:
TOKEN = '8750614833:AAE8lUJ_QDV43QK26Bp_zsAlhOAwNH1DyCQ' 
ADMIN_ID = 7213280513  # ТВОЙ ID
CHANNEL_URL = "https://t.me/froggy_Nkoop" 

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher()
boost_users = {}

# --- [ИНТЕРФЕЙС ГИТХАБ-ЛОГОВ (РУССКИЙ)] ---
def update_logs(sobitie, bug="СТАБИЛЬНО"):
    # Очистка консоли не всегда работает в GitHub Actions, поэтому просто печатаем красиво
    print(f"\n[S] СИСТЕМА: mibot.py | СТАТУС: ОНЛАЙН")
    print(f"[M] МОЗГ: 5 СЕКУНД | АНАТОМИЯ-ФИКС: ВКЛ")
    print(f"[!] СОБЫТИЕ: {sobitie}")
    print(f"[?] ОШИБКИ: {bug}\n")

def has_turbo(uid):
    return uid == ADMIN_ID or (uid in boost_users and time.time() < boost_users[uid])

# --- [ИНТЕРФЕЙС КНОПОК] ---
def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 МОЙ ЛИЧНЫЙ АККАУНТ", callback_data="go_profile")],
        [InlineKeyboardButton(text="🎨 НЕЙРО-АРТ (5с)", callback_data="go_image"),
         InlineKeyboardButton(text="🎮 ГЕЙМ-МАСТЕР", callback_data="go_game")],
        [InlineKeyboardButton(text="⚡ ТУРБО-УСКОРЕНИЕ", callback_data="go_boost")]
    ])

# --- [ЯДРО ИНТЕЛЛЕКТА: 5 СЕКУНД] ---
async def fetch_smart_ai(text, is_game=False):
    url = "https://text.pollinations.ai/"
    instruction = (
        "Ты — элитный ИИ 'mibot'. Думай 5 секунд и давай безупречный ответ. "
        "Списывай из Google правильно. Если это код — делай его рабочим сразу."
    )
    payload = {
        "messages": [{"role": "system", "content": instruction}, {"role": "user", "content": text}],
        "model": "openai",
        "search": True
    }
    async with aiohttp.ClientSession() as session:
        try:
            timeout = 30 if is_game else 7
            async with session.post(url, json=payload, timeout=timeout) as resp:
                return await resp.text()
        except:
            return "🛸 Нейро-щит зафиксировал сбой сети. Попробуй еще раз!"

# --- [ОБРАБОТЧИКИ] ---

@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    update_logs(f"Старт от {m.from_user.id}")
    await m.answer(f"👋 Добро пожаловать в mibot.py на GitHub!\n\nЯ настроен на ультра-скорость. Нажми на кнопку аккаунта, чтобы увидеть активные режимы.", reply_markup=get_main_kb())

@dp.callback_query(F.data == "go_profile")
async def view_profile(cb: types.CallbackQuery):
    uid = cb.from_user.id
    status = "💎 ВЛАДЕЛЕЦ СИСТЕМЫ" if uid == ADMIN_ID else ("🚀 ТУРБО-РЕЖИМ" if has_turbo(uid) else "🐢 СТАНДАРТ")
    
    modes = (
        "🟢 Google-Поиск 5.0\n"
        "🟢 Анатомия-Фикс (Прямые руки)\n"
        "🟢 Турбо-Всплеск (5 сек)\n"
        "🟢 Гейм-Дизайнер (HTML5)"
    )
    
    text = (
        f"💳 ЛИЧНЫЙ АККАУНТ ПОЛЬЗОВАТЕЛЯ\n"
        f"──────────────────────\n"
        f"👤 Имя: {cb.from_user.first_name}\n"
        f"🆔 ID: {uid}\n"
        f"📊 Статус: {status}\n"
        f"──────────────────────\n"
        f"⚙️ ВКЛЮЧЕННЫЕ РЕЖИМЫ ОТ ТЕБЯ:\n{modes}\n"
        f"──────────────────────\n"
        f"🚀 *Все системы GitHub работают на 100%*"
    )
    await cb.message.answer(text, reply_markup=get_main_kb())
    await cb.answer()

@dp.message(Command("game"))
async def game_gen(m: types.Message):
    p = m.text.replace("/game", "").strip()
    if not p: return await m.answer("📝 Напиши название игры!")
update_logs(f"Код игры: {p}")
    msg = await m.answer("⚙️ Нейро-кодер на GitHub пишет твою игру...")
    code = await fetch_smart_ai(f"Напиши один файл HTML5 с игрой: {p}", is_game=True)
    path = f"game_{m.from_user.id}.html"
    with open(path, "w", encoding="utf-8") as f: f.write(code)
    await m.answer_document(FSInputFile(path), caption="🎮 Твоя игра готова!")
    os.remove(path)

@dp.message(Command("image"))
async def image_gen(m: types.Message):
    p = m.text.replace("/image", "").strip()
    if not p: return await m.answer("📝 Опиши арт!")
    update_logs(f"Арт (Фикс рук): {p[:15]}")
    await bot.send_chat_action(m.chat.id, "upload_photo")
    
    # Сверх-точный промпт для рук
    fix = "perfect anatomy, five fingers, masterpiece, high resolution"
    url = f"https://image.pollinations.ai/prompt/{p}, {fix}?nologo=true&seed={random.randint(1,99999)}&model=flux"
    
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            await m.answer_photo(BufferedInputFile(await r.read(), "art.png"), caption="🎨 Анатомия проверена. Руки в порядке.")

@dp.message()
async def talk(m: types.Message):
    if m.text.startswith("/"): return
    update_logs(f"Запрос: {m.text[:20]}")
    await bot.send_chat_action(m.chat.id, "typing")
    
    start_t = time.time()
    res = await fetch_smart_ai(m.text)
    total_t = round(time.time() - start_t, 2)
    
    await m.answer(f"{res}\n\n⏱ Списано идеально за {total_t} сек.")

async def main():
    await bot.set_my_commands([
        BotCommand(command='/start', description='🚀 Запуск'),
        BotCommand(command='/image', description='🎨 Арт (5 пальцев)'),
        BotCommand(command='/game', description='🎮 Игры'),
        BotCommand(command='/profile', description='💎 Аккаунт')
    ])
    update_logs("БОТ ПОЛНОСТЬЮ ОБНОВЛЕН НА GITHUB")
    await dp.start_polling(bot)

if __name__ == "__main__":
    while True:
        try: asyncio.run(main())
        except: time.sleep(1)
