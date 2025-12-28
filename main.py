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

# --- قاعدة بيانات بسيطة ---
DB_FILE = 'db.json'
def load_db():
    if not os.path.exists(DB_FILE): 
        return {"users": {}, "orders_count": 6385597}
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f: json.dump(db, f)

# --- واجهة الأزرار (نفس الصورة تماماً) ---
def main_markup(uid, points):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # الزر العلوي الكبير
    btn_services = types.InlineKeyboardButton("🛍️ الخدمات", callback_data="services")
    markup.row(btn_services)
    
    # الصف الأول
    btn_acc = types.InlineKeyboardButton("📟 الحساب", callback_data="account")
    btn_coll = types.InlineKeyboardButton("✳️ تجميع نقاط", callback_data="collect")
    markup.add(btn_acc, btn_coll)
    
    # الصف الثاني
    btn_trans = types.InlineKeyboardButton("♻️ تحويل نقاط", callback_data="transfer")
    btn_redeem = types.InlineKeyboardButton("💳 استخدام كود", callback_data="redeem_code")
    markup.add(btn_trans, btn_redeem)
    
    # الصف الثالث
    btn_my_orders = types.InlineKeyboardButton("🚩 طلباتي", callback_data="my_orders")
    btn_ord_info = types.InlineKeyboardButton("📩 معلومات الطلب", callback_data="order_info")
    markup.add(btn_my_orders, btn_ord_info)
    
    # الصف الرابع
    btn_stats = types.InlineKeyboardButton("📊 الاحصائيات", callback_data="stats")
    btn_topup = types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup")
    markup.add(btn_stats, btn_topup)
    
    # الصف الخامس
    btn_terms = types.InlineKeyboardButton("📜 الشروط", callback_data="terms")
    btn_updates = types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates")
    markup.add(btn_terms, btn_updates)
    
    # زر العداد السفلي
    db = load_db()
    btn_counter = types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none")
    markup.row(btn_counter)
    
    return markup

# --- الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = 0
    save_db(db)
    
    text = (f"👋 مرحباً بك في بوت الشموخ\n\n"
            f"👤 نقاطك : {db['users'][uid]}\n"
            f"🆔 ايديك : {uid}")
    
    bot.send_message(message.chat.id, text, reply_markup=main_
    
