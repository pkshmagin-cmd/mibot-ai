import asyncio,aiohttp,json,random,re,urllib.parse,time
from aiogram import Bot,Dispatcher,types,F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,BufferedInputFile,LabeledPrice,WebAppInfo
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# --- КОНФИГ ---
TOKEN, MY_ID, CH_LINK = '8750614833:AAE8lUJ_QDV43QK26Bp_zsAlhOAwNH1DyCQ', 7213280513, "https://t.me/froggy_Nkoop"
# Сюда впиши свою будущую ссылку GitHub Pages (например: https://твойник.github.io/название-репо/)
GITHUB_PAGE_URL = "https://github.com/твойник/твойрепо" 

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher(storage=MemoryStorage())
user_history, active_chats, online_users = {}, {}, {}

class States(StatesGroup):
    feedback = State()
    anon_chat = State()

async def ai_call(uid, txt):
    sys = "Ты TITAN 2026 (Gemini). Пиши ТОЛЬКО код HTML5+JS. Сделай код адаптивным под мобильные экраны Telegram."
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
    return "🚀 Ошибка генерации кода."

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
        [InlineKeyboardButton(text="📸 Цветное Фото", callback_data="b_dr"), InlineKeyboardButton(text="🕹 WebApp для GitHub", callback_data="b_gm")],
        [InlineKeyboardButton(text="🌟 SUPPORT ⭐10", callback_data="buy_stars")],
        [InlineKeyboardButton(text="🧱 Анонимный Чат", callback_data="b_an")]
    ])
    await m.answer("🚀 **TITAN ULTRA 2026 (GitHub Ready)**\n\nТеперь я готовлю код специально для размещения на GitHub Pages!", reply_markup=kb)

@dp.message()
async def handle_main(m: types.Message, state: FSMContext):
    uid = m.from_user.id
    online_users[uid] = {"name": m.from_user.first_name, "t": time.time()}
    
    # Обработка анонимного чата
    if await state.get_state() == States.anon_chat and uid in active_chats:
        target = active_chats[uid]
        if m.text: await bot.send_message(target, f"📩: {m.text}")
        elif m.voice: await bot.send_voice(target, m.voice.file_id)
        return

    txt = m.text.lower() if m.text else ""
    
    # Генерация фото (Цветные)
    if any(x in txt for x in ["нарисуй", "фото"]):
        st = await anim(m, ["🛰 Gemini Vision...", "🎨 Только Цвет (Flux)..."])
        p = urllib.parse.quote(f"{txt}, strictly color, vivid, 8k, raw photo")
        url = f"https://image.pollinations.ai/prompt/{p}?width=1024&height=1240&model=flux&nologo=true"
        await m.answer_photo(url, caption="🖼 **TITAN COLOR 2026**"); await st.delete(); return

   # Генерация Игр для GitHub
    if m.text:
        st = await anim(m, ["🧠 Gemini пишет код...", "📂 Подготовка для GitHub..."])
        res = await ai_call(uid, m.text); await st.delete()
        if any(x in res.lower() for x in ["<html", "doctype"]):
            # Генерируем файл index.html
            file = BufferedInputFile(res.encode(), filename="index.html")
            
            # Ссылка через pollinations для мгновенного теста (пока ты не залил на GitHub)
            webapp_url = f"https://pollinations.ai/p/{random.randint(1,9999)}?preview=true&code={urllib.parse.quote(res)}"
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎮 ТЕСТ WEBAPP (В Telegram)", web_app=WebAppInfo(url=webapp_url))],
                [InlineKeyboardButton(text="📦 ИНСТРУКЦИЯ ДЛЯ GITHUB", callback_data="gh_info")]
            ])
            
            await m.answer_document(file, caption="✅ **Код для GitHub готов!**\n\n1. Создай репозиторий на GitHub\n2. Загрузи туда этот файл под именем `index.html`\n3. Включи GitHub Pages\n4. Полученную ссылку вставь в настройки WebApp!")
            await m.answer("🕹 Можешь протестировать игру прямо сейчас:", reply_markup=kb)
        else: await m.answer(res)

@dp.callback_query(F.data == "gh_info")
async def gh_info(c: types.CallbackQuery):
    await c.message.answer("📝 **Как запустить это на GitHub:**\n\n1. Зайди на github.com и создай новый репозиторий.\n2. Нажми 'Add file' -> 'Upload files' и перетащи туда файл `index.html`.\n3. Перейди в 'Settings' -> 'Pages'.\n4. В разделе Build and deployment выбери ветку 'main' и нажми 'Save'.\n5. Через минуту GitHub даст тебе ссылку `https://...`. Её и используй!")
    await c.answer()

if __name__ == "__main__":
    async def run():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    asyncio.run(run())
