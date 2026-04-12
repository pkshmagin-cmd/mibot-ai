# -*- coding: utf-8 -*-
import asyncio,aiohttp,json,random,re,urllib.parse,time
from aiogram import Bot,Dispatcher,types,F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,BufferedInputFile,LabeledPrice
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
TOKEN,MY_ID,CH_LINK='8750614833:AAE8lUJ_QDV43QK26Bp_zsAlhOAwNH1DyCQ',7213280513,"https://t.me/froggy_Nkoop"
bot=Bot(token=TOKEN,default=DefaultBotProperties(parse_mode='Markdown'))
dp=Dispatcher(storage=MemoryStorage())
user_history,active_chats,online_users={},{},{}
class States(StatesGroup):feedback,anon_chat=State(),State()
async def ai_call(uid,txt,is_game=False):
 sys="Ты TITAN PRO 2026. Общайся на равных. Твой создатель @froggy_Nkoop."
 if is_game:sys="Напиши один HTML5+JS файл для Telegram WebApp игры. Код 2026 года."
 if uid not in user_history:user_history[uid]=[{"role":"system","content":sys}]
 user_history[uid].append({"role":"user","content":txt})
 for m in ["openai","gemini","llama-3-70b"]:
  try:
   async with aiohttp.ClientSession() as s:
    async with s.post("https://text.pollinations.ai/",json={"messages":user_history[uid][-15:],"model":m,"seed":random.randint(1,999999)},timeout=20) as r:
     if r.status==200:
      res=await r.text()
      try:res=json.loads(res).get('content',res)
      except:pass
      return re.sub(r'<reasoning_content>.*?</reasoning_content>','',res,flags=re.DOTALL).strip()
  except:continue
 return "🚀 TITAN 2026: Соединение ок."
async def anim(m,steps):
 msg=await m.answer(steps[0])
 for s in steps[1:]:
  await asyncio.sleep(0.4)
  try:await msg.edit_text(s)
  except:pass
 return msg
@dp.message(F.text=="/start")
async def cmd_start(m:types.Message):
 st=await anim(m,["🛰 TITAN 24.3...","🧠 Core 2026..."]);await st.delete()
 kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎨 Арт 2026",callback_data="b_dr"),InlineKeyboardButton(text="🕹 WebApp Игра",callback_data="b_gm")],[InlineKeyboardButton(text="🌟 ПОДДЕРЖАТЬ ⭐10",callback_data="buy_stars")],[InlineKeyboardButton(text="🧱 Чат",callback_data="b_an"),InlineKeyboardButton(text="✍️ Отзыв",callback_data="b_fd")]])
 await m.answer("🚀 **TITAN PRO 24.3**\n\n🤖 Интеллект 2026 активен.\n🎨 Recraft 2.0: Анатомия 10/10.\n🧱 Чат с отменой готов.",reply_markup=kb)
@dp.callback_query(F.data=="buy_stars")
async def pay_stars(c:types.CallbackQuery):
 try:await bot.send_invoice(c.from_user.id,title="Premium TITAN",description=f"Support {CH_LINK}",payload="stars",currency="XTR",prices=[LabeledPrice(label="⭐",amount=10)])
 except:await c.message.answer(f"🌟 **ПОДДЕРЖКА**\n\nОплата: {CH_LINK}",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔗 КАНАЛ",url=CH_LINK)]]))
 await c.answer()
@dp.callback_query(F.data.startswith("b_"))
async def handle_buttons(c:types.CallbackQuery,state:FSMContext):
 if c.data=="b_an":
  btns=[[InlineKeyboardButton(text=f"🧱 {v['name']}",callback_data=f"inv_{id}")] for id,v in online_users.items() if id!=c.from_user.id]
  await c.message.answer("🌐 В сети:" if btns else "📭 Пусто.",reply_markup=InlineKeyboardMarkup(inline_keyboard=btns) if btns else None)
 elif c.data=="b_dr":await c.message.answer("🖌 Опиши арт:")
 elif c.data=="b_gm":await c.message.answer("🕹 Какую игру (WebApp)?")
 elif c.data=="b_fd":await c.message.answer("📝 Отзыв:");await state.set_state(States.feedback)
 await c.answer()
@dp.callback_query(F.data=="stop_now")
async def inline_stop(c:types.CallbackQuery,state:FSMContext):
 if c.from_user.id in active_chats:
  p=active_chats.pop(c.from_user.id);active_chats.pop(p,None);await state.clear();await dp.fsm.get_context(bot,user_id=p,chat_id=p).clear()
  await bot.send_message(p,"🔌 Собеседник вышел.");await c.message.answer("🔌 Вы вышли.")
 await c.answer()
@dp.callback_query(F.data.startswith("inv_"))
async def handle_invite(c:types.CallbackQuery):
 kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅",callback_data=f"acc_{c.from_user.id}"),InlineKeyboardButton(text="❌",callback_data=f"deny_{c.from_user.id}")]])
 await bot.send_message(int(c.data.split("_")[1]),f"🔔 {c.from_user.full_name} зовет в чат!",reply_markup=kb);await c.answer("📡 Ушло.")
@dp.callback_query(F.data.startswith("acc_"))
async def handle_accept(c:types.CallbackQuery,state:FSMContext):
 u1,u2=c.from_user.id,int(c.data.split("_")[1]);active_chats[u1],active_chats[u2]=u2,u1
 await state.set_state(States.anon_chat);await dp.fsm.get_context(bot,user_id=u2,chat_id=u2).set_state(States.anon_chat)
 kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ СТОП",callback_data="stop_now")]])
 for u in [u1,u2]:await bot.send_message(u,"💎 СВЯЗЬ УСТАНОВЛЕНА!",reply_markup=kb)
 await c.message.delete();await c.answer()
@dp.message()
async def handle_main(m:types.Message,state:FSMContext):
 uid,uname=m.from_user.id,m.from_user.full_name;online_users[uid]={"name":uname,"last_seen":time.time()}
 if await state.get_state()==States.anon_chat and uid in active_chats:
  kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ СТОП",callback_data="stop_now")]])
  if m.text:await bot.send_message(active_chats[uid],f"📩: {m.text}",reply_markup=kb)
  return
 if await state.get_state()==States.feedback:
  await bot.send_message(MY_ID,f"🆘 ОТЗЫВ: {uname}: {m.text}");await m.answer("✅!");await state.clear();return
 txt=m.text.lower() if m.text else ""
 if any(x in txt for x in ["нарисуй","арт","фото"]):
  st=await anim(m,["🌀 Портал...","🖌 Recraft 2026..."]);p=urllib.parse.quote(f"{txt}, masterpiece, 8k, photorealistic, perfect anatomy")
  for _ in range(3):
   url=f"https://image.pollinations.ai/prompt/{p}?width=1024&height=1024&model=recraft&nologo=true&seed={random.randint(1,999999)}"
   try:await m.answer_photo(url,caption="🖼 TITAN PRO 2026");break
   except:await asyncio.sleep(2);continue
  else:await m.answer("❌ Ошибка.")
  await st.delete();return
 st=await anim(m,["🛰 Поиск...","🧠 Анализ..."]);res=await ai_call(uid,m.text,"игра" in txt);await st.delete()
 if "<html" in res.lower():await m.answer_document(BufferedInputFile(res.encode(),filename="game.html"),caption="🕹 WebApp игра!")
 else:await m.answer(res)
if __name__=="__main__":
 async def run():await bot.delete_webhook(drop_pending_updates=True);print("TITAN 24.3 ONLINE");await dp.start_polling(bot)
 asyncio.run(run())
