import telebot
from telebot import types
import json
import os
import requests
from threading import Thread
from flask import Flask

# --- إعداداتك ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "7154944941" 
API_KEY_KD1S = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "ONLINE"

DB_FILE = 'db.json'
def load_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "orders_count": 6385597}
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f: json.dump(db, f)

def main_markup(uid):
    db = load_db()
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ الخدمات", callback_data="services"))
    markup.add(types.InlineKeyboardButton("📟 الحساب", callback_data="acc"), types.InlineKeyboardButton("✳️ تجميع", callback_data="coll"))
    markup.add(types.InlineKeyboardButton("♻️ تحويل", callback_data="trans"), types.InlineKeyboardButton("💳 كود", callback_data="code"))
    markup.add(types.InlineKeyboardButton("🚩 طلباتي", callback_data="my_ord"), types.InlineKeyboardButton("📩 معلومات", callback_data="info"))
    markup.add(types.InlineKeyboardButton("📊 الاحصائيات", callback_data="stats"), types.InlineKeyboardButton("💰 شحن", callback_data="topup"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms"), types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = 0
    save_db(db)
    text = f"👋 مرحباً بك في بوت الشموخ\n\n👤 نقاطك : {db['users'][uid]}\n🆔 ايديك : {uid}"
    bot.send_message(message.chat.id, text, reply_markup=main_markup(uid))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "acc":
        db = load_db()
        bot.answer_callback_query(call.id, f"رصيدك: {db['users'].get(str(call.message.chat.id), 0)}", show_alert=True)
    elif call.data == "topup":
        bot.send_message(call.message.chat.id, "💰 للشحن أرسل الكود للمطور: @YourUsername")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
