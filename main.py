import telebot
from telebot import types
import requests
import json, os
from threading import Thread
from flask import Flask

# --- الإعدادات ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998" 
API_KEY = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"
POINT_VALUE = 2000 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "ARABIC INTERFACE ACTIVE 🟢"

# --- قائمة المنصات المفضلة (لتظهر في البداية) ---
PRIORITY_CATEGORIES = ["Instagram", "TikTok", "Telegram", "Facebook", "YouTube"]

def load_db():
    if not os.path.exists('db.json'): 
        return {"users": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def get_main_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, {"points": 0}).get("points", 0)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="collect"))
    markup.add(types.InlineKeyboardButton("🔍 بحث", callback_data="search_start"), 
               types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code"))
    markup.add(types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="info"), 
               types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms"), 
               types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = {"points": 0}
    with open('db.json', 'w') as f: json.dump(db, f)
    bot.send_message(message.chat.id, f"👋 أهلاً بك في بوت الشموخ\n👤 نقاطك: {db['users'][uid]['points']}", reply_markup=get_main_markup(uid))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = str(call.message.chat.id)
    
    if call.data == "services":
        try:
            res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
            all_cats = list(set([s['category'] for s in res]))
            
            # ترتيب الأقسام: وضع المنصات المفضلة في البداية
            priority = []
            others = []
            for cat in all_cats:
                if any(p in cat for p in PRIORITY_CATEGORIES):
                    priority.append(cat)
                else:
                    others.append(cat)
            
            sorted_cats = sorted(priority) + sorted(others)
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            for c in sorted_cats[:15]: # عرض أهم 15 قسم
                markup.add(types.InlineKeyboardButton(f"⭐ {c}", callback_data=f"cat_{c[:20]}"))
            
            markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back"))
            bot.edit_message_text("📂 اختر المنصة المطلوبة (الأهم في البداية):", call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.answer_callback_query(call.id, "❌ خطأ في الاتصال بالموقع")

    elif call.data.startswith("cat_"):
        cat_name = call.data.replace("cat_", "")
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
        markup = types.InlineKeyboardMarkup()
        # عرض الخدمات بأسماء عربية (تحتاج لترجمة يدوية إذا كان الموقع لا يدعم العربية)
        for s in [x for x in res if x['category'].startswith(cat_name)][:15]:
            price = int(float(s['rate']) * POINT_VALUE)
            markup.add(types.InlineKeyboardButton(f"🔹 {s['name
