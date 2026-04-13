import asyncio,aiohttp,json,random,re,urllib.parse,time
from aiogram import Bot,Dispatcher,types,F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,BufferedInputFile,LabeledPrice,WebAppInfo
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# --- НАСТРОЙКИ ---
TOKEN = '8750614833:AAE8lUJ_QDV43QK26Bp_zsAlhOAwNH1DyCQ'
MY_ID = 7213280513
CH_LINK = "https://t.me/froggy_Nkoop"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher(storage=MemoryStorage())
user_history, active_chats, online_users = {}, {}, {}

class States(StatesGroup):
    feedback = State()
    anon_chat = State()

async def ai_call(uid, txt):
    sys = "Ты TITAN 2026 (Gemini). Пиши ТОЛЬКО код HTML5+JS. Без лишних слов."
    if uid not in user_history: user_history[uid] = [{"role": "system", "content": sys}]
    user_history[uid].append({"role": "user", "content": txt})
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post("https://text.pollinations.ai/", json={"messages": user_history[uid][-15:], "model": "gemini"}, timeout=30) as r:
                if r.status == 200:
                    res = await r.text()
                    try: res = json.loads(res).get('content', res)
                    except: pass
                    res = re.sub(r'<reasoning_content>.*?</reasoning_content>|\{.*?\}', '', res, flags=re.DOTALL)
                    return res.strip()
    except: pass
    return "🚀 TITAN: Ошибка связи."

async def anim(m, steps):
    msg = await m.answer(steps[0])
    for s in steps[1:]:
        await asyncio.sleep(0.4)
        try: await msg.edit_text(s)
        except: pass
    return msg

@dp.message(F.text == "/start")
async def cmd_start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Фото (Цвет)", callback_data="b_dr"), InlineKeyboardButton(text="🕹 WebApp Игра", callback_data="b_gm")],
        [InlineKeyboardButton(text="🌟 SUPPORT ⭐10", callback_data="buy_stars")],
        [InlineKeyboardButton(text="🧱 Чат 🎤", callback_data="b_an"), InlineKeyboardButton(text="✍️ Отзыв", callback_data="b_fd")]
    ])
    await m.answer("🚀 **TITAN ULTRA 2026 (FIXED)**\n\n✅ Ошибки запуска исправлены\n✅ Фото только в цвете\n✅ Игры готовы для GitHub", reply_markup=kb)

@dp.callback_query(F.data == "buy_stars")
async def pay_stars(c: types.CallbackQuery):
    try: await bot.send_invoice(c.from_user.id, title="Support", description="⭐10", payload="stars", currency="XTR", prices=[LabeledPrice(label="⭐", amount=10)])
    except: await c.message.answer(f"🌟 Линк: {CH_LINK}")
    await c.answer()

@dp.callback_query(F.data.startswith("b_"))
async def handle_buttons(c: types.CallbackQuery, state: FSMContext):
    if c.data == "b_an":
        btns = [[InlineKeyboardButton(text=f"👤 {v['name']}", callback_data=f"inv_{id}")] for id, v in online_users.items() if id != c.from_user.id]
        await c.message.answer("🌐 Онлайн:" if btns else "📭 Ждем...", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns) if btns else None)
    elif c.data == "b_dr": await c.message.answer("📸 Опиши цветное фото:")
    elif c.data == "b_gm": await c.message.answer("🕹 Какую игру создать для GitHub?")
    elif c.data == "b_fd": await c.message.answer("📝 Отзыв:"); await state.set_state(States.feedback)
    await c.answer()

@dp.callback_query(F.data.startswith("inv_"))
async def handle_invite(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Да", callback_data=f"acc_{c.from_user.id}"), InlineKeyboardButton(text="❌", callback_data="deny")]])
    await bot.send_message(int(c.data.split("_")[1]), f"🔔 Запрос от {c.from_user.first_name}!", reply_markup=kb); await c.answer("📡 Ушло.")

@dp.callback_query(F.data.startswith("acc_"))
async def handle_accept(c: types.CallbackQuery, state: FSMContext):
    u1, u2 = c.from_user.id, int(c.data.split("_")[1])
    active_chats[u1], active_chats[u2] = u2, u1
    await state.set_state(States.anon_chat); await dp.fsm.get_context(bot, user_id=u2, chat_id=u2).set_state(States.anon_chat)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ СТОП", callback_data="stop_now")]])
    for u in [u1, u2]: await bot.send_message(u, "💎 ЧАТ АКТИВЕН! (Текст + ГС 🎤)", reply_markup=kb)
    await c.message.delete(); await c.answer()

@dp.message()
async def handle_main(m: types.Message, state: FSMContext):
    uid = m.from_user.id
    online_users[uid] = {"name": m.from_user.first_name, "t": time.time()}
    if await state.get_state() == States.anon_chat and uid in active_chats:
        target, kb = active_chats[uid], InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ СТОП", callback_data="stop_now")]])
        if m.text: await bot.send_message(target, f"📩: {m.text}", reply_markup=kb)
        elif m.voice: await bot.send_voice(target, m.voice.file_id, reply_markup=kb)
        return
    if await state.get_state() == States.feedback:
        await bot.send_message(MY_ID, f"🆘 ОТЗЫВ: {m.from_user.full_name}: {m.text}"); await m.answer("✅!"); await state.clear(); return
    txt = m.text.lower() if m.text else ""
    if any(x in txt for x in ["нарисуй", "фото", "арт"]):
        st = await anim(m, ["🛰 Gemini Vision...", "🎨 Только Цвет..."])
        p = urllib.parse.quote(f"{txt}, strictly color, vivid, 8k, raw photo")
        url = f"https://image.pollinations.ai/prompt/{p}?width=1024&height=1240&model=flux&nologo=true"
        await m.answer_photo(url, caption="🖼 **TITAN 2026**"); await st.delete(); return
    if m.text:
        st = await anim(m, ["🧠 Gemini размышляет...", "🕹 Сборка WebApp..."])
        res = await ai_call(uid, m.text); await st.delete()
        if any(x in res.lower() for x in ["<html", "doctype"]):
            file = BufferedInputFile(res.encode(), filename="index.html")
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎮 ТЕСТ WEBAPP", web_app=WebAppInfo(url=f"https://pollinations.ai/p/{random.randint(1,999)}?preview=true&code={urllib.parse.quote(res)}"))]])
            await m.answer_document(file, caption="✅ Файл `index.html` для GitHub готов!")
            await m.answer("🕹 Запусти игру:", reply_markup=kb)
        else: await m.answer(res)

if __name__ == "__main__":
    async def run():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    asyncio.run(run())
@dp.callback_query(F.data.startswith("inv_"))
