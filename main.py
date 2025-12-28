import telebot
from telebot import types
import json
import os
import requests
from threading import Thread
from flask import Flask

# --- إعداداتك الخاصة ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "7154944941" 
API_KEY_KD1S = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "SYSTEM ONLINE 🟢"

# --- قاعدة بيانات المستخدمين والطلبات ---
def load_db():
    if not os.path.exists('db.json'): return {"users": {}, "orders": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

# --- واجهة الأزرار التي في الصورة ---
def main_markup(uid, points):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # الصف الأول: الخدمات
    btn_service = types.InlineKeyboardButton("🛍️ الخدمات", callback_data="services")
    markup.row(btn_service)
    # الصف الثاني: الحساب وتجميع النقاط
    btn1 = types.InlineKeyboardButton("📟 الحساب", callback_data="account")
    btn2 = types.InlineKeyboardButton("✳️ تجميع", callback_data="collect")
    # الصف الثالث: تحويل واستخدام كود
    btn3 = types.InlineKeyboardButton("♻️ تحويل نقاط", callback_data="transfer")
    btn4 = types.InlineKeyboardButton("💳 استخدام كود", callback_data="redeem")
    # الصف الرابع: طلباتي ومعلومات
    btn5 = types.InlineKeyboardButton("🚩 طلباتي", callback_data="my_orders")
    btn6 = types.InlineKeyboardButton("📩 معلومات الطلب", callback_data="order_info")
    # الصف الخامس: إحصائيات وشحن
    btn7 = types.InlineKeyboardButton("📊 الاحصائيات", callback_data="stats")
    btn8 = types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup")
    # الصف السادس: الشروط والتحديثات
    btn9 = types.InlineKeyboardButton("📜 الشروط", callback_data="terms")
    btn10 = types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
    # زر عدد الطلبات
    db = load_db()
    btn_count = types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders']}", callback_data="none")
    markup.row(btn_count)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = 0
    save_db(db)
    
    welcome_text = (f"مرحباً بك في بوت الشموخ 👋\n\n"
                    f"👥 نقاطك : {db['users'][uid]}\n"
                    f"🆔 ايديك : {uid}")
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_markup(uid, db["users"][uid]))

# --- معالجة الأزرار (أمثلة للتشغيل) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    db = load_db()
    uid = str(call.message.chat.id)

    if call.data == "account":
        bot.answer_callback_query(call.id, f"رصيدك الحالي هو {db['users'][uid]} نقطة.")
    
    elif call.data == "services":
        # هنا تضع قائمة الخدمات المتاحة للرشق
        text = "🚀 **قائمة خدمات الرشق المتاحة:**\n\n1- متابعين انستقرام (1000 نقطة)\n2- لايكات (300 نقطة)"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

    elif call.data == "topup":
        bot.send_message(call.message.chat.id, "💰 لشحن النقاط، يرجى إرسال كارت آسيا سيل إلى المطور : @YourUsername")

# --- تشغيل السيرفر ---
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
