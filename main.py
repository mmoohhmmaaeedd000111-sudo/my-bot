import telebot
from telebot import types
import json, os, requests
from threading import Thread
from flask import Flask

# --- الإعدادات ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "7154944941" 
API_URL = "https://kd1s.com/api/v2"
API_KEY = "9967a35290cae1978403a8caa91c59d6"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "OK"

def load_db():
    if not os.path.exists('db.json'): return {"users": {}, "orders": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

def get_markup():
    db = load_db()
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ الخدمات", callback_data="serv"))
    markup.add(types.InlineKeyboardButton("📟 الحساب", callback_data="acc"), types.InlineKeyboardButton("✳️ تجميع", callback_data="coll"))
    markup.add(types.InlineKeyboardButton("♻️ تحويل نقاط", callback_data="trans"), types.InlineKeyboardButton("💳 استخدام كود", callback_data="code"))
    markup.add(types.InlineKeyboardButton("🚩 طلباتي", callback_data="my_ord"), types.InlineKeyboardButton("📩 معلومات الطلب", callback_data="info"))
    markup.add(types.InlineKeyboardButton("📊 الاحصائيات", callback_data="stat"), types.InlineKeyboardButton("💰 شحن نقاط", callback_data="top"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="term"), types.InlineKeyboardButton("⚙️ التحديثات", callback_data="upd"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders']}", callback_data="none"))
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = 0
    save_db(db)
    txt = f"👋 مرحباً بك في بوت الشموخ\n\n👤 نقاطك : {db['users'][uid]}\n🆔 ايديك : {uid}"
    bot.send_message(message.chat.id, txt, reply_markup=get_markup())

@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    if call.data == "acc":
        db = load_db()
        bot.answer_callback_query(call.id, f"نقاطك: {db['users'].get(str(call.message.chat.id), 0)}", show_alert=True)

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
