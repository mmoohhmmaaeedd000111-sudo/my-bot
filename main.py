import telebot
from telebot import types
import requests
import json, os
from threading import Thread
from flask import Flask

# --- الإعدادات ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
API_KEY = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"
POINT_VALUE = 2000 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "FULL SYSTEM ACTIVE 🟢"

# --- قاعدة البيانات ---
def load_db():
    if not os.path.exists('db.json'): return {"users": {}, "codes": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

# --- ترتيب الأقسام ---
MY_CATS = [
    {"n": "📸 إنستقرام", "id": "Instagram"},
    {"n": "🎬 تيك توك", "id": "TikTok"},
    {"n": "💬 واتساب", "id": "WhatsApp"},
    {"n": "🎥 يوتيوب", "id": "YouTube"},
    {"n": "🟡 سناب شات", "id": "Snapchat"},
    {"n": "🎮 بوبجي (PUBG)", "id": "PUBG"},
    {"n": "🎲 لودو (Ludo)", "id": "Ludo"},
    {"n": "🔹 تليجرام", "id": "Telegram"},
    {"n": "👤 فيسبوك", "id": "Facebook"}
]

def main_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, {"points": 0})["points"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="open_services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="collect"))
    markup.add(types.InlineKeyboardButton("🔍 بحث", callback_data="search"), 
               types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code"))
    markup.add(types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="track"), 
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
    save_db(db)
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت الشموخ للرشق", reply_markup=main_markup(uid))

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    uid = str(call.message.chat.id)
    
    if call.data == "open_services":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat in MY_CATS:
            markup.add(types.InlineKeyboardButton(cat["n"], callback_data=f"show_{cat['id']}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
        bot.edit_message_text("📂 اختر المنصة المطلوبة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("show_"):
        cat_id = call.data.split("_")[1]
        bot.answer_callback_query(call.id, "⏳ جاري جلب الخدمات...")
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
        markup = types.InlineKeyboardMarkup()
        for s in res:
            if cat_id.lower() in s['category'].lower() or cat_id.lower() in s['name'].lower():
                price = int(float(s['rate']) * POINT_VALUE)
                name = s['name'].replace("Followers", "متابعين").replace("Likes", "لايكات")
                markup.add(types.InlineKeyboardButton(f"🔹 {name[:25]} | {price}ن", callback_data=f"ord_{s['service']}"))
        markup.add(types.InlineKeyboardButton("🔙 العودة للأقسام", callback_data="open_services"))
        bot.edit_message_text(f"🚀 خدمات {cat_id}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "acc":
        db = load_db()
        pts = db["users"].get(uid, {"points": 0})["points"]
        bot.answer_callback_query(call.id, f"💰 رصيدك الحالي: {pts} نقطة", show_alert=True)

    elif call.data == "topup":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور", url="https://t.me/l550r"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
        bot.edit_message_text("💰 لشحن الرصيد تواصل مع المطور @l550r وارسل صورة التحويل.", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back_home":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=main_markup(uid))

# --- تشغيل ---
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
